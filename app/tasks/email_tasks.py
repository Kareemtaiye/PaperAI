import resend
from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.services.email_renderer import render_email
from app.core.logger import logger

resend.api_key = settings.resend_api_key


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_import_completed_email(
    self,
    to_email: str,
    title: str,
    authors: list,
    abstract: str,
    published_at: str,
    categories: list,
    total_duration: float,
    arxiv_id: str,
):
    try:
        html = render_email(
            "import_completed.html",
            {
                "title": title,
                "authors": ", ".join(authors or []),
                "abstract": abstract or "",
                "published_at": published_at,
                "categories": ", ".join(categories or []),
                "total_duration": total_duration,
                "arxiv_id": arxiv_id,
                "api_url": settings.api_url,
            },
        )

        resend.Emails.send(
            {
                "from": settings.from_email,
                "to": to_email,
                "subject": f"Paper Ready: {title}",
                "html": html,
            }
        )

        logger.info(
            "import completed email sent", extra={"to": to_email, "title": title}
        )

    except Exception as exc:
        logger.error("failed to send import completed email", extra={"error": str(exc)})
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_import_failed_email(self, to_email: str, arxiv_id: str, error_message: str):
    try:
        html = render_email(
            "import_failed.html", {"arxiv_id": arxiv_id, "error_message": error_message}
        )

        resend.Emails.send(
            {
                "from": settings.from_email,
                "to": to_email,
                "subject": "Paper Import Failed",
                "html": html,
            }
        )

        logger.info("import failed email sent", extra={"to": to_email})

    except Exception as exc:
        logger.error("failed to send import failed email", extra={"error": str(exc)})
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email(self, to_email: str):
    print(">>> EMAIL TASK STARTED")

    try:
        html = render_email("welcome.html", {"api_url": settings.api_url})

        resend.Emails.send(
            {
                "from": settings.from_email,
                "to": to_email,
                "subject": "Welcome to PaperAI",
                "html": html,
            }
        )

        logger.info("welcome email sent", extra={"to": to_email})

    except Exception as exc:
        logger.error("failed to send welcome email", extra={"error": str(exc)})
        raise self.retry(exc=exc)
