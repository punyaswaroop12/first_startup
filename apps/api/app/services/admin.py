from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.report import SummaryTemplate
from app.schemas.audit import AuditLogResponse
from app.schemas.report import SummaryTemplateResponse


def list_audit_logs(db: Session) -> list[AuditLogResponse]:
    logs = db.scalars(
        select(AuditLog).options(selectinload(AuditLog.actor)).order_by(desc(AuditLog.created_at)).limit(50)
    ).all()
    return [
        AuditLogResponse(
            id=log.id,
            event_type=log.event_type,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            message=log.message,
            actor_name=log.actor.full_name if log.actor else None,
            created_at=log.created_at,
            details=log.details,
        )
        for log in logs
    ]


def update_summary_template(
    db: Session,
    *,
    template_id: UUID,
    description: str | None,
    instructions_override: str | None,
    is_default: bool | None,
) -> SummaryTemplateResponse:
    template = db.get(SummaryTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary template not found.")

    if description is not None:
        template.description = description
    if instructions_override is not None:
        template.instructions_override = instructions_override
    if is_default is not None:
        if is_default:
            for sibling in db.scalars(
                select(SummaryTemplate).where(SummaryTemplate.report_type == template.report_type)
            ).all():
                sibling.is_default = sibling.id == template.id
        template.is_default = is_default

    db.commit()
    db.refresh(template)
    return SummaryTemplateResponse(
        id=template.id,
        name=template.name,
        report_type=template.report_type,
        template_key=template.template_key,
        description=template.description,
        instructions_override=template.instructions_override,
        is_default=template.is_default,
    )
