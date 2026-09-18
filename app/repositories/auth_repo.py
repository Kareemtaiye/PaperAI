from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.schemas.auth import RegisterInput


class AuthRepository:
    async def create_user(self, db: AsyncSession, data: dict):
        user = User(**data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def find_user_by_email(aelf, db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
