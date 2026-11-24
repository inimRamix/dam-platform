import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.database import get_session
from app.dependencies import require_admin
from app.models.user import User
from app.models.user_invitation import UserInvitation
from app.schemas.auth import TokenResponse
from app.schemas.users import (
    ActivateUserRequest,
    InviteUserRequest,
    InviteResponse
)
from app.services.email import send_email
from app.utils.url_builder import build_user_activation_url

router = APIRouter(prefix=settings.api.v1.users, tags=["Users"])


@router.post("/invite", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    data: InviteUserRequest,
    admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    existing_user = await session.execute(
        select(User).where(User.email == data.email).limit(1)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    token = secrets.token_urlsafe(32)

    invitation = UserInvitation(
        email=data.email,
        token=token,
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=settings.invitation_expire_minutes),
        invited_by=admin.id,
        role=data.role,
    )
    session.add(invitation)
    await session.commit()

    link = build_user_activation_url(token)
    await send_email(
        to=data.email,
        subject="Приглашение в DAM",
        body=(
            "<p>Вы приглашены в систему. Перейдите по ссылке:</p>"
            f"<a href='{link}'>{link}</a>"
        ),
    )

    return InviteResponse(message="Приглашение отправлено", email=data.email)


@router.post("/activate", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def activate_user(
    data: ActivateUserRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    token: str = Query(..., description="Токен приглашения из ссылки"),
):
    invite_result = await session.execute(
        select(UserInvitation).where(UserInvitation.token == token)
    )
    invite = invite_result.scalar_one_or_none()
    if (
        not invite
        or invite.used
        or invite.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный токен",
        )

    existing_user = await session.execute(
        select(User).where(User.email == invite.email).limit(1)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    user = User(
        email=invite.email,
        hashed_password=hash_password(data.password),
        role=invite.role,
    )
    session.add(user)
    invite.used = True
    await session.commit()

    access_token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token)
