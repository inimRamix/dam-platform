from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.database import get_session
from app.models.admin_activation_token import AdminActivationToken
from app.models.user import User, UserRole
from app.schemas.admin import AdminActivateRequest
from app.schemas.auth import TokenResponse

router = APIRouter(prefix=settings.api.v1.admin, tags=["Admin"])


@router.post("/activate", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def activate_admin(
    token: str = Query(..., description="Токен активации из ссылки"),
    data: AdminActivateRequest = Body(...),
    session: AsyncSession = Depends(get_session),
    # session: Annotated[AsyncSession, Depends(get_session)]
):
    existing = await session.execute(select(User).where(User.role == UserRole.ADMIN))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Администратор уже существует"
        )

    token_entry = await session.execute(
        select(AdminActivationToken).where(AdminActivationToken.token == token)
    )
    token_entry = token_entry.scalar_one_or_none()
    if not token_entry or token_entry.used or token_entry.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Недействительный токен"
        )

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.ADMIN,
    )
    session.add(user)
    token_entry.used = True
    await session.commit()

    access_token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token)
