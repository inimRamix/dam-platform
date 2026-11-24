from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.asset import AssetType, ProcessingStatus


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    parent_id: UUID | None
    owner_id: UUID
    created_at: datetime


class AssetVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_number: int
    original_filename: str
    mime_type: str
    size_bytes: int
    thumbnail_key: str | None
    dominant_colors: list[str] | None
    processing_status: ProcessingStatus
    created_at: datetime


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    asset_type: AssetType
    collection_id: UUID | None
    current_version_id: UUID | None
    uploaded_by: UUID
    tags: list[TagRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class AssetDetailRead(AssetRead):
    versions: list[AssetVersionRead] = Field(default_factory=list)


class AssetListResponse(BaseModel):
    items: list[AssetRead]
    total: int
    page: int
    page_size: int
