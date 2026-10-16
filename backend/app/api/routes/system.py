from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
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


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database unavailable"}},
)
def readiness(db: Session = Depends(get_db)) -> ReadinessResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        ) from error

    return ReadinessResponse(
        status="ready",
        checks={"api": "up", "database": "up"},
    )
