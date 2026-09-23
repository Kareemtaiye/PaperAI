from pydantic import BaseModel


class ArxivImportRequest(BaseModel):
    arxiv_url: str


class ArxivImportResponse(BaseModel):
    paper_id: str
    user_paper_id: str
    task_id: str
    celery_task_id: str
    status: str
    message: str
