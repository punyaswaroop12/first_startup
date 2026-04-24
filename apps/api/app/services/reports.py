from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.audit import AuditLog
from app.models.document import Document
from app.models.power_bi import PowerBIReportReference
from app.models.report import Report, ReportStatus, ReportType, SummaryTemplate
from app.models.user import User
from app.providers.email import get_email_provider
from app.providers.llm import get_llm_provider
from app.schemas.power_bi import PowerBIReportReferenceResponse
from app.schemas.report import (
    ReportDeliveryResponse,
    ReportExportResponse,
    ReportListResponse,
    ReportResponse,
    SummaryTemplateResponse,
)
from app.services.audit import create_audit_log
from app.services.power_bi import build_power_bi_context, resolve_power_bi_reports
from app.services.prompts import load_prompt
from app.services.teams import send_teams_message


def list_templates(db: Session) -> list[SummaryTemplateResponse]:
    templates = db.scalars(select(SummaryTemplate).order_by(SummaryTemplate.name)).all()
    return [
        SummaryTemplateResponse(
            id=template.id,
            name=template.name,
            report_type=template.report_type,
            template_key=template.template_key,
            description=template.description,
            instructions_override=template.instructions_override,
            is_default=template.is_default,
        )
        for template in templates
    ]


def list_reports(db: Session, current_user: User) -> ReportListResponse:
    reports = db.scalars(
        select(Report)
        .options(selectinload(Report.created_by))
        .order_by(desc(Report.created_at))
    ).all()
    items = [serialize_report(report, db=db) for report in reports]
    return ReportListResponse(items=items, total=len(items))


def generate_report(
    db: Session,
    *,
    current_user: User,
    report_type: str,
    template_id: UUID | None,
    document_ids: list[UUID],
    power_bi_report_ids: list[UUID],
    notes: str | None,
    trigger_automations: bool = True,
    commit: bool = True,
) -> ReportResponse:
    normalized_type = parse_report_type(report_type)
    template = resolve_template(db=db, report_type=normalized_type, template_id=template_id)
    documents = resolve_documents(db=db, document_ids=document_ids)
    linked_power_bi_reports = resolve_power_bi_reports(db=db, report_ids=power_bi_report_ids)
    activity = db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(12)).all()

    document_context = build_document_context(documents)
    activity_context = build_activity_context(activity)
    power_bi_context = build_power_bi_context(linked_power_bi_reports)

    prompt_override = template.instructions_override or ""
    instruction_prompt = load_prompt(f"reports/{template.template_key}.md")
    llm_provider = get_llm_provider()
    provider_response = llm_provider.generate_report_response(
        system_prompt=load_prompt("reports/system.md"),
        instruction_prompt=f"{instruction_prompt}\n\n{prompt_override}".strip(),
        report_type=normalized_type.value,
        document_context=f"{document_context}\n\nPower BI references:\n{power_bi_context}",
        activity_context=activity_context,
        notes=notes or "",
    )

    report_title = f"{template.name} • {datetime.now(UTC).strftime('%b %d, %Y')}"
    markdown_content = render_markdown(
        title=report_title,
        top_themes=provider_response.top_themes,
        risks=provider_response.risks,
        action_items=provider_response.action_items,
        notable_updates=provider_response.notable_updates,
    )
    html_content = render_html(
        title=report_title,
        top_themes=provider_response.top_themes,
        risks=provider_response.risks,
        action_items=provider_response.action_items,
        notable_updates=provider_response.notable_updates,
    )

    report = Report(
        title=report_title,
        report_type=normalized_type,
        status=ReportStatus.READY,
        created_by=current_user,
        template_id=template.id,
        input_document_ids=[str(document.id) for document in documents],
        notes=notes,
        top_themes=provider_response.top_themes,
        risks=provider_response.risks,
        action_items=provider_response.action_items,
        notable_updates=provider_response.notable_updates,
        power_bi_report_ids=[str(linked_report.id) for linked_report in linked_power_bi_reports],
        markdown_content=markdown_content,
        html_content=html_content,
    )
    db.add(report)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="report_generated",
        resource_type="report",
        resource_id=str(report.id),
        message=f"Generated {template.name}",
        details={
            "report_type": normalized_type.value,
            "document_count": len(documents),
            "template_name": template.name,
            "power_bi_report_count": len(linked_power_bi_reports),
        },
    )
    if commit:
        db.commit()
        db.refresh(report)
        if trigger_automations:
            from app.services.automations import evaluate_automation_rules

            evaluate_automation_rules(
                db,
                current_user=current_user,
                trigger_type="report_generated",
                resource_type="report",
                resource_id=str(report.id),
                event_payload={
                    "report_type": normalized_type.value,
                    "report_title": report.title,
                    "template_name": template.name,
                },
            )
    return serialize_report(report, db=db)


