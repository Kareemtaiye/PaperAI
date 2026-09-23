import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.tasks.celery_app import celery_app
from app.db.session import get_sync_db
from app.db.models.paper import Paper
from app.db.models.user_paper import UserPaper
from app.db.models.task import Task

ARXIV_API = "https://export.arxiv.org/api/query"
NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


def update_task(db, task_id, status, progress, stage, stage_message, error=None):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if not task:
        return
    task.status = status
    task.progress = progress
    task.stage = stage
    task.stage_message = stage_message
    if error:
        task.error = error
    if status in ("completed", "failed"):
        task.completed_at = datetime.now(timezone.utc)
    db.commit()


def update_user_paper(db, user_paper_id, status):
    user_paper = db.execute(
        select(UserPaper).where(UserPaper.id == user_paper_id)
    ).scalar_one_or_none()
    if not user_paper:
        return
    user_paper.status = status
    db.commit()


@celery_app.task(
    bind=True, max_retries=3, default_retry_delay=60, name="import_arxiv_paper"
)
def import_arxiv_paper(
    self, paper_id: str, user_paper_id: str, task_id: str, arxiv_id: str, owner_id: str
):
    db = get_sync_db()
    try:
        # Stage 1 — started
        update_task(db, task_id, "processing", 10, "fetching", "Fetching from Arxiv...")
        update_user_paper(db, user_paper_id, "processing")

        # Stage 2 — fetch from Arxiv
        response = httpx.get(
            ARXIV_API,
            params={"id_list": arxiv_id, "max_results": 1},
            timeout=30.0,
            follow_redirects=True,
        )
        response.raise_for_status()

        update_task(db, task_id, "processing", 40, "parsing", "Parsing metadata...")

        # Stage 3 — parse XML
        root = ET.fromstring(response.text)
        entry = root.find("atom:entry", NAMESPACE)

        if entry is None:
            update_task(
                db,
                task_id,
                "failed",
                0,
                "failed",
                "Paper not found on Arxiv",
                error="No entry found",
            )
            update_user_paper(db, user_paper_id, "failed")
            return

        title = entry.find("atom:title", NAMESPACE).text.strip()
        abstract = entry.find("atom:summary", NAMESPACE).text.strip()
        published = entry.find("atom:published", NAMESPACE).text

        authors = [
            author.find("atom:name", NAMESPACE).text
            for author in entry.findall("atom:author", NAMESPACE)
        ]

        categories = [
            cat.get("term")
            for cat in entry.findall("{http://arxiv.org/schemas/atom}category")
        ]

        published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))

        update_task(db, task_id, "processing", 70, "saving", "Saving to database...")

        # Stage 4 — update paper with real metadata
        paper = db.execute(
            select(Paper).where(Paper.id == paper_id)
        ).scalar_one_or_none()

        if paper:
            paper.title = title
            paper.abstract = abstract
            paper.authors = authors
            paper.categories = categories
            paper.published_at = published_at
            db.commit()

        update_task(db, task_id, "processing", 90, "finishing", "Finalizing...")

        # Stage 5 — complete
        update_user_paper(db, user_paper_id, "completed")
        update_task(db, task_id, "completed", 100, "completed", "Import complete")

        # TODO: publish WebSocket event
        # TODO: send email notification

        return {"status": "completed", "paper_id": paper_id, "title": title}

    except httpx.TimeoutException as exc:
        update_task(
            db, task_id, "failed", 0, "failed", "Timeout fetching Arxiv", error=str(exc)
        )
        update_user_paper(db, user_paper_id, "failed")
        raise self.retry(exc=exc, countdown=2**self.request.retries * 60)

    except Exception as exc:
        update_task(db, task_id, "failed", 0, "failed", str(exc), error=str(exc))
        update_user_paper(db, user_paper_id, "failed")
        raise self.retry(exc=exc)

    finally:
        db.close()
