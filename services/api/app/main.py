import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.database import db_helper

logging.basicConfig(
    level=settings.logging.level,
    format=settings.logging.format,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startapp
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    title="DAM API",
    version="0.1.0",
    lifespan=lifespan,
)


@main_app.get("/health")
async def health():
    return {"status": "ok"}
