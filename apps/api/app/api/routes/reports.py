from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.job import BackgroundJobResponse
from app.schemas.power_bi import PowerBIReportReferenceResponse
from app.schemas.report import (
    DeliverReportEmailRequest,
    DeliverReportTeamsRequest,
    GenerateReportRequest,
    ReportExportResponse,
    ReportListResponse,
    ReportResponse,
    SummaryTemplateResponse,
)
from app.schemas.teams import TeamsChannelResponse
from app.services.background_jobs import (
    dispatch_background_job,
    enqueue_report_delivery_job,
    serialize_background_job,
)
from app.services.power_bi import list_power_bi_reports
from app.services.reports import (
    export_report,
    generate_report,
    get_report,
    list_reports,
    list_templates,
)
from app.services.teams import list_teams_channels

router = APIRouter()


@router.get("/templates", response_model=list[SummaryTemplateResponse])
def list_templates_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SummaryTemplateResponse]:
    return list_templates(db=db)


@router.get("/", response_model=ReportListResponse)
def list_reports_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportListResponse:
    return list_reports(db=db, current_user=current_user)


@router.post("/generate", response_model=ReportResponse)
def generate_report_route(
    payload: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    return generate_report(
        db=db,
        current_user=current_user,
        report_type=payload.report_type,
        template_id=payload.template_id,
        document_ids=payload.document_ids,
        power_bi_report_ids=payload.power_bi_report_ids,
        notes=payload.notes,
    )


@router.get("/power-bi-references", response_model=list[PowerBIReportReferenceResponse])
def list_power_bi_references_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PowerBIReportReferenceResponse]:
    return list_power_bi_reports(db=db, active_only=True)


@router.get("/teams-channels", response_model=list[TeamsChannelResponse])
def list_teams_channels_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TeamsChannelResponse]:
    return list_teams_channels(db=db, active_only=True)


@router.post("/{report_id}/deliver/email", response_model=BackgroundJobResponse)
def deliver_report_email_route(
    report_id: UUID,
    payload: DeliverReportEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BackgroundJobResponse:
    job = enqueue_report_delivery_job(
        db,
        report_id=report_id,
        current_user=current_user,
        delivery_type="email",
        recipients=payload.recipients,
        subject=payload.subject,
    )
    dispatch_background_job(background_tasks, job)
    return serialize_background_job(job)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report_route(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    return get_report(db=db, current_user=current_user, report_id=report_id)


@router.get("/{report_id}/export", response_model=ReportExportResponse)
def export_report_route(
    report_id: UUID,
    export_format: str = "markdown",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportExportResponse:
    return export_report(
        db=db,
        current_user=current_user,
        report_id=report_id,
        export_format=export_format,
    )


@router.post("/{report_id}/deliver/teams", response_model=BackgroundJobResponse)
def deliver_report_teams_route(
    report_id: UUID,
    payload: DeliverReportTeamsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BackgroundJobResponse:
    job = enqueue_report_delivery_job(
        db,
        report_id=report_id,
        current_user=current_user,
        delivery_type="teams",
        channel_id=payload.channel_id,
    )
    dispatch_background_job(background_tasks, job)
    return serialize_background_job(job)
