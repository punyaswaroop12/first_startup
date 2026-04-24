from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PowerBIReportReferenceRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    workspace_name: str | None = None
    workspace_id: str | None = None
    report_id: str | None = None
    report_url: str
    embed_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True


class PowerBIReportReferenceResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    workspace_name: str | None
    workspace_id: str | None
    report_id: str | None
    report_url: str
    embed_url: str | None
    tags: list[str]
    is_active: bool
    created_at: datetime
