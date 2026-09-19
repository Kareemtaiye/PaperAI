from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.db.session import get_db
from app.schemas.auth import LoginInput, RegisterInput, UserResponse
from app.schemas.response import ErrorResponse
from app.services.auth_service import AuthService

service = AuthService()

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse, response_model_exclude_none=True)
async def create_user(user: RegisterInput, db=Depends(get_db)):
    user = await service.register(db=db, user=user)

    return {"status": "success", "data": user}


@router.post("/token", tags=["token"])
async def token(
    # response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    db=Depends(get_db),
):
    token_data = await service.login(
        db, LoginInput(username=form_data.username, password=form_data.password)
    )

    if not token_data:
        # logger warning
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=jsonable_encoder(
                ErrorResponse(
                    status="error",
                    message="Invalid credentials",
                    code=status.HTTP_400_BAD_REQUEST,
                )
            ),
        )

    return {
        "status": "success",
        "data": {"access_token": token_data, "token_type": "bearer"},
    }


@router.post("/refresh", tags=["refresh"])
async def refresh(): ...


@router.post("/logout", tags="logout")
async def logout(): ...
