from fastapi import FastAPI
from app.core.config import settings
from app.exceptions.handlers import register_exception_handler
from app.routers import auth, paper

app = FastAPI(title=settings.app_name, debug=settings.debug)
register_exception_handler(app)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(paper.router, prefix="/api/v1")
