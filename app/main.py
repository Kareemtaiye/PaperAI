from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
