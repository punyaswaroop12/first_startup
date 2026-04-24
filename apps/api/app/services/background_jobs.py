from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.job import BackgroundJob, BackgroundJobStatus, BackgroundJobType
from app.models.microsoft import MicrosoftConnector, MicrosoftConnectorStatus
from app.models.user import User
from app.providers.email import get_email_provider
from app.schemas.job import BackgroundJobResponse
from app.services.audit import create_audit_log
from app.services.microsoft_connectors import sync_microsoft_connector
from app.services.reports import deliver_report_email, deliver_report_to_teams
from app.services.teams import send_teams_message


def list_background_jobs(db: Session, limit: int = 50) -> list[BackgroundJobResponse]:
    jobs = db.scalars(
        select(BackgroundJob)
        .options(selectinload(BackgroundJob.created_by))
        .order_by(desc(BackgroundJob.created_at))
        .limit(limit)
    ).all()
    return [serialize_background_job(job) for job in jobs]


def enqueue_connector_sync_job(
    db: Session,
    *,
    connector_id: UUID,
    current_user: User | None,
    reason: str,
) -> BackgroundJob:
    job = BackgroundJob(
        job_type=BackgroundJobType.CONNECTOR_SYNC,
        status=BackgroundJobStatus.QUEUED,
        resource_type="microsoft_connector",
        resource_id=str(connector_id),
        created_by=current_user,
        scheduled_for=datetime.now(UTC),
        payload={"reason": reason},
    )
    db.add(job)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="background_job_queued",
        resource_type="background_job",
        resource_id=str(job.id),
        message=f"Queued connector sync job for connector {connector_id}",
        details={"job_type": job.job_type.value, "reason": reason},
    )
    db.commit()
    db.refresh(job)
    return job


def enqueue_report_delivery_job(
    db: Session,
    *,
    report_id: UUID,
    current_user: User | None,
    delivery_type: str,
    recipients: list[str] | None = None,
    subject: str | None = None,
    channel_id: UUID | None = None,
) -> BackgroundJob:
    job = BackgroundJob(
        job_type=BackgroundJobType.SUMMARY_DELIVERY,
        status=BackgroundJobStatus.QUEUED,
        resource_type="report",
        resource_id=str(report_id),
        created_by=current_user,
        scheduled_for=datetime.now(UTC),
        payload={
            "delivery_type": delivery_type,
            "recipients": recipients or [],
            "subject": subject,
            "channel_id": str(channel_id) if channel_id else None,
        },
    )
    db.add(job)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="background_job_queued",
        resource_type="background_job",
        resource_id=str(job.id),
        message=f"Queued report delivery job for report {report_id}",
        details={"job_type": job.job_type.value, "delivery_type": delivery_type},
    )
    db.commit()
    db.refresh(job)
    return job


def enqueue_notification_job(
    db: Session,
    *,
    current_user: User | None,
    resource_type: str,
    resource_id: str | None,
    channel: str,
    title: str,
    text: str,
    recipients: list[str] | None = None,
    subject: str | None = None,
    html: str | None = None,
    channel_id: UUID | None = None,
) -> BackgroundJob:
    job = BackgroundJob(
        job_type=BackgroundJobType.NOTIFICATION,
        status=BackgroundJobStatus.QUEUED,
        resource_type=resource_type,
        resource_id=resource_id,
        created_by=current_user,
        scheduled_for=datetime.now(UTC),
        payload={
            "channel": channel,
            "title": title,
            "text": text,
            "html": html,
            "subject": subject,
            "recipients": recipients or [],
            "channel_id": str(channel_id) if channel_id else None,
        },
    )
    db.add(job)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="background_job_queued",
        resource_type="background_job",
        resource_id=str(job.id),
        message=f"Queued {channel} notification job",
        details={"job_type": job.job_type.value, "resource_type": resource_type},
    )
    db.commit()
    db.refresh(job)
    return job


def enqueue_due_connector_sync_jobs(db: Session, *, current_user: User | None) -> list[BackgroundJob]:
    due_connectors = db.scalars(
        select(MicrosoftConnector).where(
            MicrosoftConnector.is_active.is_(True),
            MicrosoftConnector.next_sync_at.is_not(None),
            MicrosoftConnector.next_sync_at <= datetime.now(UTC),
        )
    ).all()
    jobs: list[BackgroundJob] = []
    for connector in due_connectors:
        existing_open_job = db.scalar(
            select(BackgroundJob).where(
                BackgroundJob.job_type == BackgroundJobType.CONNECTOR_SYNC,
                BackgroundJob.resource_id == str(connector.id),
                BackgroundJob.status.in_([BackgroundJobStatus.QUEUED, BackgroundJobStatus.RUNNING]),
            )
        )
        if existing_open_job:
            continue
        jobs.append(
            enqueue_connector_sync_job(
                db,
                connector_id=connector.id,
                current_user=current_user,
                reason="scheduled",
            )
        )
    return jobs


