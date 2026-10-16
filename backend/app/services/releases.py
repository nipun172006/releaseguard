from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ReleaseConflictError, ReleaseNotFoundError
from app.models.enums import ReleaseEnvironment, ReleaseStatus, RiskLevel
from app.models.release import Release
from app.schemas.release import (
    ReadinessResponse,
    ReleaseCreate,
    ReleaseRead,
    ReleaseStats,
    ReleaseUpdate,
)
from app.services.readiness import ReadinessAssessment, assess_release

ALLOWED_TRANSITIONS: dict[ReleaseStatus, set[ReleaseStatus]] = {
    ReleaseStatus.DRAFT: {ReleaseStatus.READY},
    ReleaseStatus.READY: {ReleaseStatus.DRAFT, ReleaseStatus.DEPLOYING},
    ReleaseStatus.DEPLOYING: {ReleaseStatus.SUCCESS, ReleaseStatus.FAILED},
    ReleaseStatus.FAILED: {ReleaseStatus.ROLLED_BACK, ReleaseStatus.DEPLOYING},
    ReleaseStatus.SUCCESS: {ReleaseStatus.ROLLED_BACK},
    ReleaseStatus.ROLLED_BACK: set(),
}


def get_release_or_raise(db: Session, release_id: int) -> Release:
    release = db.get(Release, release_id)
    if release is None:
        raise ReleaseNotFoundError(f"Release {release_id} was not found.")
    return release


def _to_release_read(release: Release) -> ReleaseRead:
    assessment = assess_release(release)
    return ReleaseRead(
        id=release.id,
        application_name=release.application_name,
        version=release.version,
        environment=release.environment,
        owner=release.owner,
        description=release.description,
        status=release.status,
        tests_passed=release.tests_passed,
        security_scan_passed=release.security_scan_passed,
        approval_received=release.approval_received,
        backup_confirmed=release.backup_confirmed,
        rollback_plan_ready=release.rollback_plan_ready,
        deployment_notes=release.deployment_notes,
        created_at=release.created_at,
        updated_at=release.updated_at,
        readiness_score=assessment.readiness_score,
        risk_level=assessment.risk_level,
        blockers=assessment.blockers,
        is_ready=assessment.is_ready,
    )


def _commit_or_conflict(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ReleaseConflictError(message) from error


def create_release(db: Session, payload: ReleaseCreate) -> ReleaseRead:
    release = Release(**payload.model_dump())
    db.add(release)
    _commit_or_conflict(
        db,
        "A release with this application, version, and environment already exists.",
    )
    db.refresh(release)
    return _to_release_read(release)


def list_releases(
    db: Session,
    *,
    status: ReleaseStatus | None = None,
    environment: ReleaseEnvironment | None = None,
    risk: RiskLevel | None = None,
    search: str | None = None,
) -> list[ReleaseRead]:
    query = select(Release)

    if status is not None:
        query = query.where(Release.status == status)
    if environment is not None:
        query = query.where(Release.environment == environment)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Release.application_name.ilike(search_term),
                Release.version.ilike(search_term),
            )
        )

    releases = db.scalars(query.order_by(Release.created_at.desc())).all()
    results = [_to_release_read(release) for release in releases]

    if risk is not None:
        results = [release for release in results if release.risk_level == risk]

    return results


def get_release(db: Session, release_id: int) -> ReleaseRead:
    return _to_release_read(get_release_or_raise(db, release_id))


def _validate_transition(
    current: ReleaseStatus,
    requested: ReleaseStatus,
    assessment: ReadinessAssessment,
) -> None:
    if requested == current:
        return

    if requested not in ALLOWED_TRANSITIONS[current]:
        raise ReleaseConflictError(
            f"Release status cannot move from {current.value} to {requested.value}."
        )

    if requested == ReleaseStatus.READY and not assessment.is_ready:
        raise ReleaseConflictError(
            "Release cannot become READY while mandatory readiness checks are missing: "
            + "; ".join(assessment.blockers)
        )

    if (
        current == ReleaseStatus.READY
        and requested == ReleaseStatus.DEPLOYING
        and not assessment.is_ready
    ):
        raise ReleaseConflictError(
            "Release cannot start deploying while mandatory readiness checks are missing."
        )


def update_release(
    db: Session,
    release_id: int,
    payload: ReleaseUpdate,
) -> ReleaseRead:
    release = get_release_or_raise(db, release_id)
    current_status = release.status
    changes = payload.model_dump(exclude_unset=True)
    requested_status = changes.pop("status", current_status)

    for field_name, value in changes.items():
        setattr(release, field_name, value)

    assessment = assess_release(release)
    _validate_transition(current_status, requested_status, assessment)

    if (
        current_status == ReleaseStatus.READY
        and requested_status == current_status
        and not assessment.is_ready
    ):
        release.status = ReleaseStatus.DRAFT
    else:
        release.status = requested_status

    _commit_or_conflict(
        db,
        "The update conflicts with an existing release or database constraint.",
    )
    db.refresh(release)
    return _to_release_read(release)


def delete_release(db: Session, release_id: int) -> None:
    release = get_release_or_raise(db, release_id)
    if release.status != ReleaseStatus.DRAFT:
        raise ReleaseConflictError("Only DRAFT releases can be deleted.")

    db.delete(release)
    db.commit()


def get_readiness(db: Session, release_id: int) -> ReadinessResponse:
    release = get_release_or_raise(db, release_id)
    assessment = assess_release(release)
    return ReadinessResponse(
        release_id=release.id,
        readiness_score=assessment.readiness_score,
        risk_level=assessment.risk_level,
        required_checks=assessment.required_checks,
        completed_checks=assessment.completed_checks,
        blockers=assessment.blockers,
        is_ready=assessment.is_ready,
    )


def get_release_stats(db: Session) -> ReleaseStats:
    releases = db.scalars(select(Release)).all()
    assessments = [assess_release(release) for release in releases]
    total = len(releases)

    return ReleaseStats(
        total_releases=total,
        ready_to_deploy=sum(
            release.status == ReleaseStatus.READY for release in releases
        ),
        active_deployments=sum(
            release.status == ReleaseStatus.DEPLOYING for release in releases
        ),
        high_or_critical_risk=sum(
            assessment.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            for assessment in assessments
        ),
        successful_deployments=sum(
            release.status == ReleaseStatus.SUCCESS for release in releases
        ),
        average_readiness_score=(
            round(
                sum(assessment.readiness_score for assessment in assessments) / total,
                2,
            )
            if total
            else 0.0
        ),
    )
