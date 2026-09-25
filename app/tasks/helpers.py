import asyncio

from datetime import datetime, timezone
from sqlalchemy import select

from app.db.models.user_paper import UserPaper
from app.db.models.task import Task
from app.services.pubsub import pubsub_manager


def update_task(
    db, task_id, status, progress, stage, stage_message, stage_durations, error=None
):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if not task:
        return
    task.status = status
    task.progress = progress
    task.stage = stage
    task.stage_message = stage_message
    if error:
        task.error = error
    if status in ("completed", "failed"):
        task.completed_at = datetime.now(timezone.utc)
    if stage_durations is not None:
        task.stage_durations = stage_durations
    db.commit()


def publish_task_status(owner_id: str, payload: dict):
    asyncio.run(pubsub_manager.publish(owner_id, payload))


def update_user_paper(db, user_paper_id, status):
    user_paper = db.execute(
        select(UserPaper).where(UserPaper.id == user_paper_id)
    ).scalar_one_or_none()
    if not user_paper:
        return
    user_paper.status = status
    db.commit()
