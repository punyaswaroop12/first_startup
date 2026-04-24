from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.automation import AutomationRule, AutomationTriggerType
from app.models.document import Document, Tag
from app.models.power_bi import PowerBIReportReference
from app.models.report import SummaryTemplate
from app.models.teams import TeamsChannel, TeamsChannelDeliveryType
from app.models.user import User, UserRole
from app.services.documents import ingest_document_upload


def seed_users() -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == settings.default_admin_email))
        if not admin:
            db.add(
                User(
                    email=settings.default_admin_email,
                    full_name="Morgan Admin",
                    role=UserRole.ADMIN,
                    hashed_password=hash_password(settings.default_admin_password),
                )
            )

        analyst = db.scalar(select(User).where(User.email == settings.default_user_email))
        if not analyst:
            db.add(
                User(
                    email=settings.default_user_email,
                    full_name="Avery Analyst",
                    role=UserRole.USER,
                    hashed_password=hash_password(settings.default_user_password),
                )
            )

        for name, description, color in [
            ("safety", "Safety and compliance material", "amber"),
            ("operations", "Day-to-day operational procedures", "teal"),
            ("compliance", "Regulatory and policy documents", "slate"),
        ]:
            tag = db.scalar(select(Tag).where(Tag.name == name))
            if not tag:
                db.add(Tag(name=name, description=description, color=color))

        for name, report_type, template_key, description in [
            ("Executive Summary", "executive", "executive/default", "High-level weekly briefing"),
            ("Operational Summary", "operational", "operational/default", "Operational updates and issues"),
            (
                "Document Changes Summary",
                "document_changes",
                "document_changes/default",
                "Summary of new and changed documents",
            ),
        ]:
            template = db.scalar(select(SummaryTemplate).where(SummaryTemplate.name == name))
            if not template:
                db.add(
                    SummaryTemplate(
                        name=name,
                        report_type=report_type,
                        template_key=template_key,
                        description=description,
                        is_default=True,
                    )
                )

        db.commit()


def seed_sample_documents() -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == settings.default_admin_email))
        if not admin:
            return

        samples = [
            ("safety-protocol.txt", "safety, compliance", "3.2"),
            ("maintenance-sop.txt", "operations", "1.0"),
        ]
        seed_dir = settings.repo_root / "seed-data" / "documents"
        for filename, tags, version_label in samples:
            path = seed_dir / filename
            if not path.exists():
                continue

            already_present = db.scalar(select(Document).where(Document.name == filename))
            if already_present:
                continue
            ingest_document_upload(
                db=db,
                current_user=admin,
                filename=filename,
                content_type="text/plain",
                file_bytes=path.read_bytes(),
                tags_raw=tags,
                version_label=version_label,
            )


def seed_automation_rules() -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == settings.default_admin_email))
        if not admin:
            return

        existing = db.scalar(
            select(AutomationRule).where(AutomationRule.name == "Safety upload summary + notify")
        )
        if existing:
            return

        db.add(
            AutomationRule(
                name="Safety upload summary + notify",
                description="When a safety-tagged document is uploaded, generate an operational summary and notify the admin inbox.",
                trigger_type=AutomationTriggerType.DOCUMENT_UPLOADED,
                condition_config={"tags_any": ["safety"]},
                action_config=[
                    {"type": "generate_summary", "report_type": "operational", "notes": "Automation-generated follow-up summary for safety-tagged upload."},
                    {"type": "notify_recipients", "recipients": [settings.default_admin_email], "subject": "Safety document uploaded"},
                ],
                is_active=True,
                created_by=admin,
            )
        )

        report_delivery_rule = db.scalar(
            select(AutomationRule).where(AutomationRule.name == "Executive report delivery")
        )
        if not report_delivery_rule:
            db.add(
                AutomationRule(
                    name="Executive report delivery",
                    description="When an executive report is generated, email it to the admin inbox and post the summary to Teams.",
                    trigger_type=AutomationTriggerType.REPORT_GENERATED,
                    condition_config={"report_type": "executive"},
                    action_config=[
                        {
                            "type": "deliver_report_email",
                            "recipients": [settings.default_admin_email],
                            "subject": "Executive report ready",
                        },
                        {"type": "deliver_report_teams"},
                    ],
                    is_active=True,
                    created_by=admin,
                )
            )
        db.commit()


def seed_delivery_and_power_bi() -> None:
    power_bi_description = "Configured Power BI reference for linked reporting context."
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.email == settings.default_admin_email))
        if not admin:
            return

        default_channel = db.scalar(select(TeamsChannel).where(TeamsChannel.name == "Operations Leadership"))
        if not default_channel:
            db.add(
                TeamsChannel(
                    name="Operations Leadership",
                    description="Default Teams destination for weekly leadership updates and flags.",
                    channel_label="Operations Leadership",
                    delivery_type=TeamsChannelDeliveryType.PREVIEW,
                    is_active=True,
                    is_default=True,
                    created_by=admin,
                )
            )

        for name, workspace, report_url, tags in [
            (
                "Operations KPI Board",
                "Ops Executive Analytics",
                "https://app.powerbi.com/groups/me/reports/operations-kpi-board",
                ["operations", "weekly"],
            ),
            (
                "Safety Incident Trends",
                "Safety Intelligence",
                "https://app.powerbi.com/groups/me/reports/safety-incident-trends",
                ["safety", "risk"],
            ),
        ]:
            report = db.scalar(select(PowerBIReportReference).where(PowerBIReportReference.name == name))
            if not report:
                db.add(
                    PowerBIReportReference(
                        name=name,
                        description=power_bi_description,
                        workspace_name=workspace,
                        report_url=report_url,
                        tags=tags,
                        is_active=True,
                        created_by=admin,
                    )
                )
            elif report.description != power_bi_description:
                report.description = power_bi_description
        db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    Path(settings.local_storage_root).mkdir(parents=True, exist_ok=True)
    Path(settings.email_preview_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.teams_preview_dir).mkdir(parents=True, exist_ok=True)
    seed_users()
    seed_delivery_and_power_bi()
    seed_sample_documents()
    seed_automation_rules()


if __name__ == "__main__":
    main()
