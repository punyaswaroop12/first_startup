from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def create_audit_log(
    db: Session,
    *,
    actor: User | None,
    event_type: str,
    resource_type: str,
    resource_id: str | None,
    message: str,
    details: dict | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        actor=actor,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        message=message,
        details=details or {},
    )
    db.add(audit_log)
    return audit_log

