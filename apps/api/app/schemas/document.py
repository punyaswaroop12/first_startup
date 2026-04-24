from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.tag import TagResponse


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_label: str | None
    parser_name: str
    extraction_notes: str | None
    created_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    source_type: str
    status: str
    owner_name: str
    owner_email: str
    content_type: str | None
    file_size_bytes: int
    version_label: str | None
    requires_review: bool
    review_reason: str | None
    tags: list[TagResponse]
    chunk_count: int
    current_version: DocumentVersionResponse | None
    connector_name: str | None = None
    external_source_kind: str | None = None
    source_label: str | None = None
    source_path: str | None = None
    source_url: str | None = None
    created_at: datetime
    updated_at: datetime
    matched_excerpt: str | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
