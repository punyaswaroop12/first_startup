from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from app.schemas.report import SummaryTemplateResponse, UpdateSummaryTemplateRequest
from app.services.admin import list_audit_logs, update_summary_template

router = APIRouter()


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[AuditLogResponse]:
    return list_audit_logs(db=db)


@router.patch("/summary-templates/{template_id}", response_model=SummaryTemplateResponse)
def update_summary_template_route(
    template_id: UUID,
    payload: UpdateSummaryTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> SummaryTemplateResponse:
    return update_summary_template(
        db=db,
        template_id=template_id,
        description=payload.description,
        instructions_override=payload.instructions_override,
        is_default=payload.is_default,
    )

