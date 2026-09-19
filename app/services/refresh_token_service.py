from datetime import datetime, timedelta
from uuid import UUID

from app.repositories.refresh_token_repo import RefreshTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession


class RefreshTokenService:
    def __init__(self):
        self.repo = RefreshTokenRepository()

    async def create_refresh_token(
        self, db: AsyncSession, user_id: str | UUID, token_hash: str
    ):
        expires_at = datetime.utcnow() + timedelta(days=7)
        return await self.repo.create_refresh_token(db, user_id, token_hash, expires_at)

    async def get_refresh_token_by_token(self, db: AsyncSession, token: str):
        return await self.repo.get_refresh_token_by_token(db, token)

    async def get_refresh_token_by_user_id(self, db: AsyncSession, user_id: str):
        return self.repo.get_refresh_token_by_user_id(db, user_id)
