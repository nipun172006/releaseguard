from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ReleaseEnvironment, ReleaseStatus


class Release(Base):
    __tablename__ = "releases"
    __table_args__ = (
        CheckConstraint(
            "length(trim(application_name)) > 0",
            name="ck_releases_application_name_not_blank",
        ),
        CheckConstraint(
            "length(trim(version)) > 0",
            name="ck_releases_version_not_blank",
        ),
        CheckConstraint(
            "length(trim(owner)) > 0",
            name="ck_releases_owner_not_blank",
        ),
        UniqueConstraint(
            "application_name",
            "version",
            "environment",
            name="uq_releases_application_version_environment",
        ),
        Index("ix_releases_status", "status"),
        Index("ix_releases_environment", "environment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    application_name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    environment: Mapped[ReleaseEnvironment] = mapped_column(
        SqlEnum(
            ReleaseEnvironment,
            name="release_environment",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    owner: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReleaseStatus] = mapped_column(
        SqlEnum(
            ReleaseStatus,
            name="release_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=ReleaseStatus.DRAFT,
        server_default=ReleaseStatus.DRAFT.value,
    )
    tests_passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    security_scan_passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    approval_received: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    backup_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    rollback_plan_ready: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    deployment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
