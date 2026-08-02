from __future__ import annotations

import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.errors import api_error
from app.db.session import get_db
from app.models import (
    Annotation,
    Asset,
    AssetType,
    CreativeBrief,
    ExportFormat,
    ExportJob,
    GenerationJob,
    GenerationJobType,
    GenerationVersion,
    JobStatus,
    Project,
    ProjectStatus,
)
from app.schemas.project import (
    AnnotationCreate,
    AnnotationCreateOut,
    ApplyVersionOut,
    AssetOut,
    CreativeBriefIn,
    EditRequest,
    ExportJobDetailOut,
    ExportJobOut,
    ExportRequest,
    GenerationJobOut,
    GenerationRequest,
    JobOut,
    ProjectCreate,
    ProjectDetail,
    ProjectOut,
    ProjectUpdate,
    ReframeRequest,
    VersionOut,
)
from app.services.export import run_export_job
from app.services.files import full_path, save_upload
from app.services.generation import run_generation_job
from app.services.prompts import build_edit_prompt, build_initial_prompt

router = APIRouter(prefix="/api/v1")


def _project_or_404(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise api_error(404, "PROJECT_NOT_FOUND", "작업을 찾지 못했어요.")
    return project


def _version_or_404(db: Session, version_id: uuid.UUID) -> GenerationVersion:
    version = db.get(GenerationVersion, version_id)
    if version is None:
        raise api_error(404, "VERSION_NOT_FOUND", "버전을 찾지 못했어요.")
    return version


def _version_out(version: GenerationVersion) -> VersionOut:
    return VersionOut(
        id=version.id,
        project_id=version.project_id,
        image_asset_id=version.image_asset_id,
        image_url=f"/api/v1/assets/{version.image_asset_id}/file",
        version_number=version.version_number,
        width=version.width,
        height=version.height,
        summary=version.summary,
        is_applied=version.is_applied,
        created_at=version.created_at,
    )


def _project_out(db: Session, project: Project) -> ProjectOut:
    image_url = None
    if project.current_version_id:
        version = db.get(GenerationVersion, project.current_version_id)
        if version:
            image_url = f"/api/v1/assets/{version.image_asset_id}/file"
    return ProjectOut(
        id=project.id,
        title=project.title,
        status=project.status.value,
        current_version_id=project.current_version_id,
        current_image_url=image_url,
        created_at=project.created_at,
    )


def _validate_project_assets(db: Session, project_id: uuid.UUID, asset_ids: list[uuid.UUID]) -> list[Asset]:
    if not asset_ids:
        return []
    assets = list(db.scalars(select(Asset).where(Asset.id.in_(asset_ids))))
    if len(assets) != len(asset_ids) or any(asset.project_id != project_id for asset in assets):
        raise api_error(422, "VALIDATION_ERROR", "첨부 이미지를 확인해주세요.")
    return assets


def _delete_project_files(db: Session, project_id: uuid.UUID) -> None:
    assets = db.scalars(select(Asset).where(Asset.project_id == project_id))
    for asset in assets:
        path = full_path(asset.storage_path)
        if path.exists() and path.is_file():
            path.unlink(missing_ok=True)


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectOut:
    project = Project(title=payload.title, status=ProjectStatus.draft)
    db.add(project)
    db.flush()
    db.add(CreativeBrief(project_id=project.id, **payload.brief.model_dump()))
    db.commit()
    db.refresh(project)
    return _project_out(db, project)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(limit: int = 20, db: Session = Depends(get_db)) -> list[ProjectOut]:
    limit = min(max(limit, 1), 50)
    projects = db.scalars(select(Project).order_by(desc(Project.created_at)).limit(limit))
    return [_project_out(db, project) for project in projects]


@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)) -> ProjectDetail:
    project = _project_or_404(db, project_id)
    return ProjectDetail(
        id=project.id,
        title=project.title,
        status=project.status.value,
        current_version_id=project.current_version_id,
        current_image_url=_project_out(db, project).current_image_url,
        created_at=project.created_at,
        brief=CreativeBriefIn.model_validate(project.brief, from_attributes=True),
    )


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: uuid.UUID, payload: ProjectUpdate, db: Session = Depends(get_db)) -> ProjectOut:
    project = _project_or_404(db, project_id)
    project.title = payload.title
    db.commit()
    db.refresh(project)
    return _project_out(db, project)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    project = _project_or_404(db, project_id)
    _delete_project_files(db, project.id)
    db.query(Annotation).filter(Annotation.project_id == project.id).delete(synchronize_session=False)
    db.query(ExportJob).filter(ExportJob.project_id == project.id).delete(synchronize_session=False)
    db.query(GenerationVersion).filter(GenerationVersion.project_id == project.id).delete(synchronize_session=False)
    db.query(GenerationJob).filter(GenerationJob.project_id == project.id).delete(synchronize_session=False)
    db.query(Asset).filter(Asset.project_id == project.id).delete(synchronize_session=False)
    db.query(CreativeBrief).filter(CreativeBrief.project_id == project.id).delete(synchronize_session=False)
    db.delete(project)
    db.commit()
    return Response(status_code=204)


