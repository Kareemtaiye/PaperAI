import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Enum, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class Digest(Base):
    __tablename__ = "digests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=True)
    paper_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    synthesis = Column(String, nullable=True)
    status = Column(
        Enum("pending", "completed", "failed", name="digest_status"),
        default="pending",
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()")
    )

    user = relationship(
        "User",
        back_populates="digests",
    )
