from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

PayloadFactory = Callable[..., dict[str, Any]]


def create_release(
    client: TestClient,
    release_payload: PayloadFactory,
    **overrides: Any,
) -> dict[str, Any]:
    response = client.post("/api/releases", json=release_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def complete_checks() -> dict[str, bool]:
    return {
        "tests_passed": True,
        "security_scan_passed": True,
        "approval_received": True,
        "backup_confirmed": True,
        "rollback_plan_ready": True,
    }


def test_create_release_returns_computed_readiness(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    response = client.post("/api/releases", json=release_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["application_name"] == "payments-api"
    assert body["status"] == "DRAFT"
    assert body["readiness_score"] == 0
    assert body["risk_level"] == "CRITICAL"
    assert body["is_ready"] is False
    assert len(body["blockers"]) == 5
    assert body["created_at"]
    assert body["updated_at"]


def test_list_supports_search_environment_and_computed_risk_filters(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    create_release(client, release_payload)
    create_release(
        client,
        release_payload,
        application_name="catalog-web",
        version="2.0.0",
        environment="STAGING",
        **complete_checks(),
    )

    response = client.get(
        "/api/releases",
        params={
            "search": "PAYMENTS",
            "environment": "PRODUCTION",
            "risk": "CRITICAL",
        },
    )

    assert response.status_code == 200
    releases = response.json()
    assert len(releases) == 1
    assert releases[0]["application_name"] == "payments-api"


def test_get_unknown_release_returns_404(client: TestClient) -> None:
    response = client.get("/api/releases/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Release 999999 was not found."}


def test_invalid_payload_returns_422(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    blank_name = client.post(
        "/api/releases",
        json=release_payload(application_name="   "),
    )
    invalid_environment = client.post(
        "/api/releases",
        json=release_payload(environment="QA"),
    )

    assert blank_name.status_code == 422
    assert invalid_environment.status_code == 422


def test_duplicate_application_version_and_environment_returns_409(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    create_release(client, release_payload)

    duplicate = client.post("/api/releases", json=release_payload())

    assert duplicate.status_code == 409
    assert duplicate.json() == {
        "detail": (
            "A release with this application, version, and environment "
            "already exists."
        )
    }


def test_release_cannot_be_ready_with_missing_mandatory_checks(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    release = create_release(client, release_payload)

    response = client.put(
        f"/api/releases/{release['id']}",
        json={"status": "READY"},
    )

    assert response.status_code == 409
    assert "mandatory readiness checks are missing" in response.json()["detail"]


def test_valid_lifecycle_can_reach_success_and_reject_reverse_transition(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    release = create_release(client, release_payload, **complete_checks())
    release_id = release["id"]

    for expected_status in ("READY", "DEPLOYING", "SUCCESS"):
        response = client.put(
            f"/api/releases/{release_id}",
            json={"status": expected_status},
        )
        assert response.status_code == 200
        assert response.json()["status"] == expected_status

    reverse = client.put(
        f"/api/releases/{release_id}",
        json={"status": "DEPLOYING"},
    )
    assert reverse.status_code == 409
    assert reverse.json() == {
        "detail": "Release status cannot move from SUCCESS to DEPLOYING."
    }


def test_removing_required_evidence_demotes_ready_release_to_draft(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    release = create_release(client, release_payload, **complete_checks())
    release_id = release["id"]
    ready = client.put(
        f"/api/releases/{release_id}",
        json={"status": "READY"},
    )
    assert ready.status_code == 200

    response = client.put(
        f"/api/releases/{release_id}",
        json={"security_scan_passed": False},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "DRAFT"
    assert response.json()["risk_level"] == "CRITICAL"
    assert response.json()["is_ready"] is False


def test_only_draft_releases_can_be_deleted(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    draft = create_release(client, release_payload)
    deleted = client.delete(f"/api/releases/{draft['id']}")
    missing = client.get(f"/api/releases/{draft['id']}")

    active = create_release(
        client,
        release_payload,
        version="2.0.0",
        **complete_checks(),
    )
    client.put(f"/api/releases/{active['id']}", json={"status": "READY"})
    refused = client.delete(f"/api/releases/{active['id']}")

    assert deleted.status_code == 204
    assert missing.status_code == 404
    assert refused.status_code == 409
    assert refused.json() == {"detail": "Only DRAFT releases can be deleted."}


def test_readiness_endpoint_exposes_evidence_and_blockers(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    release = create_release(
        client,
        release_payload,
        tests_passed=True,
        security_scan_passed=True,
    )

    response = client.get(f"/api/releases/{release['id']}/readiness")

    assert response.status_code == 200
    assert response.json() == {
        "release_id": release["id"],
        "readiness_score": 50,
        "risk_level": "CRITICAL",
        "required_checks": [
            "tests_passed",
            "security_scan_passed",
            "rollback_plan_ready",
            "approval_received",
            "backup_confirmed",
        ],
        "completed_checks": ["tests_passed", "security_scan_passed"],
        "blockers": [
            "Rollback plan must be completed before a production release can advance.",
            "Deployment approval must be completed before a production release can advance.",
            "Backup confirmation must be completed before a production release can advance.",
        ],
        "is_ready": False,
    }


def test_stats_aggregate_release_states_and_scores(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    create_release(client, release_payload)
    ready = create_release(
        client,
        release_payload,
        application_name="catalog-api",
        version="2.0.0",
        **complete_checks(),
    )
    client.put(f"/api/releases/{ready['id']}", json={"status": "READY"})

    deploying = create_release(
        client,
        release_payload,
        application_name="identity-api",
        version="3.0.0",
        environment="DEVELOPMENT",
        **complete_checks(),
    )
    client.put(f"/api/releases/{deploying['id']}", json={"status": "READY"})
    client.put(f"/api/releases/{deploying['id']}", json={"status": "DEPLOYING"})

    response = client.get("/api/releases/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_releases": 3,
        "ready_to_deploy": 1,
        "active_deployments": 1,
        "high_or_critical_risk": 1,
        "successful_deployments": 0,
        "average_readiness_score": 66.67,
    }


def test_update_rejects_explicit_null_for_required_fields(
    client: TestClient,
    release_payload: PayloadFactory,
) -> None:
    release = create_release(client, release_payload)

    response = client.put(
        f"/api/releases/{release['id']}",
        json={"owner": None},
    )

    assert response.status_code == 422
