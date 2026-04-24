from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import settings
from app.db.seed import main as seed_db
from app.db.session import SessionLocal
from app.integrations.microsoft.client import (
    MicrosoftIdentityClaims,
    MicrosoftTokenSet,
    get_microsoft_identity_client,
)
from app.main import app
from app.models.identity import MicrosoftTenant, UserIdentity


def test_login_flow() -> None:
    seed_db()
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ops-ai-demo.example.com", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["user"]["role"] == "admin"


def test_auth_providers_route_exposes_microsoft_flag(monkeypatch) -> None:
    seed_db()
    monkeypatch.setattr(settings, "microsoft_auth_enabled", True)
    monkeypatch.setattr(settings, "microsoft_client_id", "client-id")
    monkeypatch.setattr(settings, "microsoft_client_secret", "client-secret")

    client = TestClient(app)
    response = client.get("/api/v1/auth/providers")

    assert response.status_code == 200
    providers = {provider["key"]: provider for provider in response.json()["providers"]}
    assert providers["password"]["enabled"] is True
    assert providers["microsoft"]["enabled"] is True


def test_microsoft_callback_creates_internal_session(monkeypatch) -> None:
    class FakeMicrosoftClient:
        def __init__(self) -> None:
            self.state: str | None = None
            self.nonce: str | None = None

        def is_configured(self) -> bool:
            return True

        def build_authorization_url(self, *, state: str, nonce: str) -> str:
            self.state = state
            self.nonce = nonce
            return "https://login.microsoftonline.com/fake/oauth2/v2.0/authorize"

        def exchange_code_for_tokens(self, *, code: str) -> MicrosoftTokenSet:
            assert code == "test-code"
            return MicrosoftTokenSet(
                access_token="graph-token",
                id_token="id-token",
                refresh_token=None,
                expires_at=None,
                scope=["openid", "profile", "email", "User.Read"],
            )

        def validate_id_token(
            self,
            id_token: str,
            *,
            expected_nonce: str,
        ) -> MicrosoftIdentityClaims:
            assert id_token == "id-token"
            assert expected_nonce == self.nonce
            return MicrosoftIdentityClaims(
                subject="microsoft-oid-123",
                tenant_id="tenant-123",
                email="ops.admin@contoso.com",
                display_name="Ops Admin",
                given_name="Ops",
                family_name="Admin",
                raw_claims={
                    "iss": "https://login.microsoftonline.com/tenant-123/v2.0",
                    "oid": "microsoft-oid-123",
                    "tid": "tenant-123",
                },
            )

    seed_db()
    monkeypatch.setattr(settings, "microsoft_auth_enabled", True)
    monkeypatch.setattr(settings, "microsoft_client_id", "client-id")
    monkeypatch.setattr(settings, "microsoft_client_secret", "client-secret")
    monkeypatch.setattr(settings, "microsoft_admin_domains_raw", "contoso.com")
    fake_client = FakeMicrosoftClient()
    app.dependency_overrides[get_microsoft_identity_client] = lambda: fake_client

    client = TestClient(app)
    start_response = client.get("/api/v1/auth/microsoft/start", follow_redirects=False)
    assert start_response.status_code == 302
    assert start_response.headers["location"] == "https://login.microsoftonline.com/fake/oauth2/v2.0/authorize"
    assert fake_client.state

    callback_response = client.get(
        "/api/v1/auth/microsoft/callback",
        params={"code": "test-code", "state": fake_client.state},
        follow_redirects=False,
    )
    assert callback_response.status_code == 302

    redirect_url = urlparse(callback_response.headers["location"])
    fragment = parse_qs(redirect_url.fragment)
    access_token = fragment["access_token"][0]
    assert fragment["next"][0] == "/dashboard"

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ops.admin@contoso.com"
    assert me_response.json()["role"] == "admin"

    with SessionLocal() as db:
        tenant = db.scalar(
            select(MicrosoftTenant).where(MicrosoftTenant.tenant_id == "tenant-123")
        )
        identity = db.scalar(
            select(UserIdentity).where(UserIdentity.provider_subject == "microsoft-oid-123")
        )
        assert tenant is not None
        assert identity is not None
        assert identity.provider_email == "ops.admin@contoso.com"

    app.dependency_overrides.clear()
