from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.teams import TeamsChannel, TeamsChannelDeliveryType
from app.models.user import User
from app.providers.teams import TeamsDeliveryResult, get_teams_provider
from app.schemas.teams import TeamsChannelRequest, TeamsChannelResponse
from app.services.audit import create_audit_log


def list_teams_channels(db: Session, *, active_only: bool = False) -> list[TeamsChannelResponse]:
    statement = select(TeamsChannel).order_by(TeamsChannel.name)
    if active_only:
        statement = statement.where(TeamsChannel.is_active.is_(True))
    channels = db.scalars(statement).all()
    return [serialize_teams_channel(channel) for channel in channels]


def create_teams_channel(
    db: Session,
    *,
    current_user: User,
    payload: TeamsChannelRequest,
) -> TeamsChannelResponse:
    existing = db.scalar(select(TeamsChannel).where(TeamsChannel.name == payload.name))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teams channel name already exists.")
    if payload.is_default:
        clear_default_channel(db)
    channel = TeamsChannel(
        name=payload.name,
        description=payload.description,
        channel_label=payload.channel_label,
        delivery_type=TeamsChannelDeliveryType(payload.delivery_type),
        webhook_url=payload.webhook_url,
        is_active=payload.is_active,
        is_default=payload.is_default,
        created_by=current_user,
    )
    db.add(channel)
    db.flush()
    create_audit_log(
        db,
        actor=current_user,
        event_type="teams_channel_configured",
        resource_type="teams_channel",
        resource_id=str(channel.id),
        message=f"Configured Teams channel {channel.name}",
        details={"delivery_type": channel.delivery_type.value},
    )
    db.commit()
    db.refresh(channel)
    return serialize_teams_channel(channel)


def update_teams_channel(
    db: Session,
    *,
    channel_id: UUID,
    payload: TeamsChannelRequest,
    current_user: User,
) -> TeamsChannelResponse:
    channel = db.get(TeamsChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teams channel not found.")
    if payload.is_default:
        clear_default_channel(db)
    channel.name = payload.name
    channel.description = payload.description
    channel.channel_label = payload.channel_label
    channel.delivery_type = TeamsChannelDeliveryType(payload.delivery_type)
    channel.webhook_url = payload.webhook_url
    channel.is_active = payload.is_active
    channel.is_default = payload.is_default
    create_audit_log(
        db,
        actor=current_user,
        event_type="teams_channel_updated",
        resource_type="teams_channel",
        resource_id=str(channel.id),
        message=f"Updated Teams channel {channel.name}",
        details={"is_default": channel.is_default, "is_active": channel.is_active},
    )
    db.commit()
    db.refresh(channel)
    return serialize_teams_channel(channel)


def send_teams_message(
    db: Session,
    *,
    title: str,
    text: str,
    current_user: User | None,
    channel_id: UUID | None = None,
) -> TeamsDeliveryResult:
    channel = resolve_channel(db, channel_id=channel_id)
    provider = get_teams_provider(channel.delivery_type.value if channel else "preview")
    if channel and channel.delivery_type == TeamsChannelDeliveryType.WEBHOOK:
        result = provider.send_message(
            webhook_url=channel.webhook_url or "",
            channel_name=channel.channel_label or channel.name,
            title=title,
            text=text,
        )
    else:
        result = provider.send_message(
            channel_name=(channel.channel_label or channel.name) if channel else "Teams preview",
            title=title,
            text=text,
        )
    create_audit_log(
        db,
        actor=current_user,
        event_type="teams_message_sent",
        resource_type="teams_channel",
        resource_id=str(channel.id) if channel else None,
        message=f"Delivered Teams message '{title}'",
        details={"provider": result.provider},
    )
    db.commit()
    return result


def resolve_channel(db: Session, *, channel_id: UUID | None) -> TeamsChannel | None:
    if channel_id:
        channel = db.get(TeamsChannel, channel_id)
        if not channel or not channel.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teams channel not found.")
        return channel
    return db.scalar(
        select(TeamsChannel).where(
            TeamsChannel.is_active.is_(True),
            TeamsChannel.is_default.is_(True),
        )
    )


def clear_default_channel(db: Session) -> None:
    for channel in db.scalars(select(TeamsChannel).where(TeamsChannel.is_default.is_(True))).all():
        channel.is_default = False


def serialize_teams_channel(channel: TeamsChannel) -> TeamsChannelResponse:
    return TeamsChannelResponse(
        id=channel.id,
        name=channel.name,
        description=channel.description,
        channel_label=channel.channel_label,
        delivery_type=channel.delivery_type.value,
        has_webhook=bool(channel.webhook_url),
        is_active=channel.is_active,
        is_default=channel.is_default,
        created_at=channel.created_at,
    )
