from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class TeamsChannelRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    channel_label: str | None = None
    delivery_type: str = "preview"
    webhook_url: str | None = None
    is_active: bool = True
    is_default: bool = False

    @model_validator(mode="after")
    def validate_channel(self) -> "TeamsChannelRequest":
        if self.delivery_type == "webhook" and not self.webhook_url:
            raise ValueError("Webhook URL is required for Teams webhook delivery.")
        return self


class TeamsChannelResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    channel_label: str | None
    delivery_type: str
    has_webhook: bool
    is_active: bool
    is_default: bool
    created_at: datetime
