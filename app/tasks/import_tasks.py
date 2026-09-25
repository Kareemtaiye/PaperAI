from datetime import datetime
import time

import httpx
import xml.etree.ElementTree as ET
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.db.session import get_sync_db
from app.db.models.paper import Paper
from app.tasks.helpers import publish_task_status, update_task, update_user_paper

ARXIV_API = "https://export.arxiv.org/api/query"
NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


@celery_app.task(
    bind=True, max_retries=3, default_retry_delay=60, name="import_arxiv_paper"
)
def import_arxiv_paper(
    self, paper_id: str, user_paper_id: str, task_id: str, arxiv_id: str, owner_id: str
):
    db = get_sync_db()
    task_start = time.time()
    try:
        # Stage 1 — started
        stage_start = time.time()
        update_task(
            db,
            task_id,
            owner_id,
            "processing",
            10,
            "fetching",
            "Fetching from Arxiv...",
            stage_durations={},
        )

        publish_task_status(
            owner_id,
            {
                "event": "task_update",
                "task_id": task_id,
                "paper_id": paper_id,
                "status": "processing",
                "progress": 10,
                "stage": "fetching",
                "stage_message": "Fetching from Arxiv...",
                "elapsed_seconds": round(time.time() - task_start, 2),
            },
        )

        update_user_paper(db, user_paper_id, "processing")

        # Stage 2 — fetch from Arxiv
        stage_start = time.time()
        response = httpx.get(
            ARXIV_API,
            params={"id_list": arxiv_id, "max_results": 1},
            timeout=30.0,
            follow_redirects=True,
        )
        fetch_duration = round(time.time() - stage_start, 2)
        response.raise_for_status()

        stage_start = time.time()
        update_task(
            db,
            task_id,
            owner_id,
            "processing",
            40,
            "parsing",
            "Parsing metadata...",
            stage_durations={"fetching": fetch_duration},
        )

        publish_task_status(
            owner_id,
            {
                "event": "task_update",
                "task_id": task_id,
                "paper_id": paper_id,
                "status": "processing",
                "progress": 40,
                "stage": "parsing",
                "stage_message": "Parsing metadata...",
                "elapsed_seconds": round(time.time() - task_start, 2),
                "stage_durations": {"fetching": fetch_duration},
            },
        )

        # Stage 3 — parse XML
        root = ET.fromstring(response.text)
        entry = root.find("atom:entry", NAMESPACE)

        if entry is None:
            update_task(
                db,
                task_id,
                owner_id,
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
        parse_duration = round(time.time() - stage_start, 2)

        stage_start = time.time()
        update_task(
            db,
            task_id,
            owner_id,
            "processing",
            70,
            "saving",
            "Saving to database...",
            stage_durations={"fetching": fetch_duration, "parsing": parse_duration},
        )

        publish_task_status(
            owner_id,
            {
                "event": "task_update",
                "task_id": task_id,
                "paper_id": paper_id,
                "status": "processing",
                "progress": 70,
                "stage": "saving",
                "stage_message": "Saving to database...",
                "elapsed_seconds": round(time.time() - task_start, 2),
                "stage_durations": {
                    "fetching": fetch_duration,
                    "parsing": parse_duration,
                },
            },
        )

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

        # After saving to db
        save_duration = round(time.time() - stage_start, 2)

        stage_start = time.time()
        update_task(
            db,
            task_id,
            owner_id,
            "processing",
            90,
            "finishing",
            "Finalizing...",
            stage_durations={
                "fetching": fetch_duration,
                "parsing": parse_duration,
                "saving": save_duration,
            },
        )

        publish_task_status(
            owner_id,
            {
                "event": "task_update",
                "task_id": task_id,
                "paper_id": paper_id,
                "status": "processing",
                "progress": 90,
                "stage": "finishing",
                "stage_message": "Finalizing...",
                "elapsed_seconds": round(time.time() - task_start, 2),
                "stage_durations": {
                    "fetching": fetch_duration,
                    "parsing": parse_duration,
                    "saving": save_duration,
                },
            },
        )

        # Stage 5 — complete
        total_duration = round(time.time() - task_start, 2)
        update_user_paper(db, user_paper_id, "completed")
        update_task(
            db,
            task_id,
            owner_id,
            "completed",
            100,
            "completed",
            "Import complete",
            stage_durations={
                "fetching": fetch_duration,
                "parsing": parse_duration,
                "saving": save_duration,
                "total": total_duration,
            },
        )
        publish_task_status(
            owner_id,
            {
                "event": "import_completed",
                "task_id": task_id,
                "paper_id": paper_id,
                "user_paper_id": user_paper_id,
                "status": "completed",
                "progress": 100,
                "title": title,
                "authors": authors,
                "categories": categories,
                "total_duration_seconds": total_duration,
                "stage_durations": {
                    "fetching": fetch_duration,
                    "parsing": parse_duration,
                    "saving": save_duration,
                },
            },
        )

        # TODO: send email notification

        return {"status": "completed", "paper_id": paper_id, "title": title}

    except httpx.TimeoutException as exc:
        is_final_retry = self.request.retries >= self.max_retries
        update_task(
            db,
            task_id,
            owner_id,
            "failed" if is_final_retry else "processing",
            0,
            "retrying",
            "Timeout — retrying...",
            error=str(exc),
        )
        update_user_paper(
            db, user_paper_id, "failed" if is_final_retry else "processing"
        )

        if is_final_retry:
            publish_task_status(
                owner_id,
                {
                    "event": "import_failed",
                    "task_id": task_id,
                    "paper_id": paper_id,
                    "status": "failed",
                    "error": "Timeout fetching from Arxiv after 3 retries",
                },
            )

        raise self.retry(exc=exc, countdown=2**self.request.retries * 60)

    except Exception as exc:
        is_final_retry = self.request.retries >= self.max_retries
        update_task(
            db,
            task_id,
            owner_id,
            "failed" if is_final_retry else "processing",
            0,
            "retrying",
            str(exc),
            error=str(exc),
        )
        update_user_paper(
            db, user_paper_id, "failed" if is_final_retry else "processing"
        )

        if is_final_retry:
            publish_task_status(
                owner_id,
                {
                    "event": "import_failed",
                    "task_id": task_id,
                    "paper_id": paper_id,
                    "status": "failed",
                    "error": str(exc),
                },
            )
        raise self.retry(exc=exc)

    finally:
        db.close()
