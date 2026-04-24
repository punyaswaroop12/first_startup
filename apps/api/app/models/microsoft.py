from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class MicrosoftConnectorType(str, enum.Enum):
    SHAREPOINT = "sharepoint"
    ONEDRIVE = "onedrive"


class MicrosoftConnectorStatus(str, enum.Enum):
    READY = "ready"
    SYNCING = "syncing"
    ERROR = "error"
    PAUSED = "paused"


class MicrosoftSyncedItemState(str, enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    SKIPPED = "skipped"
    ERROR = "error"


class MicrosoftConnector(Base, TimestampMixin):
    __tablename__ = "microsoft_connectors"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    connector_type: Mapped[MicrosoftConnectorType] = mapped_column(
        Enum(MicrosoftConnectorType, native_enum=False)
    )
    status: Mapped[MicrosoftConnectorStatus] = mapped_column(
        Enum(MicrosoftConnectorStatus, native_enum=False), default=MicrosoftConnectorStatus.READY
    )
    microsoft_tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("microsoft_tenants.id", ondelete="RESTRICT"), index=True
    )
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_frequency_minutes: Mapped[int] = mapped_column(Integer, default=1440)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    resolved_target: Mapped[dict] = mapped_column(JSON, default=dict)
    permissions_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    last_delta_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    microsoft_tenant = relationship("MicrosoftTenant")
    created_by = relationship("User")
    synced_items = relationship(
        "MicrosoftSyncedItem",
        back_populates="connector",
        cascade="all, delete-orphan",
        order_by="desc(MicrosoftSyncedItem.updated_at)",
    )


class MicrosoftSyncedItem(Base, TimestampMixin):
    __tablename__ = "microsoft_synced_items"
    __table_args__ = (
        UniqueConstraint("connector_id", "external_item_id", name="uq_microsoft_synced_items_connector_item"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    connector_id: Mapped[UUID] = mapped_column(
        ForeignKey("microsoft_connectors.id", ondelete="CASCADE"), index=True
    )
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    last_synced_job_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("background_jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    external_item_id: Mapped[str] = mapped_column(String(255), index=True)
    parent_external_item_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drive_id: Mapped[str] = mapped_column(String(255), index=True)
    item_name: Mapped[str] = mapped_column(String(255))
    item_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_extension: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    etag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ctag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[MicrosoftSyncedItemState] = mapped_column(
        Enum(MicrosoftSyncedItemState, native_enum=False), default=MicrosoftSyncedItemState.ACTIVE
    )
    item_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    permissions_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    connector = relationship("MicrosoftConnector", back_populates="synced_items")
    document = relationship("Document")
    last_synced_job = relationship("BackgroundJob")
