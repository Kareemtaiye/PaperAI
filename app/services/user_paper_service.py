from uuid import UUID

from app.repositories.user_paper_repo import UserPaperRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserPaperService:
    def __init__(self):
        self.repo = UserPaperRepository()

    async def create_user_paper(
        self,
        db: AsyncSession,
        user_id: str | UUID,
        paper_id: str | UUID,
        status: str | None = None,
        notes: str | None = None,
    ):
        return await self.repo.create_user_paper(
            db=db, user_id=user_id, paper_id=paper_id, status=status, notes=notes
        )
