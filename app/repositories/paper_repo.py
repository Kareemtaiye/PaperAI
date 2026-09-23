from uuid import UUID
from celery import result
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.db.models.paper import Paper
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_paper import UserPaper
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.routers import paper


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

    async def create_paper_import(
        self, db: AsyncSession, source_id: str, source_url: str, source: str
    ):
        stmt = (
            pg_insert(Paper)
            .values(source_id=source_id, source_url=source_url, source=source)
            .on_conflict_do_nothing(constraint="uq_paper_source_id_source")
        )
        await db.execute(stmt)
        await db.commit()

        result = await db.execute(select(Paper).where(Paper.source_id == source_id))
        return result.scalar_one_or_none()
