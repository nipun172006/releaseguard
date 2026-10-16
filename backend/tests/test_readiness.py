from types import SimpleNamespace

import pytest

from app.models.enums import ReleaseEnvironment, ReleaseStatus, RiskLevel
from app.services.readiness import assess_release


def release_subject(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "environment": ReleaseEnvironment.PRODUCTION,
        "status": ReleaseStatus.DRAFT,
        "tests_passed": False,
        "security_scan_passed": False,
        "approval_received": False,
        "backup_confirmed": False,
        "rollback_plan_ready": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("subject", "score", "risk", "is_ready"),
    [
        (release_subject(), 0, RiskLevel.CRITICAL, False),
        (
            release_subject(
                tests_passed=True,
                security_scan_passed=True,
                rollback_plan_ready=True,
            ),
            65,
            RiskLevel.HIGH,
            False,
        ),
        (
            release_subject(
                environment=ReleaseEnvironment.DEVELOPMENT,
                tests_passed=True,
                security_scan_passed=True,
                rollback_plan_ready=True,
            ),
            65,
            RiskLevel.HIGH,
            True,
        ),
        (
            release_subject(
                environment=ReleaseEnvironment.STAGING,
                tests_passed=True,
                security_scan_passed=True,
                approval_received=True,
                backup_confirmed=True,
            ),
            85,
            RiskLevel.MEDIUM,
            False,
        ),
        (
            release_subject(
                tests_passed=True,
                security_scan_passed=True,
                approval_received=True,
                backup_confirmed=True,
                rollback_plan_ready=True,
            ),
            100,
            RiskLevel.LOW,
            True,
        ),
        (
            release_subject(
                status=ReleaseStatus.FAILED,
                tests_passed=True,
                security_scan_passed=True,
                approval_received=True,
                backup_confirmed=True,
                rollback_plan_ready=True,
            ),
            100,
            RiskLevel.CRITICAL,
            True,
        ),
    ],
)
def test_readiness_score_risk_and_gate(
    subject: SimpleNamespace,
    score: int,
    risk: RiskLevel,
    is_ready: bool,
) -> None:
    assessment = assess_release(subject)

    assert assessment.readiness_score == score
    assert assessment.risk_level == risk
    assert assessment.is_ready is is_ready


def test_production_blockers_explain_every_missing_requirement() -> None:
    assessment = assess_release(release_subject())

    assert assessment.required_checks == [
        "tests_passed",
        "security_scan_passed",
        "rollback_plan_ready",
        "approval_received",
        "backup_confirmed",
    ]
    assert assessment.completed_checks == []
    assert len(assessment.blockers) == 5
    assert assessment.blockers[0] == (
        "Automated tests must be completed before a production release can advance."
    )
