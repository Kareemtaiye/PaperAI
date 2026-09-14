import uuid

from sqlalchemy import Column, ForeignKey, Enum, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Relationship(Base):
    __tablename__ = "relationship"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_paper_id = Column(
        UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False
    )
    target_paper_id = Column(
        UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False
    )
    relationship_type = Column(Enum("extends", "contradicts", "applies", "surveys"))
    description = Column(String, nullable=True)
    confidence_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
