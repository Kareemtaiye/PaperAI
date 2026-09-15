import uuid

from sqlalchemy import Column, ForeignKey, Enum, Integer, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from sqlalchemy.orm import relationship


class PaperRelationship(Base):
    __tablename__ = "paper_relationships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_paper_id = Column(
        UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False
    )
    target_paper_id = Column(
        UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False
    )
    relationship_type = Column(
        Enum(
            "extends",
            "contradicts",
            "applies",
            "surveys",
            name="relationship_type",
        ),
        nullable=False,
    )
    description = Column(String, nullable=True)
    confidence_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    source_paper = relationship(
        "Paper",
        foreign_keys=[source_paper_id],
        back_populates="relationships_as_source",
    )
    target_paper = relationship(
        "Paper",
        foreign_keys=[target_paper_id],
        back_populates="relationships_as_target",
    )
