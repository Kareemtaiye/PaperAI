import uuid
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserPaper(Base):
    __tablename__ = "user_papers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    status = Column(String, default="pending")
    task_id = Column(String, nullable=True)
    progress = Column(Integer, default=0)
    stage = Column(String, nullable=True)
    stage_message = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    __table_args__ = (UniqueConstraint("user_id", "paper_id"),)

    # relationships
    user = relationship("User", back_populates="user_papers")
    paper = relationship("Paper", back_populates="user_papers")
    task = relationship("Task", back_populates="user_paper")
