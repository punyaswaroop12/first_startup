from datetime import datetime

from pydantic import BaseModel


class MetricCard(BaseModel):
    label: str
    value: str
    trend: str | None = None


class ActivityItem(BaseModel):
    timestamp: datetime
    title: str
    description: str


class PowerBIReportCard(BaseModel):
    id: str
    name: str
    workspace_name: str | None = None
    report_url: str
    description: str | None = None


class DashboardOverviewResponse(BaseModel):
    metrics: list[MetricCard]
    activity: list[ActivityItem]
    power_bi_reports: list[PowerBIReportCard]
