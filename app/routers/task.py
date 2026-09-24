from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.schemas.response import ErrorResponse
from app.schemas.task import TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/task", tags=["Task"])
service = TaskService()


@router.get("/{task_id}")
async def get_task(
    task_id: str, db=Depends(get_db), current_user=Depends(get_current_user)
):
    task = await service.find_task_by_id(
        db=db, user_id=current_user.id, task_id=task_id
    )

    return JSONResponse(
        jsonable_encoder(
            {"status": "success", "data": TaskResponse.model_validate(task)}
        )
    )
