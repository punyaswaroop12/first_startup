from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.document import Document
from app.models.power_bi import PowerBIReportReference
from app.models.report import Report
from app.models.user import User
from app.schemas.dashboard import (
    ActivityItem,
    DashboardOverviewResponse,
    MetricCard,
    PowerBIReportCard,
)


def build_dashboard_overview(db: Session, current_user: User) -> DashboardOverviewResponse:
    document_count = db.scalar(select(func.count(Document.id))) or 0
    report_count = db.scalar(select(func.count(Report.id))) or 0
    active_user_count = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0

    recent_activity = db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(5)).all()
    power_bi_reports = db.scalars(
        select(PowerBIReportReference)
        .where(PowerBIReportReference.is_active.is_(True))
        .order_by(PowerBIReportReference.name)
        .limit(4)
    ).all()

    metrics = [
        MetricCard(label="Documents", value=str(document_count), trend="Knowledge base footprint"),
        MetricCard(label="Reports", value=str(report_count), trend="Generated summaries"),
        MetricCard(label="Active Users", value=str(active_user_count), trend="Enabled accounts"),
        MetricCard(label="Your Role", value=current_user.role.value.title(), trend="Access profile"),
    ]
    activity = [
        ActivityItem(
            timestamp=item.created_at,
            title=item.event_type.replace("_", " ").title(),
            description=item.message,
        )
        for item in recent_activity
    ]
    return DashboardOverviewResponse(
        metrics=metrics,
        activity=activity,
        power_bi_reports=[
            PowerBIReportCard(
                id=str(report.id),
                name=report.name,
                workspace_name=report.workspace_name,
                report_url=report.report_url,
                description=report.description,
            )
            for report in power_bi_reports
        ],
    )
