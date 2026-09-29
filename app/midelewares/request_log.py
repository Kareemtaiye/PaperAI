import time
from fastapi import FastAPI, Request
from app.core.logger import logger


def regoister_middleware(app: FastAPI):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        correlation_id = request.headers.get("X-Correlation-ID", "unknown")

        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else (request.client.host if request.client else "unknown")
        )

        log_context = {
            "correlation_id": correlation_id,
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
        }

        try:
            logger.info("request started", extra=log_context)
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_context.update(
                {"status_code": response.status_code, "duration_ms": duration_ms}
            )
            logger.info("request completed", extra=log_context)
            return response

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_context.update({"status_code": 500, "duration_ms": duration_ms})
            logger.error(f"request failed: {str(e)}", extra=log_context)
            raise
