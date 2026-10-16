from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import ReleaseEnvironment, ReleaseStatus, RiskLevel
from app.schemas.release import (
    ReadinessResponse,
    ReleaseCreate,
    ReleaseRead,
    ReleaseStats,
    ReleaseUpdate,
)
from app.services import releases as release_service

router = APIRouter(prefix="/api/releases", tags=["releases"])


@router.get("", response_model=list[ReleaseRead])
def list_release_records(
    release_status: ReleaseStatus | None = Query(default=None, alias="status"),
    environment: ReleaseEnvironment | None = None,
    risk: RiskLevel | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=120),
    db: Session = Depends(get_db),
) -> list[ReleaseRead]:
    return release_service.list_releases(
        db,
        status=release_status,
        environment=environment,
        risk=risk,
        search=search,
    )


@router.post("", response_model=ReleaseRead, status_code=status.HTTP_201_CREATED)
def create_release_record(
    payload: ReleaseCreate,
    db: Session = Depends(get_db),
) -> ReleaseRead:
    return release_service.create_release(db, payload)


@router.get("/stats", response_model=ReleaseStats)
def get_release_statistics(db: Session = Depends(get_db)) -> ReleaseStats:
    return release_service.get_release_stats(db)


@router.get("/{release_id}/readiness", response_model=ReadinessResponse)
def get_release_readiness(
    release_id: int,
    db: Session = Depends(get_db),
) -> ReadinessResponse:
    return release_service.get_readiness(db, release_id)


@router.get("/{release_id}", response_model=ReleaseRead)
def get_release_record(
    release_id: int,
    db: Session = Depends(get_db),
) -> ReleaseRead:
    return release_service.get_release(db, release_id)


@router.put("/{release_id}", response_model=ReleaseRead)
def update_release_record(
    release_id: int,
    payload: ReleaseUpdate,
    db: Session = Depends(get_db),
) -> ReleaseRead:
    return release_service.update_release(db, release_id, payload)


@router.delete("/{release_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_release_record(
    release_id: int,
    db: Session = Depends(get_db),
) -> Response:
    release_service.delete_release(db, release_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
