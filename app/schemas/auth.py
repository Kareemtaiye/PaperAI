from pydantic import UUID1, BaseModel, EmailStr


class BaseUser(BaseModel):
    email: str


class RegisterInput(BaseUser):
    password: str


class UserLoginInput(BaseModel):
    username: EmailStr
    password: str


class UserLoginOuput(BaseUser):
    id: str | UUID1
    role: str = "user"
    email_verified: bool
    is_demo: bool
    created_at: str
    updated_at: str
