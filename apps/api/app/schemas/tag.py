from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    color: str | None
    created_at: datetime


class TagCreateRequest(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None

