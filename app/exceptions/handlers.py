from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# from app.core.logger import logger
from app.exceptions.resource_not_found import ResourceNotFoundException
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

    @app.exception_handler(ResourceNotFoundException)
    def resource_not_found_exc_handler(
        request: Request, exc: ResourceNotFoundException
    ):

        # logger.error(
        #     f"{exc.name} not found: {exc.resource_id} | Path: {request.url.path} - {request.method}"
        # )

        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(
                ErrorResponse(
                    status="error",
                    code=404,
                    message=f"{exc.name} with id_ {exc.resource_id} does not exist",
                    # message=f"Paper with id_ {exc} does not exist",
                ),
            ),
        )
