import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base


class PaperAnalysis(Base):
    __tablename__ = "paper_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(
        UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False, unique=True
    )
    summary = Column(String, nullable=True)
    contributions = Column(ARRAY(String), nullable=True)
    limitations = Column(ARRAY(String), nullable=True)
    topics = Column(ARRAY(String), nullable=True)
    difficulty = Column(String, nullable=True)
    recommended_for = Column(String, nullable=True)
    status = Column(
        Enum("pending", "completed", "failed", name="analysis_status"),
        default="pending",
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    # relationship
    paper = relationship("Paper", back_populates="analysis")
