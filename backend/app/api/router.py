from fastapi import APIRouter

from app.api.routes import releases, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(releases.router)
