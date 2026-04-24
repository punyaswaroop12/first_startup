from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class MicrosoftTenantSummaryResponse(BaseModel):
    id: UUID
    tenant_id: str
    display_name: str | None
    primary_domain: str | None
    last_seen_at: datetime


class MicrosoftConnectorRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    connector_type: str
    microsoft_tenant_id: UUID | None = None
    site_hostname: str | None = None
    site_path: str | None = None
    drive_name: str | None = None
    user_principal_name: EmailStr | None = None
    folder_path: str | None = None
    default_tags: list[str] = Field(default_factory=list)
    sync_frequency_minutes: int = Field(ge=15, le=10080)
    is_active: bool = True
    run_initial_sync: bool = True

    @model_validator(mode="after")
    def validate_for_type(self) -> "MicrosoftConnectorRequest":
        connector_type = self.connector_type.strip().lower()
        if connector_type == "sharepoint":
            if not self.site_hostname or not self.site_path:
                raise ValueError("SharePoint connectors require a site hostname and site path.")
        elif connector_type == "onedrive":
            if not self.user_principal_name:
                raise ValueError("OneDrive connectors require a user principal name.")
        else:
            raise ValueError("Unsupported Microsoft connector type.")
        return self


class MicrosoftConnectorUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    default_tags: list[str] | None = None
    sync_frequency_minutes: int | None = Field(default=None, ge=15, le=10080)
    is_active: bool | None = None


class MicrosoftConnectorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    connector_type: str
    status: str
    is_active: bool
    microsoft_tenant_id: UUID
    tenant_label: str
    source_url: str | None
    source_label: str
    default_tags: list[str]
    sync_frequency_minutes: int
    last_synced_at: datetime | None
    next_sync_at: datetime | None
    last_error: str | None
    document_count: int
    synced_item_count: int
    resolved_target: dict
    permissions_metadata: dict
    created_at: datetime
    updated_at: datetime


class MicrosoftOverviewResponse(BaseModel):
    microsoft_auth_enabled: bool
    microsoft_graph_app_configured: bool
    configured_tenant_id: str
    email_provider: str
    teams_provider: str
    microsoft_outlook_sender: str | None
    admin_emails: list[str]
    admin_domains: list[str]
    tenants: list[MicrosoftTenantSummaryResponse]
    connector_count: int
    teams_channel_count: int
    power_bi_report_count: int
    queued_job_count: int
    default_teams_channel_name: str | None
