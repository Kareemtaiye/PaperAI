from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import generate_access_token, generate_refresh_token, hash_token
from app.db.session import get_db
from app.dependencies.user import get_current_user
from app.schemas.auth import LoginInput, RegisterInput, UserResponse
from app.schemas.response import ErrorResponse
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

service = AuthService()
token_service = TokenService()

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, response_model_exclude_none=True)
async def create_user(user: RegisterInput, db=Depends(get_db)):
    user = await service.register(db=db, user=user)

    return {"status": "success", "data": user}


@router.post("/token")
async def token(
    response: Response,
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
            detail=ErrorResponse(
                status="error",
                message="Invalid credentials",
                code=status.HTTP_400_BAD_REQUEST,
            ),
        )

    access_token, refresh_token = token_data
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=604800,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def rotate_refresh_token(
    response: Response, refresh_token: str = Cookie(), db=Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                status="error",
                code=status.HTTP_401_UNAUTHORIZED,
                message="No refresh token provided",
            ),
        )

    token = await token_service.get_refresh_token_by_token(
        db=db, token=hash_token(refresh_token)
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                status="error",
                code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid Refresh token",
            ),
        )

    # Detecting token replay
    if token.revoked:
        await token_service.revoke_user_refresh_tokens(db=db, user_id=token.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                status="error",
                message="Security alert. Please log in again",
                code=status.HTTP_401_UNAUTHORIZED,
            ),
        )

    if token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                status="error",
                message="Refresh token expired",
                code=status.HTTP_401_UNAUTHORIZED,
            ),
        )

    # revoke the old token
    await token_service.revoke_refresh_token(db=db, token=token.token_hash)

    new_refresh_token = generate_refresh_token()
    new_access_token = generate_access_token(str(token.user_id))

    # rotate token
    await token_service.create_refresh_token(
        db=db,
        user_id=token.user_id,
        token_hash=token.token_hash,
        expiry=token.expires_at,
    )

    # Store in cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
        path="/",
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str = Cookie(),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not refresh_token:
        return {"message": "Already logged out"}

    await token_service.revoke_refresh_token(db=db, token=refresh_token)

    response.delete_cookie(
        key="refresh_token", httponly=True, secure=True, samesite="lax"
    )

    return {"message": "Logged out successfully"}
