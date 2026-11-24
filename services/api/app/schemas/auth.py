from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    role: UserRole
