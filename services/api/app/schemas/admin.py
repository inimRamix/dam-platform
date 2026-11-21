from pydantic import BaseModel, EmailStr

from app.schemas.validators import Password


class AdminActivateRequest(BaseModel):
    email: EmailStr
    password: Password
    first_name: str
    last_name: str
