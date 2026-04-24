from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from time import sleep
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
import structlog
from jwt import PyJWKClient

from app.core.config import Settings, get_settings

logger = structlog.get_logger(__name__)


class MicrosoftIntegrationError(RuntimeError):
    pass


@dataclass(slots=True)
class MicrosoftOIDCConfiguration:
    authorization_endpoint: str
    token_endpoint: str
    issuer: str
    jwks_uri: str


@dataclass(slots=True)
class MicrosoftTokenSet:
    access_token: str
    id_token: str
    refresh_token: str | None
    expires_at: datetime | None
    scope: list[str]


@dataclass(slots=True)
class MicrosoftIdentityClaims:
    subject: str
    tenant_id: str
    email: str
    display_name: str
    given_name: str | None
    family_name: str | None
    raw_claims: dict[str, Any]


class MicrosoftIdentityClient:
    def __init__(self, app_settings: Settings | None = None, timeout_seconds: float = 10.0) -> None:
        self.settings = app_settings or get_settings()
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return bool(
            self.settings.microsoft_auth_enabled
            and self.settings.microsoft_client_id
            and self.settings.microsoft_client_secret
        )

    def ensure_configured(self) -> None:
        if not self.is_configured():
            raise MicrosoftIntegrationError("Microsoft authentication is not configured.")

    def get_openid_configuration(self, tenant: str | None = None) -> MicrosoftOIDCConfiguration:
        authority = tenant or self.settings.microsoft_tenant_id
        metadata_url = f"https://login.microsoftonline.com/{authority}/v2.0/.well-known/openid-configuration"
        payload = self._request_json("GET", metadata_url)
        return MicrosoftOIDCConfiguration(
            authorization_endpoint=payload["authorization_endpoint"],
            token_endpoint=payload["token_endpoint"],
            issuer=payload["issuer"],
            jwks_uri=payload["jwks_uri"],
        )

    def build_authorization_url(self, *, state: str, nonce: str) -> str:
        self.ensure_configured()
        config = self.get_openid_configuration()
        query = urlencode(
            {
                "client_id": self.settings.microsoft_client_id,
                "response_type": "code",
                "redirect_uri": self.settings.microsoft_redirect_uri,
                "response_mode": "query",
                "scope": " ".join(self.settings.microsoft_scopes),
                "state": state,
                "nonce": nonce,
                "prompt": "select_account",
            }
        )
        return f"{config.authorization_endpoint}?{query}"

    def exchange_code_for_tokens(self, *, code: str) -> MicrosoftTokenSet:
        self.ensure_configured()
        config = self.get_openid_configuration()
        payload = self._request_json(
            "POST",
            config.token_endpoint,
            data={
                "grant_type": "authorization_code",
                "client_id": self.settings.microsoft_client_id,
                "client_secret": self.settings.microsoft_client_secret,
                "code": code,
                "redirect_uri": self.settings.microsoft_redirect_uri,
                "scope": " ".join(self.settings.microsoft_scopes),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        expires_at = None
        expires_in = payload.get("expires_in")
        if expires_in:
            expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))
        return MicrosoftTokenSet(
            access_token=payload["access_token"],
            id_token=payload["id_token"],
            refresh_token=payload.get("refresh_token"),
            expires_at=expires_at,
            scope=payload.get("scope", "").split(),
        )

    def validate_id_token(self, id_token: str, *, expected_nonce: str) -> MicrosoftIdentityClaims:
        unverified_claims = jwt.decode(
            id_token,
            options={"verify_signature": False, "verify_aud": False, "verify_exp": False},
            algorithms=["RS256"],
        )
        tenant_id = str(unverified_claims.get("tid") or "").strip()
        if not tenant_id:
            raise MicrosoftIntegrationError("Microsoft ID token is missing a tenant identifier.")

        if self.settings.microsoft_tenant_id not in {"common", "organizations", tenant_id}:
            raise MicrosoftIntegrationError("Microsoft tenant does not match the configured authority.")

        config = self.get_openid_configuration(tenant=tenant_id)
        signing_key = PyJWKClient(config.jwks_uri).get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.settings.microsoft_client_id,
            issuer=config.issuer,
        )

        if claims.get("nonce") != expected_nonce:
            raise MicrosoftIntegrationError("Microsoft nonce validation failed.")

        email = str(
            claims.get("preferred_username") or claims.get("email") or claims.get("upn") or ""
        ).strip()
        subject = str(claims.get("oid") or claims.get("sub") or "").strip()
        if not email or not subject:
            raise MicrosoftIntegrationError("Microsoft ID token is missing required user claims.")

        return MicrosoftIdentityClaims(
            subject=subject,
            tenant_id=tenant_id,
            email=email.lower(),
            display_name=str(claims.get("name") or email).strip(),
            given_name=claims.get("given_name"),
            family_name=claims.get("family_name"),
            raw_claims=claims,
        )

    def request_graph(
        self,
        path: str,
        *,
        access_token: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.settings.microsoft_graph_base_url}/{path.lstrip('/')}"
        return self._request_json(
            method,
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            json=json_body,
        )

    def _request_json(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self._request(method, url, **kwargs)
        try:
            return response.json()
        except ValueError as exc:
            raise MicrosoftIntegrationError("Microsoft returned a non-JSON response.") from exc

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                response = httpx.request(method, url, timeout=self.timeout_seconds, **kwargs)
                if response.status_code in {429, 500, 502, 503, 504} and attempt < 3:
                    logger.warning(
                        "microsoft.request.retry",
                        url=url,
                        method=method,
                        status_code=response.status_code,
                        attempt=attempt,
                    )
                    sleep(0.25 * attempt)
                    continue
                response.raise_for_status()
                return response
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < 3:
                    logger.warning(
                        "microsoft.request.http_error",
                        url=url,
                        method=method,
                        attempt=attempt,
                        error=str(exc),
                    )
                    sleep(0.25 * attempt)
                    continue
        raise MicrosoftIntegrationError("Microsoft request failed.") from last_error


@lru_cache(maxsize=1)
def get_microsoft_identity_client() -> MicrosoftIdentityClient:
    return MicrosoftIdentityClient()
