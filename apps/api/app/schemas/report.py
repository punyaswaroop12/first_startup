from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.power_bi import PowerBIReportReferenceResponse


class SummaryTemplateResponse(BaseModel):
    id: UUID
    name: str
    report_type: str
    template_key: str
    description: str | None
    instructions_override: str | None = None
    is_default: bool


class UpdateSummaryTemplateRequest(BaseModel):
    description: str | None = None
    instructions_override: str | None = None
    is_default: bool | None = None


class GenerateReportRequest(BaseModel):
    report_type: str
    template_id: UUID | None = None
    document_ids: list[UUID] = Field(default_factory=list)
    power_bi_report_ids: list[UUID] = Field(default_factory=list)
    notes: str | None = None


class ReportResponse(BaseModel):
    id: UUID
    title: str
    report_type: str
    status: str
    template_name: str | None
    top_themes: list[str]
    risks: list[str]
    action_items: list[str]
    notable_updates: list[str]
    linked_power_bi_reports: list[PowerBIReportReferenceResponse] = Field(default_factory=list)
    markdown_content: str
    html_content: str
    created_at: datetime


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int


class ReportExportResponse(BaseModel):
    filename: str
    export_format: str
    content_type: str
    content: str


class DeliverReportEmailRequest(BaseModel):
    recipients: list[str] = Field(default_factory=list)
    subject: str | None = None


class DeliverReportTeamsRequest(BaseModel):
    channel_id: UUID | None = None


class ReportDeliveryResponse(BaseModel):
    provider: str
    preview_path: str | None = None
