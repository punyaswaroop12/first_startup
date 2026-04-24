from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.integrations.microsoft import (
    MicrosoftGraphClient,
    MicrosoftIntegrationError,
    ResolvedMicrosoftTarget,
    get_microsoft_graph_client,
)
from app.models.identity import MicrosoftTenant
from app.models.job import BackgroundJob, BackgroundJobStatus
from app.models.microsoft import (
    MicrosoftConnector,
    MicrosoftConnectorStatus,
    MicrosoftConnectorType,
    MicrosoftSyncedItem,
    MicrosoftSyncedItemState,
)
from app.models.power_bi import PowerBIReportReference
from app.models.teams import TeamsChannel
from app.models.user import User
from app.schemas.microsoft import (
    MicrosoftConnectorRequest,
    MicrosoftConnectorResponse,
    MicrosoftConnectorUpdateRequest,
    MicrosoftOverviewResponse,
    MicrosoftTenantSummaryResponse,
)
from app.services.audit import create_audit_log
from app.services.documents import ALLOWED_EXTENSIONS, delete_document, ingest_external_document


def list_microsoft_overview(db: Session) -> MicrosoftOverviewResponse:
    tenants = db.scalars(select(MicrosoftTenant).order_by(MicrosoftTenant.primary_domain)).all()
    connector_count = db.scalar(select(func.count()).select_from(MicrosoftConnector)) or 0
    teams_channel_count = db.scalar(select(func.count()).select_from(TeamsChannel)) or 0
    power_bi_report_count = db.scalar(select(func.count()).select_from(PowerBIReportReference)) or 0
    queued_job_count = db.scalar(
        select(func.count()).select_from(BackgroundJob).where(
            BackgroundJob.status.in_([BackgroundJobStatus.QUEUED, BackgroundJobStatus.RUNNING])
        )
    ) or 0
    default_teams_channel = db.scalar(
        select(TeamsChannel).where(
            TeamsChannel.is_active.is_(True),
            TeamsChannel.is_default.is_(True),
        )
    )
    return MicrosoftOverviewResponse(
        microsoft_auth_enabled=settings.microsoft_auth_enabled,
        microsoft_graph_app_configured=get_microsoft_graph_client().is_application_configured(),
        configured_tenant_id=settings.microsoft_tenant_id,
        email_provider=settings.email_provider,
        teams_provider=settings.teams_provider,
        microsoft_outlook_sender=settings.microsoft_outlook_sender or None,
        admin_emails=settings.microsoft_admin_emails,
        admin_domains=settings.microsoft_admin_domains,
        tenants=[
            MicrosoftTenantSummaryResponse(
                id=tenant.id,
                tenant_id=tenant.tenant_id,
                display_name=tenant.display_name,
                primary_domain=tenant.primary_domain,
                last_seen_at=tenant.last_seen_at,
            )
            for tenant in tenants
        ],
        connector_count=int(connector_count),
        teams_channel_count=int(teams_channel_count),
        power_bi_report_count=int(power_bi_report_count),
        queued_job_count=int(queued_job_count),
        default_teams_channel_name=default_teams_channel.name if default_teams_channel else None,
    )


def list_microsoft_connectors(db: Session) -> list[MicrosoftConnectorResponse]:
    connectors = db.scalars(
        select(MicrosoftConnector)
        .options(
            selectinload(MicrosoftConnector.microsoft_tenant),
            selectinload(MicrosoftConnector.synced_items),
        )
        .order_by(MicrosoftConnector.name)
    ).all()
    return [serialize_connector(connector) for connector in connectors]


def create_microsoft_connector(
    db: Session,
    *,
    current_user: User,
    payload: MicrosoftConnectorRequest,
    graph_client: MicrosoftGraphClient | None = None,
) -> MicrosoftConnectorResponse:
    existing = db.scalar(select(MicrosoftConnector).where(MicrosoftConnector.name == payload.name))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Connector name already exists.")

    graph_client = graph_client or get_microsoft_graph_client()
    tenant = resolve_microsoft_tenant(db, tenant_record_id=payload.microsoft_tenant_id)
    connector_type = parse_connector_type(payload.connector_type)
    resolved_target = resolve_connector_target(
        graph_client=graph_client,
        connector_type=connector_type,
        tenant=tenant,
        payload=payload,
    )
    resolved_target_payload = {**resolved_target.resolved_target, "source_label": resolved_target.source_label}
    now = datetime.now(UTC)
    connector = MicrosoftConnector(
        name=payload.name.strip(),
        description=payload.description,
        connector_type=connector_type,
        status=MicrosoftConnectorStatus.READY if payload.is_active else MicrosoftConnectorStatus.PAUSED,
        microsoft_tenant=tenant,
        created_by=current_user,
        is_active=payload.is_active,
        sync_frequency_minutes=payload.sync_frequency_minutes,
        source_url=resolved_target.source_url,
        config=build_connector_config(payload),
        resolved_target=resolved_target_payload,
        permissions_metadata=resolved_target.permissions_metadata,
        next_sync_at=now if payload.is_active else None,
    )
    db.add(connector)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="microsoft_connector_created",
        resource_type="microsoft_connector",
        resource_id=str(connector.id),
        message=f"Configured Microsoft connector {connector.name}",
        details={
            "connector_type": connector.connector_type.value,
            "tenant_id": tenant.tenant_id,
            "source_url": connector.source_url,
        },
    )
    db.commit()
    db.refresh(connector)
    return serialize_connector(load_connector(db, connector.id))