def get_report(db: Session, current_user: User, report_id: UUID) -> ReportResponse:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return serialize_report(report, db=db)


def export_report(
    db: Session,
    *,
    current_user: User,
    report_id: UUID,
    export_format: str,
) -> ReportExportResponse:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    if export_format == "html":
        return ReportExportResponse(
            filename=f"{slugify(report.title)}.html",
            export_format="html",
            content_type="text/html",
            content=report.html_content,
        )
    return ReportExportResponse(
        filename=f"{slugify(report.title)}.md",
        export_format="markdown",
        content_type="text/markdown",
        content=report.markdown_content,
    )


def deliver_report_email(
    db: Session,
    *,
    current_user: User | None,
    report_id: UUID,
    recipients: list[str],
    subject: str | None,
) -> ReportDeliveryResponse:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    if not recipients:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient is required.")
    delivery = get_email_provider().send_email(
        recipients=recipients,
        subject=subject or report.title,
        html=report.html_content,
        text=report.markdown_content,
    )
    create_audit_log(
        db,
        actor=current_user,
        event_type="report_delivered_email",
        resource_type="report",
        resource_id=str(report.id),
        message=f"Delivered report {report.title} by email",
        details={"provider": delivery.provider, "recipient_count": len(recipients)},
    )
    db.commit()
    return ReportDeliveryResponse(provider=delivery.provider, preview_path=delivery.preview_path)


def deliver_report_to_teams(
    db: Session,
    *,
    current_user: User | None,
    report_id: UUID,
    channel_id: UUID | None,
) -> ReportDeliveryResponse:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    delivery = send_teams_message(
        db,
        current_user=current_user,
        channel_id=channel_id,
        title=report.title,
        text=build_report_delivery_text(report),
    )
    return ReportDeliveryResponse(provider=delivery.provider, preview_path=delivery.preview_path)


