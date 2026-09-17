from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.schemas.auth import RegisterInput
from app.services.auth_service import AuthService

service = AuthService()

router = APIRouter(prefix="/auth")


@router.post("/register")
async def create_user(user: RegisterInput, db=Depends(get_db)):
    user = await service.register(db=db, user=user)

    return {"data": "created"}


@router.post("/token", tags=["token"])
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
): ...


# if not form_data.username or
