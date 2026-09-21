from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.schemas import paper
from app.schemas.paper import PaperManualCreate, PaperResponse
from app.schemas.response import ErrorResponse
from app.services.paper_service import PaperService
from app.utils.mappers import build_paper_response

router = APIRouter(prefix="/paper", tags=["Paper"])
service = PaperService()


@router.post("/manual", response_model=PaperResponse)
async def create_paper_manual(
    data: PaperManualCreate, db=Depends(get_db), current_user=Depends(get_current_user)
):
    paper, user_paper = await service.create_paper_manual(
        db=db, title=data.title, user_id=current_user.id
    )

    res_data = PaperResponse(
        id=paper.id,
        title=paper.title,
        source=paper.source,
        status=user_paper.status,
        notes=user_paper.notes,
        progress=user_paper.progress,
        created_at=user_paper.created_at,
        abstract=None,
        authors=None,
        categories=None,
        arxiv_id=None,
        published_at=None,
    )
    return JSONResponse(jsonable_encoder({"status": "success", "data": res_data}))


@router.get("/", response_model=list[PaperResponse])
async def get_all_user_papers(
    db=Depends(get_db), current_user=Depends(get_current_user)
):
    user_papers = await service.get_all_user_papers(db=db, user_id=current_user.id)

    data = [build_paper_response(paper) for paper in user_papers]
    return JSONResponse(jsonable_encoder({"status": "success", "data": data}))


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_user_paper(
    paper_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_paper = await service.get_user_paper(
        db=db, user_id=current_user.id, paper_id=paper_id
    )

    return JSONResponse(
        jsonable_encoder(
            {"status": "success", "data": build_paper_response(user_paper)}
        )
    )


@router.delete("/{paper_id}", response_model=PaperResponse)
async def delete_user_paper(
    paper_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    Paper = await service.delete_user_paper(
        db=db, user_id=current_user.id, paper_id=paper_id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
