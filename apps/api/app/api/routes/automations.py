from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.automation import (
    AutomationRuleRequest,
    AutomationRuleResponse,
    AutomationRunResponse,
)
from app.services.automations import create_rule, list_rules, list_runs, update_rule

router = APIRouter()


@router.get("/rules", response_model=list[AutomationRuleResponse])
def list_rules_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[AutomationRuleResponse]:
    return list_rules(db=db)


@router.post("/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule_route(
    payload: AutomationRuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AutomationRuleResponse:
    return create_rule(db=db, current_user=current_user, payload=payload)


@router.patch("/rules/{rule_id}", response_model=AutomationRuleResponse)
def update_rule_route(
    rule_id: UUID,
    payload: AutomationRuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AutomationRuleResponse:
    return update_rule(db=db, rule_id=rule_id, payload=payload)


@router.get("/runs", response_model=list[AutomationRunResponse])
def list_runs_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[AutomationRunResponse]:
    return list_runs(db=db)

