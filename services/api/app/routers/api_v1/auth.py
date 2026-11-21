from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead

router = APIRouter(prefix=settings.api.v1.auth, tags=["Auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(data: LoginRequest, session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
        )

    access_token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