def resolve_template(db: Session, *, report_type: ReportType, template_id: UUID | None) -> SummaryTemplate:
    if template_id:
        template = db.get(SummaryTemplate, template_id)
        if template:
            return template
    template = db.scalar(
        select(SummaryTemplate).where(
            SummaryTemplate.report_type == report_type.value,
            SummaryTemplate.is_default.is_(True),
        )
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template not found.")
    return template


def resolve_documents(db: Session, document_ids: list[UUID]) -> list[Document]:
    statement = select(Document).options(selectinload(Document.versions), selectinload(Document.tags))
    if document_ids:
        statement = statement.where(Document.id.in_(document_ids))
    return list(db.scalars(statement.order_by(desc(Document.created_at)).limit(6)).all())


def build_document_context(documents: list[Document]) -> str:
    if not documents:
        return "No documents selected."

    blocks = []
    for document in documents:
        version = next((item for item in document.versions if item.is_current), None)
        extracted = version.extracted_text[:1800] if version else "No extracted text."
        blocks.append(
            "\n".join(
                [
                    f"Document: {document.name}",
                    f"Tags: {', '.join(tag.name for tag in document.tags) or 'none'}",
                    f"Version: {document.version_label or 'n/a'}",
                    f"Review flag: {document.review_reason or 'none'}",
                    f"Excerpt:\n{extracted}",
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)


def build_activity_context(activity: list[AuditLog]) -> str:
    if not activity:
        return "No recent activity logs."
    return "\n".join(
        f"- {item.created_at.isoformat()} | {item.event_type} | {item.message}" for item in activity
    )


def render_markdown(
    *,
    title: str,
    top_themes: list[str],
    risks: list[str],
    action_items: list[str],
    notable_updates: list[str],
) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "## Top themes",
            *[f"- {item}" for item in top_themes],
            "",
            "## Risks/issues",
            *[f"- {item}" for item in risks],
            "",
            "## Action items",
            *[f"- {item}" for item in action_items],
            "",
            "## Notable updates",
            *[f"- {item}" for item in notable_updates],
            "",
        ]
    )


def render_html(
    *,
    title: str,
    top_themes: list[str],
    risks: list[str],
    action_items: list[str],
    notable_updates: list[str],
) -> str:
    return "".join(
        [
            "<html><body style='font-family: IBM Plex Sans, sans-serif; color: #162033;'>",
            f"<h1>{escape(title)}</h1>",
            render_section_html("Top themes", top_themes),
            render_section_html("Risks/issues", risks),
            render_section_html("Action items", action_items),
            render_section_html("Notable updates", notable_updates),
            "</body></html>",
        ]
    )


def render_section_html(title: str, items: list[str]) -> str:
    return (
        f"<h2>{escape(title)}</h2><ul>"
        + "".join(f"<li>{escape(item)}</li>" for item in items)
        + "</ul>"
    )


def build_report_delivery_text(report: Report) -> str:
    return "\n".join(
        [
            "Top themes:",
            *[f"- {item}" for item in report.top_themes[:3]],
            "",
            "Risks:",
            *[f"- {item}" for item in report.risks[:3]],
            "",
            "Action items:",
            *[f"- {item}" for item in report.action_items[:3]],
        ]
    )


def parse_report_type(value: str) -> ReportType:
    try:
        return ReportType(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report type.") from exc


def serialize_report(report: Report, *, db: Session) -> ReportResponse:
    template_name = None
    if report.template_id:
        template = db.get(SummaryTemplate, report.template_id)
        template_name = template.name if template else None
    linked_power_bi_reports = resolve_report_power_bi_links(db=db, report=report)
    return ReportResponse(
        id=report.id,
        title=report.title,
        report_type=report.report_type.value,
        status=report.status.value,
        template_name=template_name,
        top_themes=report.top_themes,
        risks=report.risks,
        action_items=report.action_items,
        notable_updates=report.notable_updates,
        linked_power_bi_reports=linked_power_bi_reports,
        markdown_content=report.markdown_content,
        html_content=report.html_content,
        created_at=report.created_at,
    )


def slugify(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-")


def resolve_report_power_bi_links(
    *,
    db: Session,
    report: Report,
) -> list[PowerBIReportReferenceResponse]:
    if not report.power_bi_report_ids:
        return []
    report_ids: list[UUID] = []
    for raw_id in report.power_bi_report_ids:
        try:
            report_ids.append(UUID(str(raw_id)))
        except ValueError:
            continue
    if not report_ids:
        return []
    linked_reports = db.scalars(
        select(PowerBIReportReference).where(PowerBIReportReference.id.in_(report_ids))
    ).all()
    return [
        PowerBIReportReferenceResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            workspace_name=item.workspace_name,
            workspace_id=item.workspace_id,
            report_id=item.report_id,
            report_url=item.report_url,
            embed_url=item.embed_url,
            tags=item.tags,
            is_active=item.is_active,
            created_at=item.created_at,
        )
        for item in linked_reports
    ]
