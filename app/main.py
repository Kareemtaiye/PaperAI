from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(auth.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
