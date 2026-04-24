from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from urllib.parse import urlencode

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.microsoft.client import MicrosoftIdentityClaims
from app.models.identity import IdentityProvider, MicrosoftTenant, UserIdentity
from app.models.user import User, UserRole
from app.services.audit import create_audit_log
from app.services.auth import issue_access_token
from app.services.user import get_user_by_email


@dataclass(slots=True)
class PreparedMicrosoftOAuthState:
    state_token: str
    nonce: str
    redirect_to: str


def sanitize_redirect_path(redirect_to: str | None) -> str:
    if not redirect_to:
        return "/dashboard"
    if not redirect_to.startswith("/") or redirect_to.startswith("//"):
        return "/dashboard"
    return redirect_to


def prepare_microsoft_oauth_state(redirect_to: str | None = None) -> PreparedMicrosoftOAuthState:
    safe_redirect = sanitize_redirect_path(redirect_to)
    nonce = token_urlsafe(24)
    expires = datetime.now(UTC) + timedelta(minutes=settings.microsoft_oauth_state_expire_minutes)
    state_token = jwt.encode(
        {
            "purpose": "microsoft_oauth_state",
            "nonce": nonce,
            "redirect_to": safe_redirect,
            "exp": expires,
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )
    return PreparedMicrosoftOAuthState(
        state_token=state_token,
        nonce=nonce,
        redirect_to=safe_redirect,
    )


def parse_microsoft_oauth_state(state_token: str) -> PreparedMicrosoftOAuthState:
    payload = jwt.decode(state_token, settings.jwt_secret_key, algorithms=["HS256"])
    if payload.get("purpose") != "microsoft_oauth_state":
        raise ValueError("Invalid Microsoft OAuth state.")
    nonce = payload.get("nonce")
    if not nonce:
        raise ValueError("Microsoft OAuth state is missing a nonce.")
    return PreparedMicrosoftOAuthState(
        state_token=state_token,
        nonce=nonce,
        redirect_to=sanitize_redirect_path(payload.get("redirect_to")),
    )


def build_frontend_microsoft_callback_url(
    *,
    access_token: str | None = None,
    redirect_to: str = "/dashboard",
    error: str | None = None,
) -> str:
    query = urlencode(
        {
            key: value
            for key, value in {
                "access_token": access_token,
                "next": sanitize_redirect_path(redirect_to),
                "error": error,
            }.items()
            if value
        }
    )
    return f"{settings.web_base_url}/auth/callback/microsoft#{query}"


def resolve_microsoft_role(email: str) -> UserRole:
    normalized_email = email.strip().lower()
    if normalized_email in settings.microsoft_admin_emails:
        return UserRole.ADMIN
    domain = normalized_email.split("@")[-1]
    if domain in settings.microsoft_admin_domains:
        return UserRole.ADMIN
    return UserRole.USER


def upsert_microsoft_user(db: Session, claims: MicrosoftIdentityClaims) -> User:
    now = datetime.now(UTC)
    tenant = db.scalar(
        select(MicrosoftTenant).where(MicrosoftTenant.tenant_id == claims.tenant_id)
    )
    primary_domain = claims.email.split("@")[-1]
    if tenant is None:
        tenant = MicrosoftTenant(
            tenant_id=claims.tenant_id,
            display_name=primary_domain,
            primary_domain=primary_domain,
            tenant_metadata={"issuer": claims.raw_claims.get("iss"), "tid": claims.tenant_id},
            last_seen_at=now,
        )
        db.add(tenant)
        db.flush()
    else:
        tenant.primary_domain = tenant.primary_domain or primary_domain
        tenant.display_name = tenant.display_name or primary_domain
        tenant.tenant_metadata = {
            **tenant.tenant_metadata,
            "issuer": claims.raw_claims.get("iss"),
            "tid": claims.tenant_id,
        }
        tenant.last_seen_at = now

    identity = db.scalar(
        select(UserIdentity).where(
            UserIdentity.provider == IdentityProvider.MICROSOFT,
            UserIdentity.provider_subject == claims.subject,
        )
    )

    user = identity.user if identity else get_user_by_email(db, claims.email)
    is_new_user = False
    if user is None:
        is_new_user = True
        user = User(
            email=claims.email,
            full_name=claims.display_name,
            role=resolve_microsoft_role(claims.email),
            hashed_password=None,
            is_active=True,
        )
        db.add(user)
        db.flush()
    elif not user.is_active:
        raise ValueError("This account is inactive.")
    else:
        user.email = claims.email
        user.full_name = claims.display_name or user.full_name
        if user.role != UserRole.ADMIN and resolve_microsoft_role(claims.email) == UserRole.ADMIN:
            user.role = UserRole.ADMIN

    if identity is None:
        identity = UserIdentity(
            user=user,
            provider=IdentityProvider.MICROSOFT,
            provider_subject=claims.subject,
        )
        db.add(identity)

    identity.provider_email = claims.email
    identity.provider_display_name = claims.display_name
    identity.microsoft_tenant = tenant
    identity.claims = claims.raw_claims
    identity.last_login_at = now

    create_audit_log(
        db,
        actor=user,
        event_type="auth.login.microsoft",
        resource_type="user",
        resource_id=str(user.id),
        message=f"Microsoft sign-in completed for {claims.email}",
        details={
            "provider": IdentityProvider.MICROSOFT.value,
            "tenant_id": claims.tenant_id,
            "is_new_user": is_new_user,
        },
    )
    db.flush()
    return user


def issue_microsoft_app_session(db: Session, claims: MicrosoftIdentityClaims) -> str:
    user = upsert_microsoft_user(db, claims)
    return issue_access_token(user)
