from pydantic import UUID1, BaseModel


class BaseUser(BaseModel):
    full_name: str
    email: str


class UserLoginInput(BaseUser):
    password: str


class UserLoginOuput(BaseUser):
    id: str | UUID1
    role: str = "user"
    email_verified: bool
    is_demo: bool
