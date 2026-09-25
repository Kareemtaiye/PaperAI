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


# @router.get("/")
# async def get_all_tasks(db=Depends(get_db), current_user=Depends(get_current_user)):
#     result = await db.execute(
#         select(Task)
#         .where(Task.user_id == current_user.id)
#         .order_by(Task.created_at.desc())
#     )
#     tasks = result.scalars().all()

#     return {
#         "status": "success",
#         "data": [
#             {
#                 "task_id": str(t.id),
#                 "task_type": t.task_type,
#                 "status": t.status,
#                 "progress": t.progress,
#                 "stage_message": t.stage_message,
#                 "created_at": t.created_at,
#                 "completed_at": t.completed_at,
#             }
#             for t in tasks
#         ],
#     }
