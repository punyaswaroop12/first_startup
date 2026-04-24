from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from time import sleep
from typing import Any
from urllib.parse import quote

import httpx
import structlog

from app.core.config import Settings, get_settings
from app.integrations.microsoft.client import MicrosoftIntegrationError

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class ResolvedMicrosoftTarget:
    source_url: str | None
    source_label: str
    resolved_target: dict[str, Any]
    permissions_metadata: dict[str, Any]


@dataclass(slots=True)
class MicrosoftGraphDeltaResult:
    items: list[dict[str, Any]]
    delta_link: str | None


class MicrosoftGraphClient:
    def __init__(self, app_settings: Settings | None = None, timeout_seconds: float = 20.0) -> None:
        self.settings = app_settings or get_settings()
        self.timeout_seconds = timeout_seconds
        self._app_token_cache: dict[str, tuple[str, datetime | None]] = {}

    def is_application_configured(self) -> bool:
        return bool(self.settings.microsoft_client_id and self.settings.microsoft_client_secret)

    def ensure_application_configured(self) -> None:
        if not self.is_application_configured():
            raise MicrosoftIntegrationError("Microsoft Graph application credentials are not configured.")

    def get_application_access_token(self, tenant_id: str) -> str:
        self.ensure_application_configured()
        cached = self._app_token_cache.get(tenant_id)
        if cached:
            token, expires_at = cached
            if not expires_at or expires_at > datetime.now(UTC) + timedelta(minutes=5):
                return token

        payload = self._request_json(
            "POST",
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.settings.microsoft_client_id,
                "client_secret": self.settings.microsoft_client_secret,
                "scope": self.settings.microsoft_graph_scope_value,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        expires_at = None
        if payload.get("expires_in"):
            expires_at = datetime.now(UTC) + timedelta(seconds=int(payload["expires_in"]))
        token = payload["access_token"]
        self._app_token_cache[tenant_id] = (token, expires_at)
        return token

    def resolve_sharepoint_target(
        self,
        *,
        tenant_id: str,
        site_hostname: str,
        site_path: str,
        drive_name: str | None,
        folder_path: str | None,
    ) -> ResolvedMicrosoftTarget:
        access_token = self.get_application_access_token(tenant_id)
        normalized_site_path = site_path.strip("/")
        site = self.request_json(
            f"/sites/{site_hostname}:/{normalized_site_path}",
            access_token=access_token,
        )
        drives_response = self.request_json(
            f"/sites/{site['id']}/drives",
            access_token=access_token,
        )
        drives = drives_response.get("value", [])
        if not drives:
            raise MicrosoftIntegrationError("No SharePoint document libraries were found for the site.")

        selected_drive = None
        if drive_name:
            selected_drive = next(
                (drive for drive in drives if str(drive.get("name", "")).lower() == drive_name.lower()),
                None,
            )
            if selected_drive is None:
                raise MicrosoftIntegrationError(
                    f"Drive '{drive_name}' was not found for SharePoint site {site_path}."
                )
        else:
            selected_drive = drives[0]

        target_folder = self._get_drive_item_by_path(
            drive_id=selected_drive["id"],
            access_token=access_token,
            folder_path=folder_path,
        )
        site_display = site.get("displayName") or site.get("name") or normalized_site_path
        effective_folder_path = target_folder.get("parentReference", {}).get("path") or folder_path or "/"
        source_label = f"SharePoint · {site_display} · {selected_drive.get('name', 'Documents')}"
        if folder_path:
            source_label = f"{source_label} · /{folder_path.strip('/')}"
        return ResolvedMicrosoftTarget(
            source_url=target_folder.get("webUrl") or selected_drive.get("webUrl") or site.get("webUrl"),
            source_label=source_label,
            resolved_target={
                "tenant_id": tenant_id,
                "site_id": site["id"],
                "site_name": site_display,
                "site_hostname": site_hostname,
                "site_path": f"/{normalized_site_path}",
                "drive_id": selected_drive["id"],
                "drive_name": selected_drive.get("name"),
                "folder_item_id": target_folder["id"],
                "folder_name": target_folder.get("name"),
                "folder_path": folder_path or "/",
                "folder_web_url": target_folder.get("webUrl"),
            },
            permissions_metadata={
                "service": "sharepoint",
                "drive_type": selected_drive.get("driveType"),
                "folder_reference": effective_folder_path,
            },
        )

    def resolve_onedrive_target(
        self,
        *,
        tenant_id: str,
        user_principal_name: str,
        folder_path: str | None,
    ) -> ResolvedMicrosoftTarget:
        access_token = self.get_application_access_token(tenant_id)
        drive = self.request_json(f"/users/{user_principal_name}/drive", access_token=access_token)
        target_folder = self._get_drive_item_by_path(
            drive_id=drive["id"],
            access_token=access_token,
            folder_path=folder_path,
        )
        source_label = f"OneDrive · {user_principal_name}"
        if folder_path:
            source_label = f"{source_label} · /{folder_path.strip('/')}"
        return ResolvedMicrosoftTarget(
            source_url=target_folder.get("webUrl") or drive.get("webUrl"),
            source_label=source_label,
            resolved_target={
                "tenant_id": tenant_id,
                "user_principal_name": user_principal_name,
                "drive_id": drive["id"],
                "drive_name": drive.get("name"),
                "folder_item_id": target_folder["id"],
                "folder_name": target_folder.get("name"),
                "folder_path": folder_path or "/",
                "folder_web_url": target_folder.get("webUrl"),
            },
            permissions_metadata={
                "service": "onedrive",
                "drive_type": drive.get("driveType"),
            },
        )

    def list_delta_items(
        self,
        *,
        tenant_id: str,
        drive_id: str,
        folder_item_id: str,
        delta_link: str | None,
    ) -> MicrosoftGraphDeltaResult:
        access_token = self.get_application_access_token(tenant_id)
        items: list[dict[str, Any]] = []
        next_url = delta_link or (
            f"{self.settings.microsoft_graph_base_url}/drives/{drive_id}/items/{folder_item_id}/delta"
            f"?$top={self.settings.microsoft_sync_page_size}"
        )
        latest_delta_link: str | None = delta_link
        while next_url:
            payload = self.request_json(next_url, access_token=access_token, absolute=next_url.startswith("http"))
            items.extend(payload.get("value", []))
            next_url = payload.get("@odata.nextLink")
            latest_delta_link = payload.get("@odata.deltaLink", latest_delta_link)
        return MicrosoftGraphDeltaResult(items=items, delta_link=latest_delta_link)

    def download_drive_item_content(self, *, tenant_id: str, drive_id: str, item_id: str) -> bytes:
        access_token = self.get_application_access_token(tenant_id)
        response = self._request(
            "GET",
            f"{self.settings.microsoft_graph_base_url}/drives/{drive_id}/items/{item_id}/content",
            headers={"Authorization": f"Bearer {access_token}"},
            follow_redirects=True,
        )
        return response.content

    def send_mail_as_user(
        self,
        *,
        tenant_id: str,
        sender_user_principal_name: str,
        recipients: list[str],
        subject: str,
        html: str,
        text: str,
    ) -> None:
        access_token = self.get_application_access_token(tenant_id)
        self._request(
            "POST",
            f"{self.settings.microsoft_graph_base_url}/users/{sender_user_principal_name}/sendMail",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": html},
                    "toRecipients": [
                        {"emailAddress": {"address": recipient}}
                        for recipient in recipients
                    ],
                    "internetMessageHeaders": [
                        {"name": "X-Ops-AI-Channel", "value": "reporting-assistant"}
                    ],
                },
                "saveToSentItems": True,
            },
        )

    def request_json(
        self,
        path_or_url: str,
        *,
        access_token: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        absolute: bool = False,
    ) -> dict[str, Any]:
        url = path_or_url if absolute else f"{self.settings.microsoft_graph_base_url}/{path_or_url.lstrip('/')}"
        return self._request_json(
            method,
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            json=json_body,
        )

    def _get_drive_item_by_path(
        self,
        *,
        drive_id: str,
        access_token: str,
        folder_path: str | None,
    ) -> dict[str, Any]:
        if not folder_path or folder_path.strip("/") == "":
            return self.request_json(
                f"/drives/{drive_id}/root",
                access_token=access_token,
            )
        encoded_path = quote(folder_path.strip("/"), safe="/")
        return self.request_json(
            f"/drives/{drive_id}/root:/{encoded_path}",
            access_token=access_token,
        )

    def _request_json(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self._request(method, url, **kwargs)
        try:
            return response.json()
        except ValueError as exc:
            raise MicrosoftIntegrationError("Microsoft Graph returned a non-JSON response.") from exc

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                response = httpx.request(method, url, timeout=self.timeout_seconds, **kwargs)
                if response.status_code in {429, 500, 502, 503, 504} and attempt < 3:
                    logger.warning(
                        "microsoft.graph.retry",
                        url=url,
                        method=method,
                        status_code=response.status_code,
                        attempt=attempt,
                    )
                    sleep(0.4 * attempt)
                    continue
                response.raise_for_status()
                return response
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < 3:
                    logger.warning(
                        "microsoft.graph.http_error",
                        url=url,
                        method=method,
                        attempt=attempt,
                        error=str(exc),
                    )
                    sleep(0.4 * attempt)
                    continue
        raise MicrosoftIntegrationError("Microsoft Graph request failed.") from last_error


@lru_cache(maxsize=1)
def get_microsoft_graph_client() -> MicrosoftGraphClient:
    return MicrosoftGraphClient()
