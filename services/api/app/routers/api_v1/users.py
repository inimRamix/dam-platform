import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.database import get_session
from app.dependencies import require_admin
from app.models.user import User
from app.models.user_invitation import UserInvitation
from app.schemas.auth import TokenResponse
from app.schemas.users import ActivateUserRequest, InviteUserRequest
from app.services.email import send_email
from app.utils.url_builder import build_user_activation_url

router = APIRouter(prefix=settings.api.v1.users, tags=["Users"])


@router.post("/invite", status_code=status.HTTP_204_NO_CONTENT)
async def invite_user(
    data: InviteUserRequest,
    admin: Annotated[User, Depends(require_admin)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
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
        body=f"<p>Вы приглашены в систему. Перейдите по ссылке:</p><a href='{link}'>{link}</a>",
    )


@router.post("/activate", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def activate_user(
    data: ActivateUserRequest, session: Annotated[AsyncSession, Depends(get_session)]
):
    invite = await session.execute(select(UserInvitation).where(UserInvitation.token == data.token))
    invite = invite.scalar_one_or_none()
    if not invite or invite.used or invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Недействительный токен"
        )

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=invite.email,
        hashed_password=hash_password(data.password),
        role=invite.role,
    )
    session.add(user)
    invite.used = True
    await session.commit()

    access_token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token)
