from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.db.models.paper import Paper
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_paper import UserPaper


class PaperRepostiory:
    async def create_paper_manual(self, db: AsyncSession, title: str, source: str):
        paper = Paper(title=title, source=source)

        db.add(paper)
        await db.commit()
        await db.refresh(paper)
        return paper

    async def get_all_user_papers(self, db: AsyncSession, user_id: str | UUID):
        result = await db.execute(
            select(UserPaper)
            .where(UserPaper.user_id == user_id)
            .options(selectinload(UserPaper.paper))
            .order_by(UserPaper.created_at)
        )

        return result.scalars().all()

    async def get_user_paper(
        self, db: AsyncSession, user_id: str | UUID, paper_id: str | UUID
    ):
        result = await db.execute(
            select(UserPaper)
            .where(UserPaper.user_id == user_id)
            .where(UserPaper.paper_id == paper_id)
            .options(selectinload(UserPaper.paper))
        )

        return result.scalar_one_or_none()

    async def delete_user_paper(
        self, db: AsyncSession, user_id: str | UUID, paper_id: str | UUID
    ):
        result = await db.execute(
            delete(UserPaper)
            .where(UserPaper.user_id == user_id)
            .where(UserPaper.paper_id == paper_id)
            .returning(UserPaper.id)
        )

        await db.commit()
        deleted = result.fetchone()
        return delete is not None
