from app.repositories.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    async def find_user_by_id(self, db: AsyncSession, id: str):
        return await self.repo.find_user_by_id(db, id)
