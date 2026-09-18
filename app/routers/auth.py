from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.schemas.auth import RegisterInput, UserResponse
from app.services.auth_service import AuthService

service = AuthService()

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse, response_model_exclude_none=True)
async def create_user(user: RegisterInput, db=Depends(get_db)):
    user = await service.register(db=db, user=user)

    return {"status": "success", "data": user}


@router.post("/token", tags=["token"])
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
): ...


# if not form_data.username or