def dispatch_background_job(background_tasks: BackgroundTasks, job: BackgroundJob) -> None:
    if settings.background_job_inline_execution:
        background_tasks.add_task(run_background_job, job.id)


def dispatch_background_jobs(background_tasks: BackgroundTasks, jobs: list[BackgroundJob]) -> None:
    for job in jobs:
        dispatch_background_job(background_tasks, job)


def run_background_job_inline_if_enabled(job_id: UUID) -> None:
    if settings.background_job_inline_execution:
        run_background_job(job_id)


def run_background_job(job_id: UUID) -> None:
    with SessionLocal() as db:
        job = db.scalar(
            select(BackgroundJob)
            .where(BackgroundJob.id == job_id)
            .options(selectinload(BackgroundJob.created_by))
        )
        if not job or job.status not in {BackgroundJobStatus.QUEUED, BackgroundJobStatus.RUNNING}:
            return

        job.status = BackgroundJobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        job.attempt_count += 1
        job.error_message = None
        db.commit()

        try:
            result_payload = execute_background_job(db, job)
            job.result_payload = result_payload
            job.status = BackgroundJobStatus.SUCCEEDED
            job.finished_at = datetime.now(UTC)
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            failed_job = db.get(BackgroundJob, job_id)
            if failed_job:
                if failed_job.resource_type == "microsoft_connector" and failed_job.resource_id:
                    connector = db.scalar(
                        select(MicrosoftConnector).where(MicrosoftConnector.id == UUID(failed_job.resource_id))
                    )
                    if connector:
                        connector.status = MicrosoftConnectorStatus.ERROR
                        connector.last_error = str(exc)
                failed_job.status = BackgroundJobStatus.FAILED
                failed_job.error_message = str(exc)
                failed_job.finished_at = datetime.now(UTC)
                db.commit()


def execute_background_job(db: Session, job: BackgroundJob) -> dict:
    if job.job_type == BackgroundJobType.CONNECTOR_SYNC and job.resource_id:
        return sync_microsoft_connector(
            db,
            connector_id=UUID(job.resource_id),
            job=job,
        )
    if job.job_type == BackgroundJobType.SUMMARY_DELIVERY and job.resource_id:
        if job.payload.get("delivery_type") == "email":
            delivery = deliver_report_email(
                db,
                current_user=job.created_by,
                report_id=UUID(job.resource_id),
                recipients=list(job.payload.get("recipients", [])),
                subject=job.payload.get("subject"),
            )
            return delivery.model_dump()
        if job.payload.get("delivery_type") == "teams":
            channel_id = job.payload.get("channel_id")
            delivery = deliver_report_to_teams(
                db,
                current_user=job.created_by,
                report_id=UUID(job.resource_id),
                channel_id=UUID(channel_id) if channel_id else None,
            )
            return delivery.model_dump()
    if job.job_type == BackgroundJobType.NOTIFICATION:
        return execute_notification_job(db, job)
    return {"status": "skipped"}


def execute_notification_job(db: Session, job: BackgroundJob) -> dict:
    channel = str(job.payload.get("channel") or "email")
    if channel == "teams":
        channel_id = job.payload.get("channel_id")
        delivery = send_teams_message(
            db,
            current_user=job.created_by,
            channel_id=UUID(channel_id) if channel_id else None,
            title=str(job.payload.get("title") or "Operations assistant notification"),
            text=str(job.payload.get("text") or ""),
        )
        return {"provider": delivery.provider, "preview_path": delivery.preview_path}

    recipients = [value for value in job.payload.get("recipients", []) if value]
    if not recipients:
        return {"status": "skipped", "reason": "no_recipients"}

    delivery = get_email_provider().send_email(
        recipients=recipients,
        subject=str(job.payload.get("subject") or job.payload.get("title") or "Operations assistant notification"),
        html=str(job.payload.get("html") or f"<p>{job.payload.get('text') or ''}</p>"),
        text=str(job.payload.get("text") or ""),
    )
    create_audit_log(
        db,
        actor=job.created_by,
        event_type="notification_email_sent",
        resource_type=job.resource_type,
        resource_id=job.resource_id,
        message=f"Delivered notification email for {job.resource_type}",
        details={"provider": delivery.provider, "recipient_count": len(recipients)},
    )
    db.commit()
    return {"provider": delivery.provider, "preview_path": delivery.preview_path}


def serialize_background_job(job: BackgroundJob) -> BackgroundJobResponse:
    return BackgroundJobResponse(
        id=job.id,
        job_type=job.job_type.value,
        status=job.status.value,
        resource_type=job.resource_type,
        resource_id=job.resource_id,
        created_by_name=job.created_by.full_name if job.created_by else None,
        scheduled_for=job.scheduled_for,
        started_at=job.started_at,
        finished_at=job.finished_at,
        attempt_count=job.attempt_count,
        payload=job.payload,
        result_payload=job.result_payload,
        error_message=job.error_message,
        created_at=job.created_at,
    )
