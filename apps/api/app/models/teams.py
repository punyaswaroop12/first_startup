from __future__ import annotations

import enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class TeamsChannelDeliveryType(str, enum.Enum):
    WEBHOOK = "webhook"
    PREVIEW = "preview"


class TeamsChannel(Base, TimestampMixin):
    __tablename__ = "teams_channels"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delivery_type: Mapped[TeamsChannelDeliveryType] = mapped_column(
        Enum(TeamsChannelDeliveryType, native_enum=False),
        default=TeamsChannelDeliveryType.PREVIEW,
    )
    webhook_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_by = relationship("User")
