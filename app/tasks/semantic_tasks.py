import time

from app.db.session import get_sync_db
from app.tasks import celery_app
from app.services.semantic_scholar_service import semantic_service


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def import_sematic_scholar_paper(self, arxiv_id: str, owner_id: str, owner_email: str):

    res = semantic_service.fetch_paper_by_arxiv_id(arxiv_id)
    data = semantic_service.parse_paper(res)
