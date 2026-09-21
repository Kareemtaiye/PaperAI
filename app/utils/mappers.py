from app.db.models.user_paper import UserPaper
from app.schemas.paper import PaperResponse


def build_paper_response(up: UserPaper) -> PaperResponse:
    return PaperResponse(
        id=up.paper.id,
        title=up.paper.title,
        source=up.paper.source,
        status=up.status,
        notes=up.notes,
        progress=up.progress,
        created_at=up.created_at,
        abstract=up.paper.abstract,
        authors=up.paper.authors,
        categories=up.paper.categories,
        arxiv_id=up.paper.arxiv_id,
        published_at=up.paper.published_at,
    )
