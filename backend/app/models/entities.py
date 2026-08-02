from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    generating = "generating"
    generated = "generated"
    editing = "editing"
    ready = "ready"
    exporting = "exporting"
    failed = "failed"


class AssetType(str, enum.Enum):
    menu_photo = "menu_photo"
    reference_image = "reference_image"
    generated_image = "generated_image"
    edited_image = "edited_image"
    export_file = "export_file"


class GenerationJobType(str, enum.Enum):
    initial = "initial"
    edit = "edit"
    reframe = "reframe"


class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class ExportFormat(str, enum.Enum):
    png = "png"
    jpeg = "jpeg"
    pdf = "pdf"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(120))
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.draft)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    brief: Mapped["CreativeBrief"] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")


class CreativeBrief(Base):
    __tablename__ = "creative_briefs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), unique=True)
    purpose: Mapped[str] = mapped_column(String(40))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    primary_copy: Mapped[str] = mapped_column(String(80))
    secondary_copy: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_copy: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notice_copy: Mapped[str | None] = mapped_column(String(240), nullable=True)
    store_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    menu_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    price: Mapped[str | None] = mapped_column(String(80), nullable=True)
    store_location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mood_keywords: Mapped[list[str]] = mapped_column(JSON, default=list)
    mood_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    project: Mapped[Project] = relationship(back_populates="brief")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    type: Mapped[AssetType] = mapped_column(Enum(AssetType))
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_path: Mapped[str] = mapped_column(Text)
    public_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    source_version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    type: Mapped[GenerationJobType] = mapped_column(Enum(GenerationJobType))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued)
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    prompt_text: Mapped[str] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class GenerationVersion(Base):
    __tablename__ = "generation_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generation_jobs.id"))
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    image_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str | None] = mapped_column(String(240), nullable=True)
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generation_versions.id"))
    note: Mapped[str] = mapped_column(String(300))
    x: Mapped[float] = mapped_column(Numeric(6, 5))
    y: Mapped[float] = mapped_column(Numeric(6, 5))
    width: Mapped[float | None] = mapped_column(Numeric(6, 5), nullable=True)
    height: Mapped[float | None] = mapped_column(Numeric(6, 5), nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="yellow")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generation_versions.id"))
    format: Mapped[ExportFormat] = mapped_column(Enum(ExportFormat))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