def update_microsoft_connector(
    db: Session,
    *,
    connector_id: UUID,
    payload: MicrosoftConnectorUpdateRequest,
    current_user: User,
) -> MicrosoftConnectorResponse:
    connector = load_connector(db, connector_id)
    if payload.name is not None:
        duplicate = db.scalar(
            select(MicrosoftConnector).where(
                MicrosoftConnector.name == payload.name,
                MicrosoftConnector.id != connector.id,
            )
        )
        if duplicate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Connector name already exists.")
        connector.name = payload.name.strip()
    connector.description = payload.description if payload.description is not None else connector.description
    if payload.default_tags is not None:
        connector.config = {**connector.config, "default_tags": normalize_tags(payload.default_tags)}
    if payload.sync_frequency_minutes is not None:
        connector.sync_frequency_minutes = payload.sync_frequency_minutes
    if payload.is_active is not None:
        connector.is_active = payload.is_active
        connector.status = (
            MicrosoftConnectorStatus.READY if payload.is_active else MicrosoftConnectorStatus.PAUSED
        )
        connector.next_sync_at = (
            datetime.now(UTC) + timedelta(minutes=connector.sync_frequency_minutes)
            if payload.is_active
            else None
        )
    create_audit_log(
        db,
        actor=current_user,
        event_type="microsoft_connector_updated",
        resource_type="microsoft_connector",
        resource_id=str(connector.id),
        message=f"Updated Microsoft connector {connector.name}",
        details={"is_active": connector.is_active},
    )
    db.commit()
    db.refresh(connector)
    return serialize_connector(load_connector(db, connector.id))


def load_connector(db: Session, connector_id: UUID) -> MicrosoftConnector:
    connector = db.scalar(
        select(MicrosoftConnector)
        .where(MicrosoftConnector.id == connector_id)
        .options(
            selectinload(MicrosoftConnector.microsoft_tenant),
            selectinload(MicrosoftConnector.created_by),
            selectinload(MicrosoftConnector.synced_items).selectinload(MicrosoftSyncedItem.document),
        )
    )
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Microsoft connector not found.")
    return connector


def sync_microsoft_connector(
    db: Session,
    *,
    connector_id: UUID,
    job: BackgroundJob,
    graph_client: MicrosoftGraphClient | None = None,
) -> dict:
    connector = load_connector(db, connector_id)
    graph_client = graph_client or get_microsoft_graph_client()
    connector.status = MicrosoftConnectorStatus.SYNCING
    connector.last_error = None
    db.commit()

    delta_result = graph_client.list_delta_items(
        tenant_id=connector.microsoft_tenant.tenant_id,
        drive_id=str(connector.resolved_target["drive_id"]),
        folder_item_id=str(connector.resolved_target["folder_item_id"]),
        delta_link=connector.last_delta_link,
    )

    counts = {"created": 0, "updated": 0, "deleted": 0, "skipped": 0, "failed": 0}
    default_tags = normalize_tags(connector.config.get("default_tags", []))
    for raw_item in delta_result.items:
        if raw_item.get("id") == connector.resolved_target.get("folder_item_id"):
            continue
        if raw_item.get("folder"):
            continue

        synced_item = get_or_create_synced_item(db, connector=connector, raw_item=raw_item, job=job)
        if raw_item.get("deleted"):
            handle_deleted_item(db, synced_item=synced_item, connector=connector)
            counts["deleted"] += 1
            continue

        try:
            file_name = str(raw_item.get("name") or synced_item.item_name)
            extension = Path(file_name).suffix.lower()
            if extension not in ALLOWED_EXTENSIONS:
                synced_item.state = MicrosoftSyncedItemState.SKIPPED
                synced_item.last_error = "Unsupported file type for ingestion."
                db.commit()
                counts["skipped"] += 1
                continue

            existing_document_id = synced_item.document_id
            content_bytes = graph_client.download_drive_item_content(
                tenant_id=connector.microsoft_tenant.tenant_id,
                drive_id=synced_item.drive_id,
                item_id=synced_item.external_item_id,
            )
            external_metadata = build_external_source_metadata(connector=connector, synced_item=synced_item)
            document_response = ingest_external_document(
                db=db,
                current_user=connector.created_by,
                filename=file_name,
                content_type=synced_item.content_type,
                file_bytes=content_bytes,
                tags=default_tags,
                version_label=build_version_label(raw_item),
                base_metadata=external_metadata,
                existing_document=synced_item.document,
            )
            synced_item.document_id = document_response.id
            synced_item.state = MicrosoftSyncedItemState.ACTIVE
            synced_item.last_error = None
            synced_item.last_synced_job = job
            db.commit()
            counts["updated" if existing_document_id else "created"] += 1
        except Exception as exc:  # noqa: BLE001
            synced_item.state = MicrosoftSyncedItemState.ERROR
            synced_item.last_error = str(exc)
            db.commit()
            counts["failed"] += 1

    connector.last_delta_link = delta_result.delta_link or connector.last_delta_link
    connector.last_synced_at = datetime.now(UTC)
    connector.next_sync_at = (
        connector.last_synced_at + timedelta(minutes=connector.sync_frequency_minutes)
        if connector.is_active
        else None
    )
    connector.status = MicrosoftConnectorStatus.READY if connector.is_active else MicrosoftConnectorStatus.PAUSED
    connector.last_error = None
    create_audit_log(
        db,
        actor=connector.created_by,
        event_type="microsoft_connector_synced",
        resource_type="microsoft_connector",
        resource_id=str(connector.id),
        message=f"Synced Microsoft connector {connector.name}",
        details=counts,
    )
    db.commit()
    return counts


