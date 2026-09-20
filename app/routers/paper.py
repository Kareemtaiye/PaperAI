from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.schemas.paper import PaperManualCreate, PaperResponse
from app.schemas.response import ErrorResponse
from app.services.paper_service import PaperService

router = APIRouter(prefix="/paper", tags=["Paper"])
service = PaperService()


@router.post("/manual")
async def create_paper_manual(
    data: PaperManualCreate, db=Depends(get_db), current_user=Depends(get_current_user)
):
    if not data.title:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(status="error", code=401, message="No title provided"),
        )

    paper, user_paper = await service.create_paper_manual(
        db=db, title=data.title, user_id=current_user.id
    )

    return PaperResponse(
        id=paper.id,
        title=paper.title,
        source=paper.source,
        status=user_paper.status,
        notes=user_paper.notes,
        progress=user_paper.progress,
        created_at=user_paper.created_at,
        # rest of fields null for manual paper
        abstract=None,
        authors=None,
        categories=None,
        arxiv_id=None,
        published_at=None,
    )
