"""add microsoft connectors and background jobs

Revision ID: 0003_microsoft_connectors_and_jobs
Revises: 0002_microsoft_identity
Create Date: 2026-04-24 17:20:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_microsoft_connectors_and_jobs"
down_revision = "0002_microsoft_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "background_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "job_type",
            sa.Enum(
                "CONNECTOR_SYNC",
                "INCREMENTAL_REINDEX",
                "SUMMARY_DELIVERY",
                "NOTIFICATION",
                name="backgroundjobtype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "QUEUED",
                "RUNNING",
                "SUCCEEDED",
                "FAILED",
                name="backgroundjobstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=True),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_background_jobs_created_by_id"), "background_jobs", ["created_by_id"], unique=False)
    op.create_index(op.f("ix_background_jobs_job_type"), "background_jobs", ["job_type"], unique=False)
    op.create_index(op.f("ix_background_jobs_resource_id"), "background_jobs", ["resource_id"], unique=False)
    op.create_index(op.f("ix_background_jobs_resource_type"), "background_jobs", ["resource_type"], unique=False)
    op.create_index(op.f("ix_background_jobs_status"), "background_jobs", ["status"], unique=False)

    op.create_table(
        "microsoft_connectors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "connector_type",
            sa.Enum("SHAREPOINT", "ONEDRIVE", name="microsoftconnectortype", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("READY", "SYNCING", "ERROR", "PAUSED", name="microsoftconnectorstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("microsoft_tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sync_frequency_minutes", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("resolved_target", sa.JSON(), nullable=False),
        sa.Column("permissions_metadata", sa.JSON(), nullable=False),
        sa.Column("last_delta_link", sa.Text(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["microsoft_tenant_id"], ["microsoft_tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_microsoft_connectors_created_by_id"), "microsoft_connectors", ["created_by_id"], unique=False)
    op.create_index(op.f("ix_microsoft_connectors_microsoft_tenant_id"), "microsoft_connectors", ["microsoft_tenant_id"], unique=False)

    op.create_table(
        "microsoft_synced_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("connector_id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("last_synced_job_id", sa.Uuid(), nullable=True),
        sa.Column("external_item_id", sa.String(length=255), nullable=False),
        sa.Column("parent_external_item_id", sa.String(length=255), nullable=True),
        sa.Column("drive_id", sa.String(length=255), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("item_path", sa.String(length=1024), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("file_extension", sa.String(length=32), nullable=True),
        sa.Column("last_modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("etag", sa.String(length=255), nullable=True),
        sa.Column("ctag", sa.String(length=255), nullable=True),
        sa.Column(
            "state",
            sa.Enum("ACTIVE", "DELETED", "SKIPPED", "ERROR", name="microsoftsynceditemstate", native_enum=False),
            nullable=False,
        ),
        sa.Column("item_metadata", sa.JSON(), nullable=False),
        sa.Column("permissions_metadata", sa.JSON(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connector_id"], ["microsoft_connectors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["last_synced_job_id"], ["background_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connector_id", "external_item_id", name="uq_microsoft_synced_items_connector_item"),
    )
    op.create_index(op.f("ix_microsoft_synced_items_connector_id"), "microsoft_synced_items", ["connector_id"], unique=False)
    op.create_index(op.f("ix_microsoft_synced_items_document_id"), "microsoft_synced_items", ["document_id"], unique=False)
    op.create_index(op.f("ix_microsoft_synced_items_drive_id"), "microsoft_synced_items", ["drive_id"], unique=False)
    op.create_index(op.f("ix_microsoft_synced_items_external_item_id"), "microsoft_synced_items", ["external_item_id"], unique=False)
    op.create_index(op.f("ix_microsoft_synced_items_last_synced_job_id"), "microsoft_synced_items", ["last_synced_job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_microsoft_synced_items_last_synced_job_id"), table_name="microsoft_synced_items")
    op.drop_index(op.f("ix_microsoft_synced_items_external_item_id"), table_name="microsoft_synced_items")
    op.drop_index(op.f("ix_microsoft_synced_items_drive_id"), table_name="microsoft_synced_items")
    op.drop_index(op.f("ix_microsoft_synced_items_document_id"), table_name="microsoft_synced_items")
    op.drop_index(op.f("ix_microsoft_synced_items_connector_id"), table_name="microsoft_synced_items")
    op.drop_table("microsoft_synced_items")

    op.drop_index(op.f("ix_microsoft_connectors_microsoft_tenant_id"), table_name="microsoft_connectors")
    op.drop_index(op.f("ix_microsoft_connectors_created_by_id"), table_name="microsoft_connectors")
    op.drop_table("microsoft_connectors")

    op.drop_index(op.f("ix_background_jobs_status"), table_name="background_jobs")
    op.drop_index(op.f("ix_background_jobs_resource_type"), table_name="background_jobs")
    op.drop_index(op.f("ix_background_jobs_resource_id"), table_name="background_jobs")
    op.drop_index(op.f("ix_background_jobs_job_type"), table_name="background_jobs")
    op.drop_index(op.f("ix_background_jobs_created_by_id"), table_name="background_jobs")
    op.drop_table("background_jobs")
