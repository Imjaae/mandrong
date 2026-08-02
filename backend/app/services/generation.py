from __future__ import annotations

import base64
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageOps
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Asset, AssetType, GenerationJob, GenerationJobType, GenerationVersion, JobStatus, Project, ProjectStatus
from app.services.files import ensure_storage_dirs, full_path, storage_root


def create_placeholder_image(path: Path, width: int, height: int, title: str) -> None:
    image = Image.new("RGB", (width, height), "#0E100F")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((32, 32, width - 32, height - 32), outline="#74D4B3", width=6)
    draw.text((64, 64), "MANDRONG", fill="#74D4B3", font=font)
    draw.text((64, 100), title[:80], fill="#F5F1EA", font=font)
    draw.text((64, height - 96), "OPENAI_API_KEY가 없어서 로컬 미리보기 이미지를 생성했습니다.", fill="#A9A399", font=font)
    image.save(path, "PNG")


def _next_version_number(db: Session, project_id: uuid.UUID) -> int:
    current = db.scalar(select(func.max(GenerationVersion.version_number)).where(GenerationVersion.project_id == project_id))
    return int(current or 0) + 1


def _payload_asset_ids(job: GenerationJob) -> list[uuid.UUID]:
    payload = job.request_payload or {}
    raw_ids = [
        *(payload.get("menu_asset_ids") or []),
        *(payload.get("reference_asset_ids") or []),
        *(payload.get("additional_asset_ids") or []),
    ]
    asset_ids: list[uuid.UUID] = []
    for raw_id in raw_ids:
        try:
            asset_ids.append(uuid.UUID(str(raw_id)))
        except ValueError:
            continue
    return asset_ids


def _input_image_assets(db: Session, job: GenerationJob) -> list[Asset]:
    assets: list[Asset] = []
    if job.source_version_id:
        source = db.get(GenerationVersion, job.source_version_id)
        if source:
            source_asset = db.get(Asset, source.image_asset_id)
            if source_asset:
                assets.append(source_asset)

    for asset_id in _payload_asset_ids(job):
        asset = db.get(Asset, asset_id)
        if asset and asset.project_id == job.project_id:
            assets.append(asset)

    unique: dict[uuid.UUID, Asset] = {}
    for asset in assets:
        unique[asset.id] = asset
    return list(unique.values())


def _prepare_openai_input_image(source_path: Path, temp_dir: Path, index: int) -> Path:
    output_path = temp_dir / f"input-{index}.png"
    with Image.open(source_path) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA")
        if max(image.size) > 2048:
            image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        image.save(output_path, format="PNG", optimize=True)
    return output_path


def _asset_source_path(asset: Asset, temp_dir: Path, index: int) -> Path | None:
    image_path = full_path(asset.storage_path)
    if image_path.exists():
        return image_path
    if asset.content:
        restored_path = temp_dir / f"source-{index}"
        restored_path.write_bytes(asset.content)
        return restored_path
    return None


def run_generation_job(job_id: uuid.UUID) -> None:
    ensure_storage_dirs()
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if job is None:
            return
        project = db.get(Project, job.project_id)
        if project is None:
            return

        job.status = JobStatus.running
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        brief = project.brief
        version_id = uuid.uuid4()
        relative = Path("generated") / str(project.id) / f"{version_id}.png"
        path = storage_root() / relative
        path.parent.mkdir(parents=True, exist_ok=True)

        settings = get_settings()
        if settings.openai_api_key:
            client = OpenAI(api_key=settings.openai_api_key)
            input_assets = _input_image_assets(db, job)
            image_files = []
            try:
                with tempfile.TemporaryDirectory() as temp_name:
                    temp_dir = Path(temp_name)
                    for index, asset in enumerate(input_assets, start=1):
                        image_path = _asset_source_path(asset, temp_dir, index)
                        if image_path:
                            prepared_path = _prepare_openai_input_image(image_path, temp_dir, index)
                            image_files.append(prepared_path.open("rb"))

                    if image_files:
                        result = client.images.edit(
                            model="gpt-image-2",
                            image=image_files,
                            prompt=job.prompt_text,
                            size=f"{brief.width}x{brief.height}",
                        )
                    else:
                        result = client.images.generate(
                            model="gpt-image-2",
                            prompt=job.prompt_text,
                            size=f"{brief.width}x{brief.height}",
                        )
            finally:
                for image_file in image_files:
                    image_file.close()
            image_b64 = result.data[0].b64_json
            if not image_b64:
                raise RuntimeError("OpenAI 응답에 이미지가 없습니다.")
            path.write_bytes(base64.b64decode(image_b64))
        else:
            create_placeholder_image(path, brief.width, brief.height, brief.primary_copy)

        with Image.open(path) as image:
            width, height = image.size
        content = path.read_bytes()

        asset_type = AssetType.generated_image if job.type != GenerationJobType.edit else AssetType.edited_image
        asset = Asset(
            project_id=project.id,
            version_id=version_id,
            type=asset_type,
            storage_path=str(relative),
            public_path=f"/api/v1/assets/{version_id}/file",
            mime_type="image/png",
            size_bytes=len(content),
            width=width,
            height=height,
            content=content,
        )
        db.add(asset)
        db.flush()

        version = GenerationVersion(
            id=version_id,
            project_id=project.id,
            job_id=job.id,
            parent_version_id=job.source_version_id,
            image_asset_id=asset.id,
            version_number=_next_version_number(db, project.id),
            width=width,
            height=height,
            summary="최초 생성" if job.type == GenerationJobType.initial else "메모 수정",
            is_applied=True,
        )
        db.query(GenerationVersion).filter(GenerationVersion.project_id == project.id).update({"is_applied": False})
        db.add(version)
        db.flush()
        asset.version_id = version.id
        project.current_version_id = version.id
        project.status = ProjectStatus.ready
        job.status = JobStatus.succeeded
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.get(GenerationJob, job_id)
        if job is not None:
            job.status = JobStatus.failed
            job.error_code = "GENERATION_FAILED"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            project = db.get(Project, job.project_id)
            if project is not None:
                project.status = ProjectStatus.failed
            db.commit()
    finally:
        db.close()
