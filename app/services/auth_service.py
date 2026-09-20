from app.core.security import (
    DUMMY_HASH,
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.repositories.auth_repo import AuthRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginInput, RegisterInput
from app.services.token_service import TokenService

token_service = TokenService()


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

        access_token = generate_access_token(str(user.id))
        refresh_token = generate_refresh_token()
        # Create session later
        try:
            await token_service.create_refresh_token(
                db=db, user_id=user.id, token_hash=hash_token(refresh_token)
            )

        except Exception as exc:
            raise exc

        # refresh token later - for managing Session later
        return access_token, refresh_token

    # async def rotate_refresh_token(self, db: AsyncSession, token: str):
    #     token = await token_service.get_refresh_token_by_token(db, token)

    #     if not token:
    #         return None
