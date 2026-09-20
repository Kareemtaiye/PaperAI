from typing import Annotated

from fastapi.encoders import jsonable_encoder
from app.core.security import oauth_scheme, verify_jwt
from fastapi import Depends, HTTPException, status

from app.db.session import get_db
from app.schemas.auth import UserOuput
from app.schemas.response import ErrorResponse
from app.services.user_service import UserService

service = UserService()


async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)], db=Depends(get_db)
) -> UserOuput:

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=jsonable_encoder(
                ErrorResponse(
                    status="error",
                    code=status.HTTP_401_UNAUTHORIZED,
                    message="Not authenticated",
                )
            ),
        )

    payload = verify_jwt(token)

    user = await service.find_user_by_id(db, payload.get("sub"))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=jsonable_encoder(
                ErrorResponse(
                    status="error",
                    code=status.HTTP_400_BAD_REQUEST,
                    message="Invalid access token",
                )
            ),
        )

    return user
