import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.schemas.import_paper import ArxivImportRequest
from app.schemas.response import ErrorResponse
from app.services.paper_service import PaperService
from app.services.user_paper_service import UserPaperService
from app.utils.extract_arxiv_id import extract_arxiv_id

router = APIRouter(prefix="paper")
service = PaperService()
user_paper_service = UserPaperService()


@router.post("/import/arxiv")
async def import_arxiv_paper(
    body: ArxivImportRequest, db=Depends(get_db), current_user=Depends(get_current_user)
):
    arxiv_id = extract_arxiv_id(body.arxiv_url)
    if arxiv_id:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                status="error", code=400, message="Invalid Arxiv url or ID"
            ),
        )

    arxiv_url = (
        f"https://arxiv.org/abs/{arxiv_id}"
        if re.match(r"^\d{4}\.\d{4,5}$", body.arxiv_url.strip())
        else body.arxiv_url
    )

    # 1
    paper = await service.create_paper_import(
        db=db, source_id=arxiv_id, source_url=arxiv_url, source="arxiv"
    )
    # 2
    try:
        user_paper = await user_paper_service.create_user_paper(
            db=db, user_id=current_user.id, paper_id=paper.id, status="pending"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                status="error", code=409, message="You have already imported this paper"
            ),
        )

    # 3
