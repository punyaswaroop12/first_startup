from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from app.core.config import settings


@dataclass(slots=True)
class TeamsDeliveryResult:
    provider: str
    preview_path: str | None = None


class PreviewTeamsProvider:
    def __init__(self) -> None:
        self.root = settings.teams_preview_dir
        self.root.mkdir(parents=True, exist_ok=True)

    def send_message(self, *, channel_name: str, title: str, text: str) -> TeamsDeliveryResult:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        safe_channel = "".join(character.lower() if character.isalnum() else "-" for character in channel_name).strip("-")
        filename = f"{timestamp}-{safe_channel or 'teams-preview'}.md"
        absolute_path = self.root / filename
        absolute_path.write_text(
            "\n".join(
                [
                    f"# {title}",
                    "",
                    f"Channel: {channel_name}",
                    "",
                    text,
                ]
            ),
            encoding="utf-8",
        )
        return TeamsDeliveryResult(provider="preview", preview_path=str(absolute_path))


class WebhookTeamsProvider:
    def send_message(
        self,
        *,
        webhook_url: str,
        channel_name: str,
        title: str,
        text: str,
    ) -> TeamsDeliveryResult:
        payload = {"text": f"**{title}**\n\n{text}"}
        response = httpx.post(
            webhook_url,
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        response.raise_for_status()
        return TeamsDeliveryResult(provider="webhook")


def get_teams_provider(delivery_type: str):
    configured_provider = settings.teams_provider.strip().lower()
    effective_provider = configured_provider or delivery_type
    if effective_provider == "webhook" and delivery_type == "webhook":
        return WebhookTeamsProvider()
    return PreviewTeamsProvider()
