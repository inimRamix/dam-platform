"""add assets collections tags

Revision ID: 5bc2e8bcb51b
Revises: 6863b01c0f34
Create Date: 2026-11-24 12:44:07.763409

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5bc2e8bcb51b"
down_revision: Union[str, Sequence[str], None] = "6863b01c0f34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tags")),
        sa.UniqueConstraint("name", name=op.f("uq_tags_name")),
    )
    op.create_index(op.f("ix_tags_slug"), "tags", ["slug"], unique=True)

    op.create_table(
        "collections",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=op.f("fk_collections_owner_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["collections.id"],
            name=op.f("fk_collections_parent_id_collections"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collections")),
    )

    # assets создаётся БЕЗ FK на asset_versions (добавим отдельно ниже)
    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collection_id", sa.UUID(), nullable=True),
        sa.Column(
            "asset_type",
            sa.Enum("image", "pdf", "other", name="asset_type"),
            nullable=False,
        ),
        sa.Column("current_version_id", sa.UUID(), nullable=True),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=op.f("fk_assets_collection_id_collections"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name=op.f("fk_assets_uploaded_by_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assets")),
    )

    op.create_table(
        "asset_tags",
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("tag_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["assets.id"],
            name=op.f("fk_asset_tags_asset_id_assets"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
            name=op.f("fk_asset_tags_tag_id_tags"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("asset_id", "tag_id", name=op.f("pk_asset_tags")),
    )

    op.create_table(
        "asset_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("file_key", sa.String(length=500), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("thumbnail_key", sa.String(length=500), nullable=True),
        sa.Column(
            "dominant_colors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column(
            "processing_status",
            sa.Enum(
                "pending", "processing", "done", "failed",
                name="processing_status",
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["assets.id"],
            name=op.f("fk_asset_versions_asset_id_assets"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name=op.f("fk_asset_versions_uploaded_by_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_asset_versions")),
    )
    op.create_index(
        op.f("ix_asset_versions_asset_id"),
        "asset_versions",
        ["asset_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_asset_versions_checksum"),
        "asset_versions",
        ["checksum"],
        unique=False,
    )

    # Теперь, когда asset_versions существует, добавляем FK из assets
    op.create_foreign_key(
        "fk_assets_current_version_id",
        "assets",
        "asset_versions",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Сначала снимаем FK, потом дропаем таблицы
    op.drop_constraint(
        "fk_assets_current_version_id", "assets", type_="foreignkey"
    )
    op.drop_index(
        op.f("ix_asset_versions_checksum"), table_name="asset_versions"
    )
    op.drop_index(
        op.f("ix_asset_versions_asset_id"), table_name="asset_versions"
    )
    op.drop_table("asset_versions")
    op.drop_table("asset_tags")
    op.drop_table("assets")
    op.drop_table("collections")
    op.drop_index(op.f("ix_tags_slug"), table_name="tags")
    op.drop_table("tags")
