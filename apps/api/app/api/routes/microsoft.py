from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.job import BackgroundJobResponse
from app.schemas.microsoft import (
    MicrosoftConnectorRequest,
    MicrosoftConnectorResponse,
    MicrosoftConnectorUpdateRequest,
    MicrosoftOverviewResponse,
)
from app.schemas.power_bi import PowerBIReportReferenceRequest, PowerBIReportReferenceResponse
from app.schemas.teams import TeamsChannelRequest, TeamsChannelResponse
from app.services.background_jobs import (
    dispatch_background_job,
    dispatch_background_jobs,
    enqueue_connector_sync_job,
    enqueue_due_connector_sync_jobs,
    list_background_jobs,
    serialize_background_job,
)
from app.services.microsoft_connectors import (
    create_microsoft_connector,
    list_microsoft_connectors,
    list_microsoft_overview,
    update_microsoft_connector,
)
from app.services.power_bi import (
    create_power_bi_report,
    list_power_bi_reports,
    update_power_bi_report,
)
from app.services.teams import create_teams_channel, list_teams_channels, update_teams_channel

router = APIRouter()


@router.get("/overview", response_model=MicrosoftOverviewResponse)
def microsoft_overview_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MicrosoftOverviewResponse:
    return list_microsoft_overview(db)


@router.get("/connectors", response_model=list[MicrosoftConnectorResponse])
def list_microsoft_connectors_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[MicrosoftConnectorResponse]:
    return list_microsoft_connectors(db)


@router.post("/connectors", response_model=MicrosoftConnectorResponse, status_code=status.HTTP_201_CREATED)
def create_microsoft_connector_route(
    payload: MicrosoftConnectorRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MicrosoftConnectorResponse:
    connector = create_microsoft_connector(db=db, current_user=current_user, payload=payload)
    if payload.run_initial_sync:
        job = enqueue_connector_sync_job(
            db,
            connector_id=connector.id,
            current_user=current_user,
            reason="initial_sync",
        )
        dispatch_background_job(background_tasks, job)
    return connector


@router.patch("/connectors/{connector_id}", response_model=MicrosoftConnectorResponse)
def update_microsoft_connector_route(
    connector_id: UUID,
    payload: MicrosoftConnectorUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MicrosoftConnectorResponse:
    return update_microsoft_connector(
        db=db,
        connector_id=connector_id,
        payload=payload,
        current_user=current_user,
    )


@router.post("/connectors/{connector_id}/sync", response_model=BackgroundJobResponse, status_code=status.HTTP_202_ACCEPTED)
def sync_microsoft_connector_route(
    connector_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> BackgroundJobResponse:
    job = enqueue_connector_sync_job(
        db,
        connector_id=connector_id,
        current_user=current_user,
        reason="manual",
    )
    dispatch_background_job(background_tasks, job)
    return serialize_background_job(job)


@router.get("/jobs", response_model=list[BackgroundJobResponse])
def list_background_jobs_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[BackgroundJobResponse]:
    return list_background_jobs(db)


@router.post("/jobs/run-due", response_model=list[BackgroundJobResponse], status_code=status.HTTP_202_ACCEPTED)
def run_due_jobs_route(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[BackgroundJobResponse]:
    jobs = enqueue_due_connector_sync_jobs(db, current_user=current_user)
    dispatch_background_jobs(background_tasks, jobs)
    return [serialize_background_job(job) for job in jobs]


@router.get("/teams/channels", response_model=list[TeamsChannelResponse])
def list_teams_channels_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[TeamsChannelResponse]:
    return list_teams_channels(db=db)


@router.post("/teams/channels", response_model=TeamsChannelResponse, status_code=status.HTTP_201_CREATED)
def create_teams_channel_route(
    payload: TeamsChannelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> TeamsChannelResponse:
    return create_teams_channel(db=db, current_user=current_user, payload=payload)


@router.patch("/teams/channels/{channel_id}", response_model=TeamsChannelResponse)
def update_teams_channel_route(
    channel_id: UUID,
    payload: TeamsChannelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> TeamsChannelResponse:
    return update_teams_channel(
        db=db,
        channel_id=channel_id,
        payload=payload,
        current_user=current_user,
    )


@router.get("/power-bi/reports", response_model=list[PowerBIReportReferenceResponse])
def list_power_bi_reports_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[PowerBIReportReferenceResponse]:
    return list_power_bi_reports(db=db)


@router.post("/power-bi/reports", response_model=PowerBIReportReferenceResponse, status_code=status.HTTP_201_CREATED)
def create_power_bi_report_route(
    payload: PowerBIReportReferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> PowerBIReportReferenceResponse:
    return create_power_bi_report(db=db, current_user=current_user, payload=payload)


@router.patch("/power-bi/reports/{report_id}", response_model=PowerBIReportReferenceResponse)
def update_power_bi_report_route(
    report_id: UUID,
    payload: PowerBIReportReferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> PowerBIReportReferenceResponse:
    return update_power_bi_report(
        db=db,
        report_id=report_id,
        payload=payload,
        current_user=current_user,
    )
