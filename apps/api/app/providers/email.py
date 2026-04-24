from __future__ import annotations

import smtplib
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import EmailMessage

from app.core.config import settings
from app.integrations.microsoft import MicrosoftIntegrationError, get_microsoft_graph_client


@dataclass(slots=True)
class EmailDeliveryResult:
    provider: str
    preview_path: str | None = None
    message_id: str | None = None


class PreviewEmailProvider:
    def __init__(self) -> None:
        self.root = settings.email_preview_dir
        self.root.mkdir(parents=True, exist_ok=True)

    def send_email(self, *, recipients: list[str], subject: str, html: str, text: str) -> EmailDeliveryResult:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        safe_subject = "".join(character.lower() if character.isalnum() else "-" for character in subject).strip("-")
        filename = f"{timestamp}-{safe_subject or 'email-preview'}.html"
        absolute_path = self.root / filename
        absolute_path.write_text(
            "\n".join(
                [
                    f"<h1>{subject}</h1>",
                    f"<p><strong>To:</strong> {', '.join(recipients)}</p>",
                    html,
                    f"<pre>{text}</pre>",
                ]
            ),
            encoding="utf-8",
        )
        return EmailDeliveryResult(provider="preview", preview_path=str(absolute_path))


class SMTPEmailProvider:
    def send_email(self, *, recipients: list[str], subject: str, html: str, text: str) -> EmailDeliveryResult:
        message = EmailMessage()
        message["From"] = settings.mail_from
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.set_content(text)
        message.add_alternative(html, subtype="html")

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return EmailDeliveryResult(provider="smtp", message_id=message["Message-ID"])


class GraphEmailProvider:
    def send_email(self, *, recipients: list[str], subject: str, html: str, text: str) -> EmailDeliveryResult:
        if not settings.microsoft_outlook_sender:
            raise MicrosoftIntegrationError("MICROSOFT_OUTLOOK_SENDER must be configured for Graph email.")
        graph_client = get_microsoft_graph_client()
        tenant_id = settings.microsoft_tenant_id
        if tenant_id in {"organizations", "common"}:
            raise MicrosoftIntegrationError(
                "Use a specific tenant ID for Graph email delivery instead of organizations/common."
            )
        graph_client.send_mail_as_user(
            tenant_id=tenant_id,
            sender_user_principal_name=settings.microsoft_outlook_sender,
            recipients=recipients,
            subject=subject,
            html=html,
            text=text,
        )
        return EmailDeliveryResult(provider="graph")


def get_email_provider():
    if settings.email_provider == "graph":
        return GraphEmailProvider()
    if settings.email_provider == "smtp":
        return SMTPEmailProvider()
    return PreviewEmailProvider()