def serialize_connector(connector: MicrosoftConnector) -> MicrosoftConnectorResponse:
    tenant_label = (
        connector.microsoft_tenant.display_name
        or connector.microsoft_tenant.primary_domain
        or connector.microsoft_tenant.tenant_id
    )
    active_items = [item for item in connector.synced_items if item.state == MicrosoftSyncedItemState.ACTIVE]
    return MicrosoftConnectorResponse(
        id=connector.id,
        name=connector.name,
        description=connector.description,
        connector_type=connector.connector_type.value,
        status=connector.status.value,
        is_active=connector.is_active,
        microsoft_tenant_id=connector.microsoft_tenant_id,
        tenant_label=tenant_label,
        source_url=connector.source_url,
        source_label=build_source_label(connector),
        default_tags=normalize_tags(connector.config.get("default_tags", [])),
        sync_frequency_minutes=connector.sync_frequency_minutes,
        last_synced_at=connector.last_synced_at,
        next_sync_at=connector.next_sync_at,
        last_error=connector.last_error,
        document_count=len([item for item in active_items if item.document_id]),
        synced_item_count=len(active_items),
        resolved_target=connector.resolved_target,
        permissions_metadata=connector.permissions_metadata,
        created_at=connector.created_at,
        updated_at=connector.updated_at,
    )


def resolve_microsoft_tenant(db: Session, tenant_record_id: UUID | None) -> MicrosoftTenant:
    if tenant_record_id:
        tenant = db.get(MicrosoftTenant, tenant_record_id)
        if not tenant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Microsoft tenant not found.")
        return tenant

    tenants = db.scalars(select(MicrosoftTenant).order_by(MicrosoftTenant.last_seen_at.desc())).all()
    if len(tenants) == 1:
        return tenants[0]
    if not tenants and settings.microsoft_tenant_id not in {"organizations", "common"}:
        tenant = MicrosoftTenant(
            tenant_id=settings.microsoft_tenant_id,
            display_name=settings.microsoft_tenant_id,
            primary_domain=settings.microsoft_tenant_id,
            tenant_metadata={"seeded_from_env": True},
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Select a Microsoft tenant before configuring a connector.",
    )


def resolve_connector_target(
    *,
    graph_client: MicrosoftGraphClient,
    connector_type: MicrosoftConnectorType,
    tenant: MicrosoftTenant,
    payload: MicrosoftConnectorRequest,
) -> ResolvedMicrosoftTarget:
    try:
        if connector_type == MicrosoftConnectorType.SHAREPOINT:
            return graph_client.resolve_sharepoint_target(
                tenant_id=tenant.tenant_id,
                site_hostname=payload.site_hostname or "",
                site_path=payload.site_path or "",
                drive_name=payload.drive_name,
                folder_path=payload.folder_path,
            )
        return graph_client.resolve_onedrive_target(
            tenant_id=tenant.tenant_id,
            user_principal_name=str(payload.user_principal_name),
            folder_path=payload.folder_path,
        )
    except MicrosoftIntegrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def parse_connector_type(value: str) -> MicrosoftConnectorType:
    try:
        return MicrosoftConnectorType(value.strip().lower())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid connector type.") from exc


