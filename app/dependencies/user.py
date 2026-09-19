from typing import Annotated

from fastapi.encoders import jsonable_encoder
from app.core.security import oauth_scheme, verify_jwt
from fastapi import Depends, HTTPException, status

from app.db.session import get_db
from app.schemas.response import ErrorResponse


async def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)], db=Depends(get_db)
):
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

    # payload = verify_jwt(token)

    # user = await
