import uuid
from sqlalchemy import Column, String, DateTime, Integer, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    arxiv_id = Column(String, unique=True, nullable=True, index=True)
    title = Column(String, nullable=True)
    abstract = Column(String, nullable=True)
    authors = Column(ARRAY(String), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    citation_count = Column(Integer, default=0)
    source = Column(String, nullable=False, default="arxiv")
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    # relationships
    user_papers = relationship(
        "UserPaper", back_populates="paper", cascade="all, delete-orphan"
    )
    analysis = relationship("PaperAnalysis", back_populates="paper", uselist=False)

    relationships_as_source = relationship(
        "PaperRelationship",
        foreign_keys="PaperRelationship.source_paper_id",
        back_populates="source_paper",
    )
    relationships_as_target = relationship(
        "PaperRelationship",
        foreign_keys="PaperRelationship.target_paper_id",
        back_populates="target_paper",
    )
