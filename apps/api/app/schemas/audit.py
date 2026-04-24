from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    event_type: str
    resource_type: str
    resource_id: str | None
    message: str
    actor_name: str | None
    created_at: datetime
    details: dict

