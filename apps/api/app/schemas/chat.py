from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CitationResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_name: str
    version_label: str | None
    citation_label: str
    excerpt: str
    score: float
    connector_name: str | None = None
    external_source_kind: str | None = None
    source_label: str | None = None
    source_path: str | None = None
    source_url: str | None = None


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    citations: list[CitationResponse]
    suggested_follow_ups: list[str]
    created_at: datetime


class ChatConversationSummaryResponse(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
    message_count: int


class ChatConversationResponse(BaseModel):
    id: UUID
    title: str
    updated_at: datetime
    messages: list[ChatMessageResponse]


class CreateConversationRequest(BaseModel):
    title: str | None = None


class SendChatMessageRequest(BaseModel):
    content: str
