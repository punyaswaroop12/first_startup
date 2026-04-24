from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.power_bi import PowerBIReportReference
from app.models.user import User
from app.schemas.power_bi import PowerBIReportReferenceRequest, PowerBIReportReferenceResponse
from app.services.audit import create_audit_log


def list_power_bi_reports(db: Session, *, active_only: bool = False) -> list[PowerBIReportReferenceResponse]:
    statement = select(PowerBIReportReference).order_by(PowerBIReportReference.name)
    if active_only:
        statement = statement.where(PowerBIReportReference.is_active.is_(True))
    reports = db.scalars(statement).all()
    return [serialize_power_bi_report(report) for report in reports]


def create_power_bi_report(
    db: Session,
    *,
    current_user: User,
    payload: PowerBIReportReferenceRequest,
) -> PowerBIReportReferenceResponse:
    existing = db.scalar(select(PowerBIReportReference).where(PowerBIReportReference.name == payload.name))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Power BI report name already exists.")
    report = PowerBIReportReference(
        name=payload.name,
        description=payload.description,
        workspace_name=payload.workspace_name,
        workspace_id=payload.workspace_id,
        report_id=payload.report_id,
        report_url=payload.report_url,
        embed_url=payload.embed_url,
        tags=normalize_tags(payload.tags),
        is_active=payload.is_active,
        created_by=current_user,
    )
    db.add(report)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="power_bi_report_configured",
        resource_type="power_bi_report",
        resource_id=str(report.id),
        message=f"Configured Power BI reference {report.name}",
        details={"workspace_name": report.workspace_name, "report_url": report.report_url},
    )
    db.commit()
    db.refresh(report)
    return serialize_power_bi_report(report)


def update_power_bi_report(
    db: Session,
    *,
    report_id: UUID,
    payload: PowerBIReportReferenceRequest,
    current_user: User,
) -> PowerBIReportReferenceResponse:
    report = db.get(PowerBIReportReference, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Power BI report not found.")
    report.name = payload.name
    report.description = payload.description
    report.workspace_name = payload.workspace_name
    report.workspace_id = payload.workspace_id
    report.report_id = payload.report_id
    report.report_url = payload.report_url
    report.embed_url = payload.embed_url
    report.tags = normalize_tags(payload.tags)
    report.is_active = payload.is_active
    create_audit_log(
        db,
        actor=current_user,
        event_type="power_bi_report_updated",
        resource_type="power_bi_report",
        resource_id=str(report.id),
        message=f"Updated Power BI reference {report.name}",
        details={"is_active": report.is_active},
    )
    db.commit()
    db.refresh(report)
    return serialize_power_bi_report(report)


def resolve_power_bi_reports(db: Session, report_ids: list[UUID]) -> list[PowerBIReportReference]:
    if not report_ids:
        return []
    return list(
        db.scalars(
            select(PowerBIReportReference).where(
                PowerBIReportReference.id.in_(report_ids),
                PowerBIReportReference.is_active.is_(True),
            )
        ).all()
    )


def build_power_bi_context(reports: list[PowerBIReportReference]) -> str:
    if not reports:
        return "No linked Power BI reports."
    return "\n".join(
        [
            f"- {report.name} | Workspace: {report.workspace_name or 'n/a'} | URL: {report.report_url}"
            for report in reports
        ]
    )


def serialize_power_bi_report(report: PowerBIReportReference) -> PowerBIReportReferenceResponse:
    return PowerBIReportReferenceResponse(
        id=report.id,
        name=report.name,
        description=report.description,
        workspace_name=report.workspace_name,
        workspace_id=report.workspace_id,
        report_id=report.report_id,
        report_url=report.report_url,
        embed_url=report.embed_url,
        tags=report.tags,
        is_active=report.is_active,
        created_at=report.created_at,
    )


def normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    for tag in tags:
        value = tag.strip()
        if value and value not in normalized:
            normalized.append(value)
    return normalized
