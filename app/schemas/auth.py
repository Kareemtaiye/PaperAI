from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class BaseUser(BaseModel):
    email: EmailStr


class RegisterInput(BaseUser):
    password: str


class LoginInput(BaseModel):
    username: EmailStr
    password: str


class UserOuput(BaseUser):
    id: str | UUID
    role: str = "user"
    email_verified: bool
    is_demo: bool
    created_at: str | datetime
    updated_at: str | datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    status: str
    message: str | None = None
    data: UserOuput
