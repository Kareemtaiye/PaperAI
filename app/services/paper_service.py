from uuid import UUID

from app.exceptions.resource_not_found import PaperNotFoundException
from app.repositories.paper_repo import PaperRepostiory
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_paper_service import UserPaperService

user_paper_service = UserPaperService()


class PaperService:
    def __init__(self):
        self.repo = PaperRepostiory()

    async def create_paper_manual(
        self, db: AsyncSession, title: str, user_id: str | UUID
    ):

        paper = await self.repo.create_paper_manual(db=db, title=title, source="manual")

        user_paper = await user_paper_service.create_user_paper(
            db=db, user_id=user_id, paper_id=paper.id
        )

        await db.refresh(paper)
        await db.refresh(user_paper)

        return paper, user_paper

    async def get_all_user_papers(self, db: AsyncSession, user_id: str | UUID):
        return await self.repo.get_all_user_papers(db=db, user_id=user_id)

    async def get_user_paper(
        self, db: AsyncSession, user_id: str | UUID, paper_id: str | UUID
    ):
        paper = await self.repo.get_user_paper(
            db=db, user_id=user_id, paper_id=paper_id
        )

        if not paper:
            raise PaperNotFoundException(paper_id)
        return paper

    async def delete_user_paper(
        self, db: AsyncSession, user_id: str | UUID, paper_id: str | UUID
    ):
        paper = await self.repo.delete_user_paper(
            db=db, user_id=user_id, paper_id=paper_id
        )

        if not paper:
            raise PaperNotFoundException(paper_id)
