from __future__ import annotations

import enum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class AutomationTriggerType(str, enum.Enum):
    DOCUMENT_UPLOADED = "document_uploaded"
    REPORT_GENERATED = "report_generated"
    KEYWORD_DETECTED = "keyword_detected"


class AutomationRunStatus(str, enum.Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class AutomationRule(Base, TimestampMixin):
    __tablename__ = "automation_rules"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[AutomationTriggerType] = mapped_column(
        Enum(AutomationTriggerType, native_enum=False)
    )
    condition_config: Mapped[dict] = mapped_column(JSON, default=dict)
    action_config: Mapped[list[dict]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_by = relationship("User", back_populates="automation_rules")
    runs = relationship("AutomationRun", back_populates="rule", cascade="all, delete-orphan")


class AutomationRun(Base, TimestampMixin):
    __tablename__ = "automation_runs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    rule_id: Mapped[UUID] = mapped_column(ForeignKey("automation_rules.id", ondelete="CASCADE"))
    trigger_type: Mapped[AutomationTriggerType] = mapped_column(
        Enum(AutomationTriggerType, native_enum=False)
    )
    status: Mapped[AutomationRunStatus] = mapped_column(Enum(AutomationRunStatus, native_enum=False))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(128))
    event_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    rule = relationship("AutomationRule", back_populates="runs")
