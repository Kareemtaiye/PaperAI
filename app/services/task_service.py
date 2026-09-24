from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task import Task
from app.exceptions.resource_not_found import TaskNotFoundException
from app.repositories.task_repo import TaskRepository


class TaskService:
    def __init__(self):
        self.repo = TaskRepository()

    async def create_task(
        self,
        db: AsyncSession,
        user_id: str | UUID,
        user_paper_id: str | UUID,
        task_type: str,
    ) -> Task:
        return await self.repo.create_task(
            db=db, user_id=user_id, user_paper_id=user_paper_id, task_type=task_type
        )

    async def find_task_by_id(
        self, db: AsyncSession, user_id: str, task_id: str
    ) -> Task | None:
        task = await self.repo.find_task_by_id(db=db, user_id=user_id, task_id=task_id)
        if not task:
            raise TaskNotFoundException(task_id)
        return task
