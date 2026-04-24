from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.automation import (
    AutomationRule,
    AutomationRun,
    AutomationRunStatus,
    AutomationTriggerType,
)
from app.models.document import Document
from app.models.job import BackgroundJob
from app.models.user import User
from app.schemas.automation import (
    AutomationRuleRequest,
    AutomationRuleResponse,
    AutomationRunResponse,
)
from app.services.audit import create_audit_log
from app.services.background_jobs import (
    enqueue_notification_job,
    enqueue_report_delivery_job,
    run_background_job_inline_if_enabled,
)
from app.services.reports import generate_report


def list_rules(db: Session) -> list[AutomationRuleResponse]:
    rules = db.scalars(select(AutomationRule).order_by(AutomationRule.name)).all()
    return [serialize_rule(rule) for rule in rules]


def create_rule(db: Session, *, current_user: User, payload: AutomationRuleRequest) -> AutomationRuleResponse:
    rule = AutomationRule(
        name=payload.name,
        description=payload.description,
        trigger_type=parse_trigger_type(payload.trigger_type),
        condition_config=payload.condition_config,
        action_config=payload.action_config,
        is_active=payload.is_active,
        created_by=current_user,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return serialize_rule(rule)


def update_rule(db: Session, *, rule_id: UUID, payload: AutomationRuleRequest) -> AutomationRuleResponse:
    rule = db.get(AutomationRule, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation rule not found.")

    rule.name = payload.name
    rule.description = payload.description
    rule.trigger_type = parse_trigger_type(payload.trigger_type)
    rule.condition_config = payload.condition_config
    rule.action_config = payload.action_config
    rule.is_active = payload.is_active
    db.commit()
    db.refresh(rule)
    return serialize_rule(rule)


def list_runs(db: Session) -> list[AutomationRunResponse]:
    runs = db.scalars(
        select(AutomationRun).join(AutomationRun.rule).order_by(desc(AutomationRun.created_at)).limit(50)
    ).all()
    return [
        AutomationRunResponse(
            id=run.id,
            rule_name=run.rule.name,
            trigger_type=run.trigger_type.value,
            status=run.status.value,
            resource_type=run.resource_type,
            resource_id=run.resource_id,
            error_message=run.error_message,
            created_at=run.created_at,
            event_payload=run.event_payload,
            result_payload=run.result_payload,
        )
        for run in runs
    ]


def evaluate_automation_rules(
    db: Session,
    *,
    current_user: User | None,
    trigger_type: str,
    resource_type: str,
    resource_id: str,
    event_payload: dict,
) -> None:
    parsed_trigger = parse_trigger_type(trigger_type)
    rules = db.scalars(
        select(AutomationRule).where(
            AutomationRule.trigger_type == parsed_trigger,
            AutomationRule.is_active.is_(True),
        )
    ).all()

    for rule in rules:
        if not rule_matches(rule=rule, event_payload=event_payload):
            continue

        run = AutomationRun(
            rule=rule,
            trigger_type=parsed_trigger,
            status=AutomationRunStatus.SUCCEEDED,
            resource_type=resource_type,
            resource_id=resource_id,
            event_payload=event_payload,
            result_payload={},
        )
        db.add(run)
        db.flush()

        try:
            results = []
            for action in rule.action_config:
                results.append(
                    execute_action(
                        db=db,
                        current_user=current_user,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        event_payload=event_payload,
                    )
                )
            run.result_payload = {"actions": results}
            create_audit_log(
                db,
                actor=current_user,
                event_type="automation_triggered",
                resource_type="automation_rule",
                resource_id=str(rule.id),
                message=f"Automation rule '{rule.name}' executed",
                details={"resource_type": resource_type, "resource_id": resource_id},
            )
        except Exception as exc:  # noqa: BLE001
            run.status = AutomationRunStatus.FAILED
            run.error_message = str(exc)
        db.commit()


def rule_matches(*, rule: AutomationRule, event_payload: dict) -> bool:
    conditions = rule.condition_config or {}

    tags_any = conditions.get("tags_any", [])
    if tags_any and not set(tags_any).intersection(set(event_payload.get("tags", []))):
        return False

    keywords_any = conditions.get("keywords_any", [])
    if keywords_any and not set(keywords_any).intersection(set(event_payload.get("matched_keywords", []))):
        return False

    report_type = conditions.get("report_type")
    if report_type and event_payload.get("report_type") != report_type:
        return False

    return True


def execute_action(
    db: Session,
    *,
    current_user: User | None,
    action: dict,
    resource_type: str,
    resource_id: str,
    event_payload: dict,
) -> dict:
    action_type = action.get("type")
    if action_type == "notify_recipients":
        recipients = action.get("recipients", [])
        subject = action.get("subject") or f"Automation notification: {event_payload.get('name', resource_type)}"
        job = enqueue_notification_job(
            db,
            current_user=current_user,
            resource_type=resource_type,
            resource_id=resource_id,
            channel="email",
            title=subject,
            subject=subject,
            text=build_notification_text(resource_type=resource_type, resource_id=resource_id, event_payload=event_payload),
            html=build_notification_html(resource_type=resource_type, resource_id=resource_id, event_payload=event_payload),
            recipients=recipients,
        )
        return serialize_background_action_result(action_type=action_type, job=run_or_refresh_job(db, job.id))

    if action_type == "flag_for_review" and resource_type == "document":
        document = db.get(Document, UUID(resource_id))
        if document:
            document.requires_review = True
            document.review_reason = action.get("reason", "Flagged by automation rule")
        return {"type": action_type, "flagged": bool(document)}

    if action_type == "generate_summary" and resource_type == "document":
        document = db.get(Document, UUID(resource_id))
        if not document:
            return {"type": action_type, "status": "skipped"}
        report = generate_report(
            db=db,
            current_user=current_user or document.owner,
            report_type=action.get("report_type", "operational"),
            template_id=None,
            document_ids=[document.id],
            power_bi_report_ids=[],
            notes=action.get("notes"),
            trigger_automations=False,
            commit=False,
        )
        return {"type": action_type, "report_id": str(report.id), "report_title": report.title}

    if action_type == "deliver_report_email" and resource_type == "report":
        job = enqueue_report_delivery_job(
            db,
            report_id=UUID(resource_id),
            current_user=current_user,
            delivery_type="email",
            recipients=action.get("recipients", []),
            subject=action.get("subject"),
        )
        return serialize_background_action_result(action_type=action_type, job=run_or_refresh_job(db, job.id))

    if action_type == "deliver_report_teams" and resource_type == "report":
        channel_id = action.get("channel_id")
        job = enqueue_report_delivery_job(
            db,
            report_id=UUID(resource_id),
            current_user=current_user,
            delivery_type="teams",
            channel_id=UUID(channel_id) if channel_id else None,
        )
        return serialize_background_action_result(action_type=action_type, job=run_or_refresh_job(db, job.id))

    if action_type == "post_to_teams":
        title = str(action.get("title") or build_notification_title(resource_type=resource_type, event_payload=event_payload))
        job = enqueue_notification_job(
            db,
            current_user=current_user,
            resource_type=resource_type,
            resource_id=resource_id,
            channel="teams",
            title=title,
            text=build_notification_text(resource_type=resource_type, resource_id=resource_id, event_payload=event_payload),
            channel_id=UUID(action["channel_id"]) if action.get("channel_id") else None,
        )
        return serialize_background_action_result(action_type=action_type, job=run_or_refresh_job(db, job.id))

    return {"type": action_type, "status": "skipped"}


def serialize_rule(rule: AutomationRule) -> AutomationRuleResponse:
    return AutomationRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        trigger_type=rule.trigger_type.value,
        condition_config=rule.condition_config,
        action_config=rule.action_config,
        is_active=rule.is_active,
        created_at=rule.created_at,
    )


def parse_trigger_type(value: str) -> AutomationTriggerType:
    try:
        return AutomationTriggerType(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trigger type.") from exc


def run_or_refresh_job(db: Session, job_id: UUID) -> BackgroundJob:
    run_background_job_inline_if_enabled(job_id)
    refreshed = db.get(BackgroundJob, job_id)
    if not refreshed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Background job not found.")
    return refreshed


def serialize_background_action_result(*, action_type: str, job: BackgroundJob) -> dict:
    return {
        "type": action_type,
        "job_id": str(job.id),
        "status": job.status.value,
        **job.result_payload,
    }


def build_notification_title(*, resource_type: str, event_payload: dict) -> str:
    return f"{resource_type.replace('_', ' ').title()} event: {event_payload.get('name', resource_type)}"


def build_notification_text(*, resource_type: str, resource_id: str, event_payload: dict) -> str:
    return "\n".join(
        [
            f"Resource: {resource_type} {resource_id}",
            "",
            "Payload:",
            str(event_payload),
        ]
    )


def build_notification_html(*, resource_type: str, resource_id: str, event_payload: dict) -> str:
    return (
        f"<p>Automation event for <strong>{resource_type}</strong> {resource_id}</p>"
        f"<pre>{event_payload}</pre>"
    )
