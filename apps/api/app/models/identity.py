from __future__ import annotations

import enum
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class IdentityProvider(str, enum.Enum):
    MICROSOFT = "microsoft"


class MicrosoftTenant(Base, TimestampMixin):
    __tablename__ = "microsoft_tenants"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tenant_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    identities = relationship("UserIdentity", back_populates="microsoft_tenant")


class UserIdentity(Base, TimestampMixin):
    __tablename__ = "user_identities"
    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uq_user_identities_provider_subject"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[IdentityProvider] = mapped_column(
        Enum(IdentityProvider, native_enum=False), default=IdentityProvider.MICROSOFT
    )
    provider_subject: Mapped[str] = mapped_column(String(255))
    provider_email: Mapped[str] = mapped_column(String(255), index=True)
    provider_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    microsoft_tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("microsoft_tenants.id", ondelete="SET NULL"), nullable=True
    )
    claims: Mapped[dict] = mapped_column(JSON, default=dict)
    last_login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    user = relationship("User", back_populates="identities")
    microsoft_tenant = relationship("MicrosoftTenant", back_populates="identities")
