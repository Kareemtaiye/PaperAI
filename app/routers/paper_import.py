import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.db.models.task import Task
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.schemas.import_paper import ArxivImportRequest, ArxivImportResponse
from app.schemas.response import ErrorResponse
from app.services.paper_service import PaperService
from app.services.task_service import TaskService
from app.services.user_paper_service import UserPaperService
from app.tasks.import_tasks import import_arxiv_paper
from app.utils.extract_arxiv_id import extract_arxiv_id

router = APIRouter(prefix="/paper", tags=["Paper"])
service = PaperService()
user_paper_service = UserPaperService()
task_service = TaskService()


@router.post("/import/arxiv")
async def import_paper_arxiv(
    body: ArxivImportRequest, db=Depends(get_db), current_user=Depends(get_current_user)
):
    arxiv_id = extract_arxiv_id(body.arxiv_url)
    if not arxiv_id:
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
    task = await task_service.create_task(
        db=db,
        user_id=current_user.id,
        user_paper_id=user_paper.id,
        task_type="import_arxiv",
    )

    # 4
    celery_task = import_arxiv_paper.delay(
        str(paper.id), str(user_paper.id), str(task.id), arxiv_id, str(current_user.id)
    )

    # 5
    task.celery_task_id = celery_task.id
    await db.commit()  # This is possible cos the task service returned the task as 'Task' type

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "data": ArxivImportResponse(
                paper_id=str(paper.id),
                user_paper_id=str(user_paper.id),
                task_id=str(task.id),
                celery_task_id=str(celery_task.id),
                status=str(task.status),
                message=f"Import queued. Poll /tasks/{task.id} for updates.",
            ).model_dump(),
        },
    )
