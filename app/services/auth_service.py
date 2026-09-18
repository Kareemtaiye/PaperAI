from app.core.security import (
    DUMMY_HASH,
    generate_access_token,
    hash_password,
    verify_password,
)
from app.repositories.auth_repo import AuthRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginInput, RegisterInput


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

    async def login(self, db: AsyncSession, user_data: LoginInput):
        user = await self.repo.find_user_by_email(db=db, email=user_data.username)

        if not user:
            verify_password(user_data.username, DUMMY_HASH)  # for timing attack
            return None

        if not user.is_acive:
            # Logger warning later
            return None

        if not verify_password(user_data.password, user.password_hash):
            return None

        # Create session later

        access_token = generate_access_token(str(user.id))
        # refresh token later - for managing Session later
        return access_token
