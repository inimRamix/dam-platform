import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssetType(str, PyEnum):
    IMAGE = "image"
    PDF = "pdf"
    OTHER = "other"


class ProcessingStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("collections.id", ondelete="SET NULL"), nullable=True
    )
    asset_type: Mapped[AssetType] = mapped_column(
        SAEnum(
            AssetType,
            name="asset_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "asset_versions.id",
            use_alter=True,
            name="fk_assets_current_version_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    collection: Mapped["Collection | None"] = relationship(
        "Collection", back_populates="assets"
    )
    current_version: Mapped["AssetVersion | None"] = relationship(
        "AssetVersion",
        foreign_keys=[current_version_id],
        post_update=True,
    )
    versions: Mapped[list["AssetVersion"]] = relationship(
        "AssetVersion",
        back_populates="asset",
        foreign_keys="AssetVersion.asset_id",
        cascade="all, delete-orphan",
        order_by="AssetVersion.version_number",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="asset_tags", back_populates="assets"
    )


class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    thumbnail_key: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    dominant_colors: Mapped[list[str] | None] = mapped_column(
        JSONB, nullable=True
    )
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SAEnum(
            ProcessingStatus,
            name="processing_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ProcessingStatus.PENDING,
        nullable=False,
    )

    asset: Mapped["Asset"] = relationship(
        "Asset", back_populates="versions", foreign_keys=[asset_id]
    )
