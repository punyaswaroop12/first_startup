from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.integrations.microsoft.client import (
    MicrosoftIdentityClient,
    MicrosoftIntegrationError,
    get_microsoft_identity_client,
)
from app.schemas.auth import AuthProvidersResponse, AuthProviderStatus, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth import authenticate_user, issue_access_token
from app.services.microsoft_auth import (
    build_frontend_microsoft_callback_url,
    parse_microsoft_oauth_state,
    prepare_microsoft_oauth_state,
    sanitize_redirect_path,
    upsert_microsoft_user,
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = issue_access_token(user)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/providers", response_model=AuthProvidersResponse)
def auth_providers(
    microsoft_client: MicrosoftIdentityClient = Depends(get_microsoft_identity_client),
) -> AuthProvidersResponse:
    return AuthProvidersResponse(
        providers=[
            AuthProviderStatus(key="password", label="Email and password", enabled=True),
            AuthProviderStatus(
                key="microsoft",
                label="Microsoft Entra ID",
                enabled=microsoft_client.is_configured(),
            ),
        ]
    )


@router.get("/microsoft/start", include_in_schema=False)
def microsoft_start(
    redirect_to: str | None = Query(default=None),
    microsoft_client: MicrosoftIdentityClient = Depends(get_microsoft_identity_client),
) -> RedirectResponse:
    try:
        state = prepare_microsoft_oauth_state(redirect_to)
        authorization_url = microsoft_client.build_authorization_url(
            state=state.state_token,
            nonce=state.nonce,
        )
    except MicrosoftIntegrationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)


@router.get("/microsoft/callback", include_in_schema=False)
def microsoft_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
    db: Session = Depends(get_db),
    microsoft_client: MicrosoftIdentityClient = Depends(get_microsoft_identity_client),
) -> RedirectResponse:
    if error:
        return RedirectResponse(
            url=build_frontend_microsoft_callback_url(
                error=error_description or error,
                redirect_to="/dashboard",
            ),
            status_code=status.HTTP_302_FOUND,
        )

    if not code or not state:
        return RedirectResponse(
            url=build_frontend_microsoft_callback_url(
                error="Microsoft sign-in did not return the expected callback payload.",
                redirect_to="/dashboard",
            ),
            status_code=status.HTTP_302_FOUND,
        )

    try:
        parsed_state = parse_microsoft_oauth_state(state)
        tokens = microsoft_client.exchange_code_for_tokens(code=code)
        claims = microsoft_client.validate_id_token(tokens.id_token, expected_nonce=parsed_state.nonce)
        user = upsert_microsoft_user(db, claims)
        db.commit()
        access_token = issue_access_token(user)
    except (InvalidTokenError, MicrosoftIntegrationError, ValueError) as exc:
        db.rollback()
        return RedirectResponse(
            url=build_frontend_microsoft_callback_url(
                error=str(exc),
                redirect_to=sanitize_redirect_path("/dashboard"),
            ),
            status_code=status.HTTP_302_FOUND,
        )

    return RedirectResponse(
        url=build_frontend_microsoft_callback_url(
            access_token=access_token,
            redirect_to=parsed_state.redirect_to,
        ),
        status_code=status.HTTP_302_FOUND,
    )
