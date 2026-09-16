from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from h11 import Response

router = APIRouter(prefix="/auth")


@router.get("/register")
async def create_user(): ...


@router.post("/token", tags=["token"])
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
): ...


# if not form_data.username or
