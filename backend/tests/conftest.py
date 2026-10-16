import os
from collections.abc import Callable, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

test_database_url = os.environ.get("RELEASEGUARD_TEST_DATABASE_URL")
if test_database_url is None:
    raise RuntimeError(
        "RELEASEGUARD_TEST_DATABASE_URL must point to an isolated PostgreSQL "
        "database whose name ends with '_test'."
    )

database_name = make_url(test_database_url).database or ""
if not database_name.endswith("_test"):
    raise RuntimeError(
        "Refusing to run tests because RELEASEGUARD_TEST_DATABASE_URL does not "
        "use a database whose name ends with '_test'."
    )

# Settings are created while application modules are imported, so the isolated
# URL and test environment must be present before those imports happen.
os.environ["RELEASEGUARD_DATABASE_URL"] = test_database_url
os.environ["RELEASEGUARD_ENVIRONMENT"] = "test"

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Release  # noqa: E402, F401

test_engine = create_engine(test_database_url, pool_pre_ping=True)


@pytest.fixture(scope="session", autouse=True)
def database_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    outer_transaction = connection.begin()
    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def release_payload() -> Callable[..., dict[str, Any]]:
    def factory(**overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "application_name": "payments-api",
            "version": "1.0.0",
            "environment": "PRODUCTION",
            "owner": "Platform Team",
            "description": "Production release candidate",
            "tests_passed": False,
            "security_scan_passed": False,
            "approval_received": False,
            "backup_confirmed": False,
            "rollback_plan_ready": False,
            "deployment_notes": None,
        }
        payload.update(overrides)
        return payload

    return factory
