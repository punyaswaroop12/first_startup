from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AutomationRuleRequest(BaseModel):
    name: str
    description: str | None = None
    trigger_type: str
    condition_config: dict = Field(default_factory=dict)
    action_config: list[dict] = Field(default_factory=list)
    is_active: bool = True


class AutomationRuleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    trigger_type: str
    condition_config: dict
    action_config: list[dict]
    is_active: bool
    created_at: datetime


class AutomationRunResponse(BaseModel):
    id: UUID
    rule_name: str
    trigger_type: str
    status: str
    resource_type: str
    resource_id: str
    error_message: str | None
    created_at: datetime
    event_payload: dict
    result_payload: dict

