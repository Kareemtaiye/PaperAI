from uuid import UUID

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

        async with db.begin():
            paper = await self.repo.create_paper_manual(
                db=db, title=title, source="manual"
            )

            user_paper = await user_paper_service.create_user_paper(
                db=db, user_id=user_id, paper_id=paper.id
            )

        await db.refresh(paper)
        await db.refresh(user_paper)

        return paper, user_paper
