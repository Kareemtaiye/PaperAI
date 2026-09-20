from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PaperManualCreate(BaseModel):
    title: str
    notes: Optional[str] = None


class PaperResponse(BaseModel):
    id: UUID
    title: Optional[str]
    abstract: Optional[str]
    authors: Optional[list[str]]
    categories: Optional[list[str]]
    arxiv_id: Optional[str]
    source: str
    published_at: Optional[datetime]

    # user-specific fields from user_papers
    status: Optional[str]
    notes: Optional[str]
    progress: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
