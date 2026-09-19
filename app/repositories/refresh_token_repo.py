from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from app.db.models.refresh_token import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession


class RefreshTokenRepository:
    async def create_refresh_token(
        self,
        db: AsyncSession,
        user_id: str | UUID,
        token_hash: str,
        expires_at: str | datetime,
    ):
        token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token

    async def get_refresh_token_by_token(self, db: AsyncSession, token: str):
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token)
        )
        return result.scalar_one_or_none()

    async def get_refresh_token_by_user_id(self, db: AsyncSession, user_id: str):
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return result.scalar_one_or_none()
