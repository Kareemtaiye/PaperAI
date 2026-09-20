from app.db.models.paper import Paper
from sqlalchemy.ext.asyncio import AsyncSession


class PaperRepostiory:
    async def create_paper_manual(self, db: AsyncSession, title: str, source: str):
        paper = Paper(title=title, source=source)

        db.add(paper)
        await db.commit()
        await db.refresh(paper)
        return paper
