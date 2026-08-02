"""store asset bytes

Revision ID: 0002_asset_content
Revises: 0001_initial
Create Date: 2026-08-02
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_asset_content"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("content", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("assets", "content")
