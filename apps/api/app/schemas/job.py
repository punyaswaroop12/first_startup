from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BackgroundJobResponse(BaseModel):
    id: UUID
    job_type: str
    status: str
    resource_type: str
    resource_id: str | None
    created_by_name: str | None
    scheduled_for: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    attempt_count: int
    payload: dict
    result_payload: dict
    error_message: str | None
    created_at: datetime
