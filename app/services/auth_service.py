from app.core.security import hash_password
from app.repositories.auth_repo import AuthRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegisterInput


class AuthService:
    def __init__(self):
        self.repo = AuthRepository()

    async def register(self, db: AsyncSession, user: RegisterInput):
        data = user.model_dump()
        data["password_hash"] = hash_password(data.pop("password"))

        return await self.repo.create_user(db, data)

    async def find_user_by_email(self, db: AsyncSession, email: str):
        user = await self.repo.find_user_by_email(db=db, email=email)

        if not user:
            return None  # --- im raising UserNotFoundException later

        return user
