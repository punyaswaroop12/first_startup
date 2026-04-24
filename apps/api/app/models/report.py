from __future__ import annotations

import enum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin


class ReportType(str, enum.Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    DOCUMENT_CHANGES = "document_changes"


class ReportStatus(str, enum.Enum):
    READY = "ready"
    FAILED = "failed"


class SummaryTemplate(Base, TimestampMixin):
    __tablename__ = "summary_templates"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    report_type: Mapped[str] = mapped_column(String(64))
    template_key: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType, native_enum=False))
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, native_enum=False), default=ReportStatus.READY
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    template_id: Mapped[UUID | None] = mapped_column(ForeignKey("summary_templates.id"), nullable=True)
    input_document_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    top_themes: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    action_items: Mapped[list[str]] = mapped_column(JSON, default=list)
    notable_updates: Mapped[list[str]] = mapped_column(JSON, default=list)
    power_bi_report_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    markdown_content: Mapped[str] = mapped_column(Text)
    html_content: Mapped[str] = mapped_column(Text)

    created_by = relationship("User", back_populates="reports")
