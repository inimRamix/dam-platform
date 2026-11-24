import hashlib
import mimetypes
import uuid
from pathlib import Path
from typing import Annotated

import magic
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.database import get_session
from app.dependencies import get_current_user
from app.models.asset import Asset, AssetType, AssetVersion
from app.models.tag import Tag, asset_tags
from app.models.user import User
from app.schemas.asset import (
    AssetDetailRead,
    AssetListResponse,
    AssetRead,
)
from app.services.storage import storage
from app.utils.slugify import slugify

router = APIRouter(prefix=settings.api.v1.assets, tags=["Assets"])

ALLOWED_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
}


async def _resolve_tags(
    session: AsyncSession, raw: str
) -> list[Tag]:
    names = [n.strip() for n in raw.split(",") if n.strip()]
    if not names:
        return []

    seen_slugs: set[str] = set()
    result: list[Tag] = []
    for name in names:
        slug = slugify(name)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        existing = await session.execute(
            select(Tag).where(Tag.slug == slug).limit(1)
        )
        tag = existing.scalar_one_or_none()
        if tag is None:
            tag = Tag(name=name, slug=slug)
            session.add(tag)
        result.append(tag)
    return result


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    title: Annotated[str, Form(min_length=1, max_length=255)],
    file: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form()] = None,
    tags: Annotated[str, Form()] = "",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if file.size and file.size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Файл больше {settings.max_file_size_bytes // (1024 * 1024)} МБ"
            ),
        )

    header = await file.read(2048)
    detected = magic.from_buffer(header, mime=True)
    await file.seek(0)

    if detected not in ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Неподдерживаемый тип файла: {detected}",
        )

    hasher = hashlib.sha256()
    while chunk := await file.read(65536):
        hasher.update(chunk)
    checksum = hasher.hexdigest()
    await file.seek(0)

    asset_id = uuid.uuid4()
    version_id = uuid.uuid4()
    suffix = Path(file.filename or "").suffix.lower() or ".bin"
    file_key = f"assets/{asset_id}/v1/original{suffix}"

    await storage.upload_fileobj(file_key, file.file, detected)

    asset = Asset(
        id=asset_id,
        title=title,
        description=description,
        asset_type=AssetType.IMAGE,
        uploaded_by=current_user.id,
    )
    version = AssetVersion(
        id=version_id,
        asset_id=asset_id,
        version_number=1,
        file_key=file_key,
        original_filename=file.filename or f"file{suffix}",
        mime_type=detected,
        size_bytes=file.size or 0,
        checksum=checksum,
        uploaded_by=current_user.id,
    )
    session.add_all([asset, version])
    await session.flush()
    asset.current_version_id = version_id

    resolved_tags = await _resolve_tags(session, tags)
    if resolved_tags:
        await session.flush()
        await session.execute(
            insert(asset_tags),
            [
                {"asset_id": asset_id, "tag_id": tag.id}
                for tag in resolved_tags
            ],
        )

    await session.commit()

    stmt = (
        select(Asset)
        .where(Asset.id == asset_id)
        .options(selectinload(Asset.tags))
    )
    asset = (await session.execute(stmt)).scalar_one()
    return asset


@router.get("", response_model=AssetListResponse)
async def list_assets(
    q: Annotated[str | None, Query(max_length=255)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    base = select(Asset).where(Asset.deleted_at.is_(None))
    if q:
        base = base.where(Asset.title.ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        base.options(selectinload(Asset.tags))
        .order_by(Asset.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await session.execute(stmt)).scalars().all()

    return AssetListResponse(
        items=list(items), total=total, page=page, page_size=page_size
    )


@router.get("/{asset_id}", response_model=AssetDetailRead)
async def get_asset(
    asset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Asset)
        .where(Asset.id == asset_id, Asset.deleted_at.is_(None))
        .options(selectinload(Asset.tags), selectinload(Asset.versions))
    )
    asset = (await session.execute(stmt)).scalar_one_or_none()
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ассет не найден"
        )
    return asset


@router.get("/{asset_id}/versions/{version_number}/download")
async def download_version(
    asset_id: uuid.UUID,
    version_number: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(AssetVersion)
        .join(Asset, Asset.id == AssetVersion.asset_id)
        .where(
            AssetVersion.asset_id == asset_id,
            AssetVersion.version_number == version_number,
            Asset.deleted_at.is_(None),
        )
    )
    version = (await session.execute(stmt)).scalar_one_or_none()
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Версия не найдена"
        )

    return StreamingResponse(
        storage.stream_object(version.file_key),
        media_type=version.mime_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{version.original_filename}"'
            ),
            "Content-Length": str(version.size_bytes),
        },
    )
