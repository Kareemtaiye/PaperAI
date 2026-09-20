from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    async def find_user_by_id(self, db: AsyncSession, id: str):
        result = await db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()
