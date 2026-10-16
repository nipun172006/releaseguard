from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.main import app


def test_root_describes_the_service(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "ReleaseGuard API",
        "message": "Ship only when the evidence says ready.",
        "documentation": "/docs",
    }


def test_health_reports_the_test_environment(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "ReleaseGuard API",
        "environment": "test",
    }


def test_metrics_exposes_prometheus_output(client: TestClient) -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "releaseguard_http_requests_total" in response.text
    assert "releaseguard_http_request_duration_seconds" in response.text


def test_ready_checks_the_real_test_database(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"api": "up", "database": "up"},
    }


def test_ready_returns_503_when_database_is_unavailable(client: TestClient) -> None:
    class UnavailableDatabase:
        def execute(self, *_args: object, **_kwargs: object) -> None:
            raise SQLAlchemyError("database offline")

    def unavailable_database() -> Generator[UnavailableDatabase, None, None]:
        yield UnavailableDatabase()

    app.dependency_overrides[get_db] = unavailable_database
    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database is unavailable."}
