"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


project_status = postgresql.ENUM("draft", "generating", "generated", "editing", "ready", "exporting", "failed", name="projectstatus", create_type=False)
asset_type = postgresql.ENUM("menu_photo", "reference_image", "generated_image", "edited_image", "export_file", name="assettype", create_type=False)
generation_job_type = postgresql.ENUM("initial", "edit", "reframe", name="generationjobtype", create_type=False)
job_status = postgresql.ENUM("queued", "running", "succeeded", "failed", "cancelled", name="jobstatus", create_type=False)
export_format = postgresql.ENUM("png", "jpeg", "pdf", name="exportformat", create_type=False)


def upgrade() -> None:
    project_status.create(op.get_bind(), checkfirst=True)
    asset_type.create(op.get_bind(), checkfirst=True)
    generation_job_type.create(op.get_bind(), checkfirst=True)
    job_status.create(op.get_bind(), checkfirst=True)
    export_format.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("status", project_status, nullable=False),
        sa.Column("current_version_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_projects_created_at", "projects", ["created_at"])
    op.create_index("idx_projects_status", "projects", ["status"])

    op.create_table(
        "creative_briefs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=False, unique=True),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("primary_copy", sa.String(length=80), nullable=False),
        sa.Column("secondary_copy", sa.Text(), nullable=True),
        sa.Column("price_copy", sa.String(length=120), nullable=True),
        sa.Column("notice_copy", sa.String(length=240), nullable=True),
        sa.Column("store_name", sa.String(length=120), nullable=True),
        sa.Column("menu_name", sa.String(length=120), nullable=True),
        sa.Column("price", sa.String(length=80), nullable=True),
        sa.Column("store_location", sa.String(length=160), nullable=True),
        sa.Column("contact", sa.String(length=120), nullable=True),
        sa.Column("mood_keywords", postgresql.JSONB(), nullable=False),
        sa.Column("mood_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("version_id", sa.UUID(), nullable=True),
        sa.Column("type", asset_type, nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("public_path", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_assets_project_id", "assets", ["project_id"])
    op.create_index("idx_assets_version_id", "assets", ["version_id"])
    op.create_index("idx_assets_type", "assets", ["type"])

    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("source_version_id", sa.UUID(), nullable=True),
        sa.Column("type", generation_job_type, nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("request_payload", postgresql.JSONB(), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_generation_jobs_project_id", "generation_jobs", ["project_id"])
    op.create_index("idx_generation_jobs_status", "generation_jobs", ["status"])

    op.create_table(
        "generation_versions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("job_id", sa.UUID(), sa.ForeignKey("generation_jobs.id"), nullable=False),
        sa.Column("parent_version_id", sa.UUID(), nullable=True),
        sa.Column("image_asset_id", sa.UUID(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("summary", sa.String(length=240), nullable=True),
        sa.Column("is_applied", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "version_number", name="uq_versions_project_number"),
    )

    op.create_table(
        "annotations",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("version_id", sa.UUID(), sa.ForeignKey("generation_versions.id"), nullable=False),
        sa.Column("note", sa.String(length=300), nullable=False),
        sa.Column("x", sa.Numeric(6, 5), nullable=False),
        sa.Column("y", sa.Numeric(6, 5), nullable=False),
        sa.Column("width", sa.Numeric(6, 5), nullable=True),
        sa.Column("height", sa.Numeric(6, 5), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "export_jobs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("version_id", sa.UUID(), sa.ForeignKey("generation_versions.id"), nullable=False),
        sa.Column("format", export_format, nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("asset_id", sa.UUID(), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("export_jobs")
    op.drop_table("annotations")
    op.drop_table("generation_versions")
    op.drop_index("idx_generation_jobs_status", table_name="generation_jobs")
    op.drop_index("idx_generation_jobs_project_id", table_name="generation_jobs")
    op.drop_table("generation_jobs")
    op.drop_index("idx_assets_type", table_name="assets")
    op.drop_index("idx_assets_version_id", table_name="assets")
    op.drop_index("idx_assets_project_id", table_name="assets")
    op.drop_table("assets")
    op.drop_table("creative_briefs")
    op.drop_index("idx_projects_status", table_name="projects")
    op.drop_index("idx_projects_created_at", table_name="projects")
    op.drop_table("projects")
    export_format.drop(op.get_bind(), checkfirst=True)
    job_status.drop(op.get_bind(), checkfirst=True)
    generation_job_type.drop(op.get_bind(), checkfirst=True)
    asset_type.drop(op.get_bind(), checkfirst=True)
    project_status.drop(op.get_bind(), checkfirst=True)