def build_connector_config(payload: MicrosoftConnectorRequest) -> dict:
    return {
        "site_hostname": payload.site_hostname,
        "site_path": payload.site_path,
        "drive_name": payload.drive_name,
        "user_principal_name": str(payload.user_principal_name) if payload.user_principal_name else None,
        "folder_path": payload.folder_path or "/",
        "default_tags": normalize_tags(payload.default_tags),
    }


def normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    for tag in tags:
        value = tag.strip().lower()
        if value and value not in normalized:
            normalized.append(value)
    return normalized


def get_or_create_synced_item(
    db: Session,
    *,
    connector: MicrosoftConnector,
    raw_item: dict,
    job: BackgroundJob,
) -> MicrosoftSyncedItem:
    synced_item = db.scalar(
        select(MicrosoftSyncedItem).where(
            MicrosoftSyncedItem.connector_id == connector.id,
            MicrosoftSyncedItem.external_item_id == str(raw_item.get("id")),
        )
    )
    if synced_item is None:
        synced_item = MicrosoftSyncedItem(
            connector=connector,
            external_item_id=str(raw_item.get("id")),
            drive_id=str(raw_item.get("parentReference", {}).get("driveId") or connector.resolved_target["drive_id"]),
            item_name=str(raw_item.get("name") or "document"),
        )
        db.add(synced_item)

    parent_reference = raw_item.get("parentReference", {}) or {}
    synced_item.parent_external_item_id = parent_reference.get("id")
    synced_item.item_name = str(raw_item.get("name") or synced_item.item_name or "document")
    synced_item.item_path = build_item_path(raw_item)
    synced_item.source_url = raw_item.get("webUrl")
    synced_item.content_type = raw_item.get("file", {}).get("mimeType")
    synced_item.file_extension = Path(synced_item.item_name).suffix.lower() or None
    synced_item.last_modified_at = parse_graph_datetime(raw_item.get("lastModifiedDateTime"))
    synced_item.etag = raw_item.get("eTag")
    synced_item.ctag = raw_item.get("cTag")
    synced_item.item_metadata = raw_item
    synced_item.permissions_metadata = {
        "shared": raw_item.get("shared"),
        "lastModifiedBy": raw_item.get("lastModifiedBy"),
        "createdBy": raw_item.get("createdBy"),
    }
    synced_item.last_synced_job = job
    db.flush()
    return synced_item


def handle_deleted_item(
    db: Session,
    *,
    synced_item: MicrosoftSyncedItem,
    connector: MicrosoftConnector,
) -> None:
    document_id = synced_item.document_id
    if document_id:
        synced_item.document_id = None
        db.flush()
        delete_document(db=db, document_id=document_id, current_user=connector.created_by)
    synced_item.state = MicrosoftSyncedItemState.DELETED
    synced_item.last_error = None
    db.commit()


def build_version_label(raw_item: dict) -> str | None:
    last_modified = raw_item.get("lastModifiedDateTime")
    if last_modified:
        return str(last_modified).replace("T", " ")[:19]
    return raw_item.get("eTag")


def build_item_path(raw_item: dict) -> str | None:
    parent_path = str((raw_item.get("parentReference") or {}).get("path") or "")
    item_name = str(raw_item.get("name") or "")
    if ":" in parent_path:
        parent_path = parent_path.split(":", 1)[1]
    if not parent_path:
        return f"/{item_name}" if item_name else None
    return f"{parent_path.rstrip('/')}/{item_name}".replace("//", "/")


def parse_graph_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_external_source_metadata(*, connector: MicrosoftConnector, synced_item: MicrosoftSyncedItem) -> dict:
    return {
        "external_source": {
            "kind": connector.connector_type.value,
            "connector_id": str(connector.id),
            "connector_name": connector.name,
            "tenant_id": connector.microsoft_tenant.tenant_id,
            "source_label": build_source_label(connector),
            "path": synced_item.item_path,
            "source_url": synced_item.source_url or connector.source_url,
            "drive_id": synced_item.drive_id,
            "external_item_id": synced_item.external_item_id,
            "parent_external_item_id": synced_item.parent_external_item_id,
            "last_modified_at": (
                synced_item.last_modified_at.isoformat() if synced_item.last_modified_at else None
            ),
            "permissions": synced_item.permissions_metadata,
            "resolved_target": connector.resolved_target,
        }
    }


def build_source_label(connector: MicrosoftConnector) -> str:
    if connector.resolved_target.get("source_label"):
        return str(connector.resolved_target["source_label"])
    if connector.connector_type == MicrosoftConnectorType.SHAREPOINT:
        return connector.resolved_target.get("site_name") or connector.name
    return connector.resolved_target.get("user_principal_name") or connector.name
