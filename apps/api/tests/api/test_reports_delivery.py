from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.seed import main as seed_db
from app.main import app


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ops-ai-demo.example.com", "password": "AdminPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_generate_report_with_power_bi_and_queue_deliveries() -> None:
    seed_db()
    client = TestClient(app)
    headers = auth_headers(client)

    documents_response = client.get("/api/v1/documents", headers=headers)
    document_id = documents_response.json()["items"][0]["id"]

    power_bi_response = client.get("/api/v1/reports/power-bi-references", headers=headers)
    assert power_bi_response.status_code == 200
    power_bi_report_id = power_bi_response.json()[0]["id"]

    teams_response = client.get("/api/v1/reports/teams-channels", headers=headers)
    assert teams_response.status_code == 200
    teams_channel_id = teams_response.json()[0]["id"]

    report_response = client.post(
        "/api/v1/reports/generate",
        headers=headers,
        json={
            "report_type": "operational",
            "document_ids": [document_id],
            "power_bi_report_ids": [power_bi_report_id],
            "notes": "Focus on safety and operating cadence.",
        },
    )
    assert report_response.status_code == 200
    report_payload = report_response.json()
    report_id = report_payload["id"]
    assert report_payload["linked_power_bi_reports"][0]["id"] == power_bi_report_id

    email_delivery_response = client.post(
        f"/api/v1/reports/{report_id}/deliver/email",
        headers=headers,
        json={"recipients": ["leadership@example.com"]},
    )
    teams_delivery_response = client.post(
        f"/api/v1/reports/{report_id}/deliver/teams",
        headers=headers,
        json={"channel_id": teams_channel_id},
    )

    assert email_delivery_response.status_code == 200
    assert teams_delivery_response.status_code == 200
    assert email_delivery_response.json()["job_type"] == "summary_delivery"
    assert teams_delivery_response.json()["job_type"] == "summary_delivery"

    jobs_response = client.get("/api/v1/admin/microsoft/jobs", headers=headers)
    assert jobs_response.status_code == 200
    delivery_jobs = [
        job
        for job in jobs_response.json()
        if job["job_type"] == "summary_delivery" and job["resource_id"] == report_id
    ]
    assert len(delivery_jobs) >= 2
    providers = {job["result_payload"].get("provider") for job in delivery_jobs}
    assert "preview" in providers

    email_previews = [job["result_payload"].get("preview_path") for job in delivery_jobs if job["result_payload"].get("preview_path")]
    assert email_previews
    for preview_path in email_previews:
        assert Path(preview_path).exists()
        assert str(preview_path).startswith(str(settings.repo_root / "storage"))
