import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.seed import run_seed
from app.db.database import dispose_engine
from app.routers import router as api_router

logging.basicConfig(
    level=settings.logging.level,
    format=settings.logging.format,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_seed()
    yield
    await dispose_engine()


main_app = FastAPI(
    title="DAM API",
    version="0.1.0",
    lifespan=lifespan,
)


main_app.include_router(
    api_router,
)


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@main_app.get("/health")
async def health():
    return {"status": "ok"}
