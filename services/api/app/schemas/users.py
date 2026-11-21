from typing import Optional, Literal

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: Optional[Literal["designer", "manager"]] = "designer"


class ActivateUserRequest(BaseModel):
    token: str
    password: str
    first_name: str
    last_name: str
