from fastapi import APIRouter

from src.api.v1.routers.user import router as router_user
from src.api.v1.routers.console import router as router_console


router = APIRouter(prefix="/v1")

router.include_router(router_user, tags=["user"])
router.include_router(router_console, tags=["console"])
