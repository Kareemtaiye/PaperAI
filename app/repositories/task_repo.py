from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task


class TaskRepository:
    async def create_task(
        self,
        db: AsyncSession,
        user_id: str | UUID,
        user_paper_id: str | UUID,
        task_type: str,
    ) -> Task:
        task = Task(user_id=user_id, user_paper_id=user_paper_id, task_type=task_type)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def find_task_by_id(
        self,
        db: AsyncSession,
        task_id: str,
        user_id: str | UUID,
    ) -> Task | None:
        result = await db.execute(
            select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        )
        return result.scalar_one_or_none()
