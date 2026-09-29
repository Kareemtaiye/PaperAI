from fastapi import FastAPI
from app.core.config import settings
from app.exceptions.handlers import register_exception_handler
from app.midelewares.request_log import regoister_middleware
from app.routers import auth, paper, paper_import, task, websocket
from contextlib import asynccontextmanager
from app.services.pubsub import pubsub_manager

app = FastAPI(title=settings.app_name, debug=settings.debug)
register_exception_handler(app)
regoister_middleware(app)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield
#     await pubsub_manager.close()


# app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
# register_exception_handler(app)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(paper_import.router, prefix="/api/v1")
app.include_router(paper.router, prefix="/api/v1")
app.include_router(task.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")
