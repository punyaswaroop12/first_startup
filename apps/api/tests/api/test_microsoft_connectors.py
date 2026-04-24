from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.seed import main as seed_db
from app.db.session import SessionLocal
from app.integrations.microsoft.graph import MicrosoftGraphDeltaResult, ResolvedMicrosoftTarget
from app.main import app
from app.models.document import Document
from app.models.identity import MicrosoftTenant
from app.models.job import BackgroundJob, BackgroundJobStatus


class FakeGraphClient:
    def is_application_configured(self) -> bool:
        return True

    def resolve_sharepoint_target(
        self,
        *,
        tenant_id: str,
        site_hostname: str,
        site_path: str,
        drive_name: str | None,
        folder_path: str | None,
    ) -> ResolvedMicrosoftTarget:
        return ResolvedMicrosoftTarget(
            source_url="https://contoso.sharepoint.com/sites/Operations/Shared%20Documents/Safety",
            source_label="SharePoint · Operations · Documents",
            resolved_target={
                "tenant_id": tenant_id,
                "site_id": "site-123",
                "site_name": "Operations",
                "site_hostname": site_hostname,
                "site_path": f"/{site_path.strip('/')}",
                "drive_id": "drive-123",
                "drive_name": drive_name or "Documents",
                "folder_item_id": "folder-123",
                "folder_name": "Safety",
                "folder_path": folder_path or "/",
                "folder_web_url": "https://contoso.sharepoint.com/sites/Operations/Shared%20Documents/Safety",
            },
            permissions_metadata={"service": "sharepoint"},
        )

    def list_delta_items(
        self,
        *,
        tenant_id: str,
        drive_id: str,
        folder_item_id: str,
        delta_link: str | None,
    ) -> MicrosoftGraphDeltaResult:
        return MicrosoftGraphDeltaResult(
            items=[
                {
                    "id": "file-123",
                    "name": "safety-sync.txt",
                    "webUrl": "https://contoso.sharepoint.com/sites/Operations/Shared%20Documents/Safety/safety-sync.txt",
                    "lastModifiedDateTime": "2026-04-24T17:45:00Z",
                    "eTag": "etag-123",
                    "cTag": "ctag-123",
                    "file": {"mimeType": "text/plain"},
                    "parentReference": {
                        "driveId": drive_id,
                        "id": folder_item_id,
                        "path": "/drive/root:/Shared Documents/Safety",
                    },
                }
            ],
            delta_link="delta-token-1",
        )

    def download_drive_item_content(self, *, tenant_id: str, drive_id: str, item_id: str) -> bytes:
        return (
            b"Safety escalation policy\n"
            b"If an incident occurs, notify the operations manager within 30 minutes.\n"
        )


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ops-ai-demo.example.com", "password": "AdminPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def ensure_tenant() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(MicrosoftTenant).where(MicrosoftTenant.tenant_id == "tenant-123"))
        if not existing:
            db.add(
                MicrosoftTenant(
                    tenant_id="tenant-123",
                    display_name="Contoso Operations",
                    primary_domain="contoso.com",
                    tenant_metadata={"source": "test"},
                )
            )
            db.commit()


def test_create_connector_and_initial_sync(monkeypatch) -> None:
    seed_db()
    ensure_tenant()
    monkeypatch.setattr("app.services.microsoft_connectors.get_microsoft_graph_client", lambda: FakeGraphClient())

    client = TestClient(app)
    headers = auth_headers(client)
    with SessionLocal() as db:
        tenant = db.scalar(select(MicrosoftTenant).where(MicrosoftTenant.tenant_id == "tenant-123"))
        tenant_id = str(tenant.id)

    create_response = client.post(
        "/api/v1/admin/microsoft/connectors",
        headers=headers,
        json={
            "name": "Contoso Safety SharePoint",
            "description": "Sync safety policies",
            "connector_type": "sharepoint",
            "microsoft_tenant_id": tenant_id,
            "site_hostname": "contoso.sharepoint.com",
            "site_path": "sites/Operations",
            "drive_name": "Documents",
            "folder_path": "Shared Documents/Safety",
            "default_tags": ["safety", "operations"],
            "sync_frequency_minutes": 1440,
            "is_active": True,
            "run_initial_sync": True,
        },
    )

    assert create_response.status_code == 201
    payload = create_response.json()
    assert payload["connector_type"] == "sharepoint"
    assert payload["status"] in {"ready", "syncing"}

    connectors_response = client.get("/api/v1/admin/microsoft/connectors", headers=headers)
    connectors = connectors_response.json()
    assert connectors[0]["document_count"] == 1
    assert connectors[0]["last_synced_at"] is not None

    jobs_response = client.get("/api/v1/admin/microsoft/jobs", headers=headers)
    jobs = jobs_response.json()
    connector_sync_job = next(job for job in jobs if job["job_type"] == "connector_sync")
    assert connector_sync_job["status"] == "succeeded"

    documents_response = client.get("/api/v1/documents", headers=headers)
    documents = documents_response.json()["items"]
    synced_document = next(document for document in documents if document["name"] == "safety-sync.txt")
    assert synced_document["external_source_kind"] == "sharepoint"
    assert synced_document["source_url"]

    with SessionLocal() as db:
        assert db.scalar(select(Document).where(Document.name == "safety-sync.txt")) is not None
        job = db.scalar(select(BackgroundJob).order_by(BackgroundJob.created_at.desc()))
        assert job is not None
        assert job.status == BackgroundJobStatus.SUCCEEDED
