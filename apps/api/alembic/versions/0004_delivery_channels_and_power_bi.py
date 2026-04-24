"""add delivery channels and power bi references

Revision ID: 0004_delivery_channels_and_power_bi
Revises: 0003_microsoft_connectors_and_jobs
Create Date: 2026-04-24 20:10:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_delivery_channels_and_power_bi"
down_revision = "0003_microsoft_connectors_and_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "reports",
        sa.Column("power_bi_report_ids", sa.JSON(), nullable=False, server_default="[]"),
    )

    op.create_table(
        "power_bi_report_references",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("workspace_name", sa.String(length=255), nullable=True),
        sa.Column("workspace_id", sa.String(length=255), nullable=True),
        sa.Column("report_id", sa.String(length=255), nullable=True),
        sa.Column("report_url", sa.String(length=1024), nullable=False),
        sa.Column("embed_url", sa.String(length=1024), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "teams_channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("channel_label", sa.String(length=255), nullable=True),
        sa.Column(
            "delivery_type",
            sa.Enum("WEBHOOK", "PREVIEW", name="teamschanneldeliverytype", native_enum=False),
            nullable=False,
        ),
        sa.Column("webhook_url", sa.String(length=2048), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(
        op.f("ix_power_bi_report_references_created_by_id"),
        "power_bi_report_references",
        ["created_by_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_teams_channels_created_by_id"),
        "teams_channels",
        ["created_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_teams_channels_created_by_id"), table_name="teams_channels")
    op.drop_index(
        op.f("ix_power_bi_report_references_created_by_id"),
        table_name="power_bi_report_references",
    )
    op.drop_table("teams_channels")
    op.drop_table("power_bi_report_references")
    op.drop_column("reports", "power_bi_report_ids")
