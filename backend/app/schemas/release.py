from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ReleaseEnvironment, ReleaseStatus, RiskLevel


class ReleaseBase(BaseModel):
    application_name: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=50)
    environment: ReleaseEnvironment
    owner: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    tests_passed: bool = False
    security_scan_passed: bool = False
    approval_received: bool = False
    backup_confirmed: bool = False
    rollback_plan_ready: bool = False
    deployment_notes: str | None = Field(default=None, max_length=4000)

    @field_validator("application_name", "version", "owner", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class ReleaseCreate(ReleaseBase):
    pass


class ReleaseUpdate(BaseModel):
    application_name: str | None = Field(default=None, min_length=1, max_length=120)
    version: str | None = Field(default=None, min_length=1, max_length=50)
    environment: ReleaseEnvironment | None = None
    owner: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: ReleaseStatus | None = None
    tests_passed: bool | None = None
    security_scan_passed: bool | None = None
    approval_received: bool | None = None
    backup_confirmed: bool | None = None
    rollback_plan_ready: bool | None = None
    deployment_notes: str | None = Field(default=None, max_length=4000)

    @field_validator("application_name", "version", "owner", mode="before")
    @classmethod
    def validate_required_update_text(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field cannot be null when supplied")
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("environment", "status", mode="before")
    @classmethod
    def validate_required_update_enum(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field cannot be null when supplied")
        return value

    @field_validator(
        "tests_passed",
        "security_scan_passed",
        "approval_received",
        "backup_confirmed",
        "rollback_plan_ready",
        mode="before",
    )
    @classmethod
    def validate_update_boolean(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field cannot be null when supplied")
        return value


class ReadinessResponse(BaseModel):
    release_id: int
    readiness_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    required_checks: list[str]
    completed_checks: list[str]
    blockers: list[str]
    is_ready: bool


class ReleaseRead(ReleaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ReleaseStatus
    created_at: datetime
    updated_at: datetime
    readiness_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    blockers: list[str]
    is_ready: bool


class ReleaseStats(BaseModel):
    total_releases: int
    ready_to_deploy: int
    active_deployments: int
    high_or_critical_risk: int
    successful_deployments: int
    average_readiness_score: float
