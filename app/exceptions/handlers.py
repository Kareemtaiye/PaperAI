from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import ErrorResponse


def register_exception_handler(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    def http_exception_handler(request: Request, exc: StarletteHTTPException):
        detail = exc.detail

        if isinstance(detail, ErrorResponse):
            content = jsonable_encoder(detail)
        elif isinstance(detail, dict) and "message" in detail:
            content = jsonable_encoder(
                ErrorResponse(
                    status=detail.get("status", "error"),
                    code=detail.get("code", exc.status_code),
                    message=str(detail["message"]),
                    details=detail.get("detail"),
                )
            )
        else:
            content = jsonable_encoder(
                ErrorResponse(
                    status="error",
                    code=exc.status_code,
                    message=str(detail),
                )
            )

        return JSONResponse(status_code=exc.status_code, content=content)
