from dataclasses import dataclass
from typing import Protocol

from app.models.enums import ReleaseEnvironment, ReleaseStatus, RiskLevel


class ReadinessSubject(Protocol):
    environment: ReleaseEnvironment
    status: ReleaseStatus
    tests_passed: bool
    security_scan_passed: bool
    approval_received: bool
    backup_confirmed: bool
    rollback_plan_ready: bool


@dataclass(frozen=True)
class CheckDefinition:
    label: str
    weight: int


@dataclass(frozen=True)
class ReadinessAssessment:
    readiness_score: int
    risk_level: RiskLevel
    required_checks: list[str]
    completed_checks: list[str]
    blockers: list[str]
    is_ready: bool


CHECKS: dict[str, CheckDefinition] = {
    "tests_passed": CheckDefinition("Automated tests", 25),
    "security_scan_passed": CheckDefinition("Security scan", 25),
    "approval_received": CheckDefinition("Deployment approval", 20),
    "backup_confirmed": CheckDefinition("Backup confirmation", 15),
    "rollback_plan_ready": CheckDefinition("Rollback plan", 15),
}

BASE_REQUIRED_CHECKS = (
    "tests_passed",
    "security_scan_passed",
    "rollback_plan_ready",
)

PRODUCTION_REQUIRED_CHECKS = (
    *BASE_REQUIRED_CHECKS,
    "approval_received",
    "backup_confirmed",
)


def assess_release(release: ReadinessSubject) -> ReadinessAssessment:
    completed_checks = [
        check_name for check_name in CHECKS if getattr(release, check_name)
    ]
    readiness_score = sum(CHECKS[name].weight for name in completed_checks)

    if release.environment == ReleaseEnvironment.PRODUCTION:
        required_checks = list(PRODUCTION_REQUIRED_CHECKS)
    else:
        required_checks = list(BASE_REQUIRED_CHECKS)

    missing_required = [
        check_name
        for check_name in required_checks
        if not getattr(release, check_name)
    ]
    blockers = [
        f"{CHECKS[name].label} must be completed before a "
        f"{release.environment.value.lower()} release can advance."
        for name in missing_required
    ]

    production_critical_check_missing = (
        release.environment == ReleaseEnvironment.PRODUCTION
        and any(
            not getattr(release, name)
            for name in BASE_REQUIRED_CHECKS
        )
    )

    if production_critical_check_missing or release.status == ReleaseStatus.FAILED:
        risk_level = RiskLevel.CRITICAL
    elif (
        release.environment == ReleaseEnvironment.PRODUCTION
        and (
            not release.approval_received
            or not release.backup_confirmed
        )
    ) or readiness_score < 70:
        risk_level = RiskLevel.HIGH
    elif readiness_score < 100:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    return ReadinessAssessment(
        readiness_score=readiness_score,
        risk_level=risk_level,
        required_checks=required_checks,
        completed_checks=completed_checks,
        blockers=blockers,
        is_ready=not blockers,
    )
