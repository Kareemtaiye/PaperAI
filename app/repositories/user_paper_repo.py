from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_paper import UserPaper


class UserPaperRepository:
    async def create_user_paper(
        self,
        db: AsyncSession,
        user_id: str | UUID,
        paper_id: str | UUID,
        status: str | None = None,
        notes: str | None = None,
    ):
        user_paper = UserPaper(
            user_id=user_id, paper_id=paper_id, status=status, notes=notes
        )
        db.add(user_paper)
        await db.commit()
        await db.refresh(user_paper)

        return user_paper
