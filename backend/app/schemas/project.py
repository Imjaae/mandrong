from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


def validate_image_size(value: int) -> int:
    if value < 256 or value > 4096:
        raise ValueError("이미지 크기는 256px 이상 4096px 이하로 입력해주세요.")
    if value % 16 != 0:
        raise ValueError("이미지 크기는 16px 단위여야 합니다.")
    return value


class CreativeBriefIn(BaseModel):
    purpose: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    primary_copy: str = Field(min_length=1, max_length=80)
    secondary_copy: str | None = None
    price_copy: str | None = Field(default=None, max_length=120)
    notice_copy: str | None = Field(default=None, max_length=240)
    store_name: str | None = Field(default=None, max_length=120)
    menu_name: str | None = Field(default=None, max_length=120)
    price: str | None = Field(default=None, max_length=80)
    store_location: str | None = Field(default=None, max_length=160)
    contact: str | None = Field(default=None, max_length=120)
    mood_keywords: list[str] = Field(default_factory=list)
    mood_text: str | None = None

    @field_validator("width", "height")
    @classmethod
    def image_size_must_match_model_step(cls, value: int) -> int:
        return validate_image_size(value)


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    brief: CreativeBriefIn


class ProjectUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ProjectOut(BaseModel):
    id: UUID
    title: str
    status: str
    current_version_id: UUID | None
    current_image_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    brief: CreativeBriefIn


class AssetOut(BaseModel):
    id: UUID
    type: str
    original_filename: str | None
    mime_type: str
    size_bytes: int
    width: int | None
    height: int | None
    url: str


class GenerationRequest(BaseModel):
    menu_asset_ids: list[UUID] = Field(default_factory=list)
    logo_asset_ids: list[UUID] = Field(default_factory=list)
    reference_asset_ids: list[UUID] = Field(default_factory=list)


class JobOut(BaseModel):
    job_id: UUID
    status: str


class GenerationJobOut(BaseModel):
    id: UUID
    project_id: UUID
    type: str
    status: str
    version_id: UUID | None = None
    error: dict | None = None


class AnnotationIn(BaseModel):
    note: str = Field(min_length=1, max_length=300)
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float | None = Field(default=None, ge=0, le=1)
    height: float | None = Field(default=None, ge=0, le=1)
    color: str = "yellow"


class AnnotationCreate(BaseModel):
    annotations: list[AnnotationIn] = Field(min_length=1)


class AnnotationCreateOut(BaseModel):
    annotation_ids: list[UUID]


class EditRequest(BaseModel):
    annotation_ids: list[UUID] = Field(default_factory=list)
    edit_text: str | None = Field(default=None, max_length=1000)
    additional_asset_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def must_have_edit_input(self) -> "EditRequest":
        if not self.annotation_ids and not (self.edit_text and self.edit_text.strip()) and not self.additional_asset_ids:
            raise ValueError("수정 메모, 수정 요청, 추가 이미지 중 하나는 필요합니다.")
        return self


class VersionOut(BaseModel):
    id: UUID
    project_id: UUID
    image_asset_id: UUID
    image_url: str
    version_number: int
    width: int
    height: int
    summary: str | None
    is_applied: bool
    created_at: datetime


class ApplyVersionOut(BaseModel):
    project_id: UUID
    current_version_id: UUID


class ReframeTarget(BaseModel):
    purpose: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)

    @field_validator("width", "height")
    @classmethod
    def image_size_must_match_model_step(cls, value: int) -> int:
        return validate_image_size(value)


class ReframeKeep(BaseModel):
    keep_copy: bool = Field(default=True, alias="copy")
    menu_photo: bool = True
    price: bool = True
    mood: bool = True

    model_config = {"populate_by_name": True}


class ReframeRequest(BaseModel):
    target: ReframeTarget
    keep: ReframeKeep = Field(default_factory=ReframeKeep)


class ExportRequest(BaseModel):
    format: str
    quality: int = Field(default=90, ge=1, le=100)


class ExportJobOut(BaseModel):
    export_job_id: UUID
    status: str


class ExportJobDetailOut(BaseModel):
    id: UUID
    status: str
    asset_id: UUID | None
    download_url: str | None
    error: dict | None = None
