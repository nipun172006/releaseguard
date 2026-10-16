"""Create the releases table.

Revision ID: 20261016_0001
Revises:
Create Date: 2026-10-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20261016_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "releases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column(
            "environment",
            sa.Enum(
                "DEVELOPMENT",
                "STAGING",
                "PRODUCTION",
                name="release_environment",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("owner", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "READY",
                "DEPLOYING",
                "SUCCESS",
                "FAILED",
                "ROLLED_BACK",
                name="release_status",
                native_enum=False,
                create_constraint=True,
            ),
            server_default="DRAFT",
            nullable=False,
        ),
        sa.Column("tests_passed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "security_scan_passed",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column(
            "approval_received",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column(
            "backup_confirmed",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column(
            "rollback_plan_ready",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("deployment_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(application_name)) > 0",
            name="ck_releases_application_name_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(version)) > 0",
            name="ck_releases_version_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(owner)) > 0",
            name="ck_releases_owner_not_blank",
        ),
        sa.UniqueConstraint(
            "application_name",
            "version",
            "environment",
            name="uq_releases_application_version_environment",
        ),
    )
    op.create_index("ix_releases_environment", "releases", ["environment"])
    op.create_index("ix_releases_status", "releases", ["status"])


def downgrade() -> None:
    op.drop_index("ix_releases_status", table_name="releases")
    op.drop_index("ix_releases_environment", table_name="releases")
    op.drop_table("releases")
