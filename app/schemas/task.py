# app/schemas/task_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    user_paper_id: Optional[uuid.UUID]
    celery_task_id: Optional[str]
    task_type: str
    status: str
    progress: int
    stage: Optional[str]
    stage_message: Optional[str]
    error: Optional[str]
    worker_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
