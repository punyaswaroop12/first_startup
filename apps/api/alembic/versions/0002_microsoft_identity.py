"""add microsoft identity scaffolding

Revision ID: 0002_microsoft_identity
Revises: 0001_initial_schema
Create Date: 2026-04-24 15:30:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_microsoft_identity"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "hashed_password", existing_type=sa.String(length=255), nullable=True)

    op.create_table(
        "microsoft_tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("primary_domain", sa.String(length=255), nullable=True),
        sa.Column("tenant_metadata", sa.JSON(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_microsoft_tenants_tenant_id"),
        "microsoft_tenants",
        ["tenant_id"],
        unique=True,
    )

    op.create_table(
        "user_identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "provider",
            sa.Enum("MICROSOFT", name="identityprovider", native_enum=False),
            nullable=False,
        ),
        sa.Column("provider_subject", sa.String(length=255), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=False),
        sa.Column("provider_display_name", sa.String(length=255), nullable=True),
        sa.Column("microsoft_tenant_id", sa.Uuid(), nullable=True),
        sa.Column("claims", sa.JSON(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["microsoft_tenant_id"], ["microsoft_tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_user_identities_provider_subject"),
    )
    op.create_index(op.f("ix_user_identities_provider_email"), "user_identities", ["provider_email"], unique=False)
    op.create_index(op.f("ix_user_identities_user_id"), "user_identities", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_identities_user_id"), table_name="user_identities")
    op.drop_index(op.f("ix_user_identities_provider_email"), table_name="user_identities")
    op.drop_table("user_identities")
    op.drop_index(op.f("ix_microsoft_tenants_tenant_id"), table_name="microsoft_tenants")
    op.drop_table("microsoft_tenants")
    op.alter_column("users", "hashed_password", existing_type=sa.String(length=255), nullable=False)
