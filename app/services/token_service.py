from datetime import datetime, timedelta
from uuid import UUID

from app.repositories.token_repo import TokenRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TokenService:
    def __init__(self):
        self.repo = TokenRepository()

    async def create_refresh_token(
        self,
        db: AsyncSession,
        user_id: str | UUID,
        token_hash: str,
        expiry: datetime | None = None,
    ):
        expires_at = datetime.utcnow() + timedelta(days=7)

        if expiry:
            expires_at = expiry

        return await self.repo.create_refresh_token(db, user_id, token_hash, expires_at)

    async def get_refresh_token_by_token(self, db: AsyncSession, token: str):
        return await self.repo.get_refresh_token_by_token(db, token)

    async def get_refresh_token_by_user_id(self, db: AsyncSession, user_id: str):
        return self.repo.get_refresh_token_by_user_id(db, user_id)

    async def revoke_refresh_token(self, db: AsyncSession, token: str):
        return self.repo.revoke_refresh_token(db, token)

    async def revoke_user_refresh_tokens(self, db: AsyncSession, user_id: str):
        return self.repo.revoke_user_refresh_tokens(db, user_id)