@router.patch("/projects/{project_id}/brief", response_model=ProjectDetail)
def update_brief(project_id: uuid.UUID, payload: CreativeBriefIn, db: Session = Depends(get_db)) -> ProjectDetail:
    project = _project_or_404(db, project_id)
    for key, value in payload.model_dump().items():
        setattr(project.brief, key, value)
    db.commit()
    return get_project(project_id, db)


@router.post("/projects/{project_id}/assets", response_model=AssetOut, status_code=201)
async def upload_asset(
    project_id: uuid.UUID,
    type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> AssetOut:
    _project_or_404(db, project_id)
    if type not in {AssetType.menu_photo.value, AssetType.reference_image.value}:
        raise api_error(422, "VALIDATION_ERROR", "자산 유형을 확인해주세요.")
    try:
        info = await save_upload(project_id, file, type)
    except ValueError as exc:
        code = str(exc)
        if code == "UPLOAD_TOO_LARGE":
            raise api_error(413, code, "파일이 너무 커요.")
        raise api_error(415, "UNSUPPORTED_FILE_TYPE", "JPG, PNG, WEBP 파일만 사용할 수 있어요.")

    asset = Asset(project_id=project_id, type=AssetType(type), **info)
    db.add(asset)
    db.flush()
    asset.public_path = f"/api/v1/assets/{asset.id}/file"
    db.commit()
    return AssetOut(
        id=asset.id,
        type=asset.type.value,
        original_filename=asset.original_filename,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        width=asset.width,
        height=asset.height,
        url=f"/api/v1/assets/{asset.id}/file",
    )


@router.get("/assets/{asset_id}/file")
def get_asset_file(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse | Response:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise api_error(404, "ASSET_NOT_FOUND", "파일을 찾지 못했어요.")
    path = full_path(asset.storage_path)
    if path.exists():
        return FileResponse(path, media_type=asset.mime_type, filename=asset.original_filename)
    if asset.content:
        return Response(
            content=asset.content,
            media_type=asset.mime_type,
        )
    raise api_error(404, "ASSET_NOT_FOUND", "파일을 찾지 못했어요.")


@router.post("/projects/{project_id}/generations", response_model=JobOut, status_code=202)
def create_generation(project_id: uuid.UUID, payload: GenerationRequest, background: BackgroundTasks, db: Session = Depends(get_db)) -> JobOut:
    project = _project_or_404(db, project_id)
    _validate_project_assets(db, project.id, [*payload.menu_asset_ids, *payload.logo_asset_ids, *payload.reference_asset_ids])
    prompt = build_initial_prompt(
        project.brief,
        menu_image_count=len(payload.menu_asset_ids),
        has_logo_images=bool(payload.logo_asset_ids),
        reference_image_count=len(payload.reference_asset_ids),
    )
    job = GenerationJob(
        project_id=project.id,
        type=GenerationJobType.initial,
        status=JobStatus.queued,
        prompt_text=prompt,
        request_payload={
            "model": "gpt-image-2",
            "purpose": project.brief.purpose,
            "width": project.brief.width,
            "height": project.brief.height,
            "menu_asset_ids": [str(item) for item in payload.menu_asset_ids],
            "logo_asset_ids": [str(item) for item in payload.logo_asset_ids],
            "reference_asset_ids": [str(item) for item in payload.reference_asset_ids],
        },
    )
    project.status = ProjectStatus.generating
    db.add(job)
    db.commit()
    background.add_task(run_generation_job, job.id)
    return JobOut(job_id=job.id, status=job.status.value)


@router.get("/generation-jobs/{job_id}", response_model=GenerationJobOut)
def get_generation_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> GenerationJobOut:
    job = db.get(GenerationJob, job_id)
    if job is None:
        raise api_error(404, "GENERATION_JOB_NOT_FOUND", "생성 작업을 찾지 못했어요.")
    version = db.scalar(select(GenerationVersion).where(GenerationVersion.job_id == job.id))
    return GenerationJobOut(
        id=job.id,
        project_id=job.project_id,
        type=job.type.value,
        status=job.status.value,
        version_id=version.id if version else None,
        error={"code": job.error_code, "message": job.error_message} if job.error_code else None,
    )


@router.post("/versions/{version_id}/annotations", response_model=AnnotationCreateOut, status_code=201)
def create_annotations(version_id: uuid.UUID, payload: AnnotationCreate, db: Session = Depends(get_db)) -> AnnotationCreateOut:
    version = _version_or_404(db, version_id)
    rows = [
        Annotation(project_id=version.project_id, version_id=version.id, **item.model_dump())
        for item in payload.annotations
    ]
    db.add_all(rows)
    db.commit()
    return AnnotationCreateOut(annotation_ids=[row.id for row in rows])


@router.post("/versions/{version_id}/edits", response_model=JobOut, status_code=202)
def create_edit(version_id: uuid.UUID, payload: EditRequest, background: BackgroundTasks, db: Session = Depends(get_db)) -> JobOut:
    version = _version_or_404(db, version_id)
    project = _project_or_404(db, version.project_id)
    _validate_project_assets(db, project.id, payload.additional_asset_ids)
    annotations = []
    if payload.annotation_ids:
        annotations = list(db.scalars(select(Annotation).where(Annotation.id.in_(payload.annotation_ids))))
        if len(annotations) != len(payload.annotation_ids) or any(item.version_id != version.id for item in annotations):
            raise api_error(422, "VALIDATION_ERROR", "수정 메모를 확인해주세요.")
    lines = [
        f"- 위치: x {item.x}, y {item.y}, width {item.width}, height {item.height}; 요청: {item.note}"
        for item in annotations
    ]
    prompt = build_edit_prompt(
        build_initial_prompt(project.brief, menu_image_count=1, has_logo_images=True),
        lines,
        payload.edit_text,
    )
    job = GenerationJob(
        project_id=project.id,
        source_version_id=version.id,
        type=GenerationJobType.edit,
        status=JobStatus.queued,
        prompt_text=prompt,
        request_payload={
            "model": "gpt-image-2",
            "annotation_ids": [str(item) for item in payload.annotation_ids],
            "additional_asset_ids": [str(item) for item in payload.additional_asset_ids],
            "edit_text": payload.edit_text,
        },
    )
    project.status = ProjectStatus.editing
    db.add(job)
    db.commit()
    background.add_task(run_generation_job, job.id)
    return JobOut(job_id=job.id, status=job.status.value)


@router.get("/projects/{project_id}/versions", response_model=list[VersionOut])
def list_versions(project_id: uuid.UUID, db: Session = Depends(get_db)) -> list[VersionOut]:
    _project_or_404(db, project_id)
    versions = db.scalars(select(GenerationVersion).where(GenerationVersion.project_id == project_id).order_by(desc(GenerationVersion.created_at)))
    return [_version_out(version) for version in versions]


@router.get("/versions/{version_id}", response_model=VersionOut)
def get_version(version_id: uuid.UUID, db: Session = Depends(get_db)) -> VersionOut:
    return _version_out(_version_or_404(db, version_id))


@router.post("/versions/{version_id}/apply", response_model=ApplyVersionOut)
def apply_version(version_id: uuid.UUID, db: Session = Depends(get_db)) -> ApplyVersionOut:
    version = _version_or_404(db, version_id)
    db.query(GenerationVersion).filter(GenerationVersion.project_id == version.project_id).update({"is_applied": False})
    version.is_applied = True
    project = _project_or_404(db, version.project_id)
    project.current_version_id = version.id
    project.status = ProjectStatus.ready
    db.commit()
    return ApplyVersionOut(project_id=project.id, current_version_id=version.id)


@router.post("/versions/{version_id}/reframes", response_model=JobOut, status_code=202)
def create_reframe(version_id: uuid.UUID, payload: ReframeRequest, background: BackgroundTasks, db: Session = Depends(get_db)) -> JobOut:
    version = _version_or_404(db, version_id)
    project = _project_or_404(db, version.project_id)
    project.brief.purpose = payload.target.purpose
    project.brief.width = payload.target.width
    project.brief.height = payload.target.height
    prompt = build_initial_prompt(project.brief) + "\n현재 이미지를 새 비율에 맞게 재구성한다. 단순 크롭하지 않는다."
    job = GenerationJob(
        project_id=project.id,
        source_version_id=version.id,
        type=GenerationJobType.reframe,
        status=JobStatus.queued,
        prompt_text=prompt,
        request_payload={"model": "gpt-image-2", "target": payload.target.model_dump(), "keep": payload.keep.model_dump(by_alias=True)},
    )
    project.status = ProjectStatus.generating
    db.add(job)
    db.commit()
    background.add_task(run_generation_job, job.id)
    return JobOut(job_id=job.id, status=job.status.value)


@router.post("/versions/{version_id}/exports", response_model=ExportJobOut, status_code=202)
def create_export(version_id: uuid.UUID, payload: ExportRequest, background: BackgroundTasks, db: Session = Depends(get_db)) -> ExportJobOut:
    version = _version_or_404(db, version_id)
    try:
        fmt = ExportFormat(payload.format)
    except ValueError:
        raise api_error(422, "VALIDATION_ERROR", "다운로드 형식을 확인해주세요.")
    job = ExportJob(project_id=version.project_id, version_id=version.id, format=fmt, status=JobStatus.queued)
    db.add(job)
    db.commit()
    background.add_task(run_export_job, job.id)
    return ExportJobOut(export_job_id=job.id, status=job.status.value)


@router.get("/export-jobs/{export_job_id}", response_model=ExportJobDetailOut)
def get_export_job(export_job_id: uuid.UUID, db: Session = Depends(get_db)) -> ExportJobDetailOut:
    job = db.get(ExportJob, export_job_id)
    if job is None:
        raise api_error(404, "EXPORT_JOB_NOT_FOUND", "내보내기 작업을 찾지 못했어요.")
    return ExportJobDetailOut(
        id=job.id,
        status=job.status.value,
        asset_id=job.asset_id,
        download_url=f"/api/v1/exports/{job.asset_id}/download" if job.asset_id else None,
        error={"code": job.error_code, "message": job.error_message} if job.error_code else None,
    )


@router.get("/exports/{asset_id}/download")
def download_export(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse | Response:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise api_error(404, "ASSET_NOT_FOUND", "파일을 찾지 못했어요.")
    path = full_path(asset.storage_path)
    filename = asset.original_filename or f"mandrong-{asset.id}"
    if path.exists():
        return FileResponse(path, media_type=asset.mime_type, filename=filename)
    if asset.content:
        return Response(
            content=asset.content,
            media_type=asset.mime_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    raise api_error(404, "ASSET_NOT_FOUND", "파일을 찾지 못했어요.")
