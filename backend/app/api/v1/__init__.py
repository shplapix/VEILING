from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.lots import router as lots_router
from app.api.v1.ws import router as ws_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(lots_router)
api_v1_router.include_router(ws_router)

__all__ = ["api_v1_router"]
