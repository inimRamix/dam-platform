from typing import Optional, Literal

from pydantic import BaseModel, EmailStr

from app.schemas.validators import Password


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: Optional[Literal["designer", "manager"]] = "designer"


class ActivateUserRequest(BaseModel):
    password: Password
    first_name: str
    last_name: str


class InviteResponse(BaseModel):
    message: str
    email: EmailStr
