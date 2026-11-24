from fastapi import APIRouter

from app.core.config import settings

from .admin import router as admin_router
from .assets import router as assets_router
from .auth import router as auth_router
from .users import router as users_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(assets_router)
