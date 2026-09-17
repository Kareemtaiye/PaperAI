from pydantic import UUID1, BaseModel


class BaseUser(BaseModel):
    email: str


class UserLoginInput(BaseUser):
    password_hash: str


class UserLoginOuput(BaseUser):
    id: str | UUID1
    role: str = "user"
    email_verified: bool
    is_demo: bool
    created_at: str
    updated_at: str
