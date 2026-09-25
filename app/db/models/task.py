import uuid

from sqlalchemy import Column, ForeignKey, Integer, Enum, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_paper_id = Column(
        UUID(as_uuid=True), ForeignKey("user_papers.id"), nullable=True
    )
    celery_task_id = Column(String, nullable=True, index=True)
    task_type = Column(
        String, nullable=False
    )  # import_arxiv | import_semantic | analyse | digest
    status = Column(
        Enum("pending", "processing", "completed", "failed", name="task_status"),
        default="pending",
    )
    progress = Column(Integer, default=0)
    stage = Column(String, nullable=True)
    stage_message = Column(String, nullable=True)
    error = Column(String, nullable=True)
    worker_name = Column(String, nullable=True)
    stage_durations = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tasks")
    user_paper = relationship("UserPaper", back_populates="task")
