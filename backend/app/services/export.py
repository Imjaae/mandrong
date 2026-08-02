from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Asset, AssetType, ExportFormat, ExportJob, GenerationVersion, JobStatus, Project, ProjectStatus
from app.services.files import full_path, storage_root


def run_export_job(export_job_id: uuid.UUID) -> None:
    from app.db.session import SessionLocal

    db: Session = SessionLocal()
    try:
        job = db.get(ExportJob, export_job_id)
        if job is None:
            return
        project = db.get(Project, job.project_id)
        if project is not None:
            project.status = ProjectStatus.exporting
        job.status = JobStatus.running
        db.commit()

        version = db.execute(select(GenerationVersion).where(GenerationVersion.id == job.version_id)).scalar_one()
        source = db.get(Asset, version.image_asset_id)
        if source is None:
            raise RuntimeError("원본 이미지 파일을 찾지 못했어요.")

        out_dir = storage_root() / "exports" / str(job.project_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = "jpg" if job.format == ExportFormat.jpeg else job.format.value
        relative = Path("exports") / str(job.project_id) / f"{job.id}.{suffix}"
        out_path = storage_root() / relative

        with Image.open(full_path(source.storage_path)) as image:
            if job.format == ExportFormat.png:
                image.save(out_path, "PNG")
                mime = "image/png"
            elif job.format == ExportFormat.jpeg:
                image.convert("RGB").save(out_path, "JPEG", quality=90)
                mime = "image/jpeg"
            elif job.format == ExportFormat.pdf:
                image.convert("RGB").save(out_path, "PDF")
                mime = "application/pdf"
            else:
                raise RuntimeError("지원하지 않는 형식입니다.")

        asset = Asset(
            project_id=job.project_id,
            version_id=job.version_id,
            type=AssetType.export_file,
            storage_path=str(relative),
            public_path=f"/api/v1/exports/{job.id}/download",
            mime_type=mime,
            size_bytes=out_path.stat().st_size,
        )
        db.add(asset)
        db.flush()
        job.asset_id = asset.id
        job.status = JobStatus.succeeded
        job.finished_at = datetime.now(timezone.utc)
        if project is not None:
            project.status = ProjectStatus.ready
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.get(ExportJob, export_job_id)
        if job is not None:
            job.status = JobStatus.failed
            job.error_code = "EXPORT_FAILED"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
