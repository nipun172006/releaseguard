from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.system import HealthResponse, ReadinessResponse, RootResponse

router = APIRouter(tags=["system"])


@router.get("/", response_model=RootResponse)
async def root(settings: Settings = Depends(get_settings)) -> RootResponse:
    return RootResponse(
        service=settings.app_name,
        message="Ship only when the evidence says ready.",
        documentation="/docs",
    )


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    return ReadinessResponse(status="ready", checks={"api": "up"})
