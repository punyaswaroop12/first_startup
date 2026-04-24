from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Knowledge + Reporting Assistant"
    environment: str = Field(default="development", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    public_api_base_url_raw: str = Field(default="http://localhost:8000", alias="PUBLIC_API_BASE_URL")
    web_base_url_raw: str = Field(default="http://localhost:3000", alias="WEB_BASE_URL")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/ops_ai_assistant",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(
        default="change-me-in-production-with-at-least-32-characters",
        alias="JWT_SECRET_KEY",
    )
    jwt_access_token_expire_minutes: int = Field(default=720, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    allowed_origins_raw: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")
    rate_limit_requests_per_minute: int = Field(default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    max_upload_size_mb: int = Field(default=15, alias="MAX_UPLOAD_SIZE_MB")
    file_storage_provider: str = Field(default="local", alias="FILE_STORAGE_PROVIDER")
    local_storage_root_raw: str = Field(default="storage/uploads", alias="LOCAL_STORAGE_ROOT")
    email_provider: str = Field(default="preview", alias="EMAIL_PROVIDER")
    email_preview_dir_raw: str = Field(default="storage/emails", alias="EMAIL_PREVIEW_DIR")
    smtp_host: str = Field(default="mailpit", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_username: str = Field(default="", alias="SMTP_USERNAME")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=False, alias="SMTP_USE_TLS")
    mail_from: str = Field(default="ops-ai-assistant@example.com", alias="MAIL_FROM")
    microsoft_outlook_sender: str = Field(default="", alias="MICROSOFT_OUTLOOK_SENDER")
    teams_provider: str = Field(default="preview", alias="TEAMS_PROVIDER")
    teams_preview_dir_raw: str = Field(default="storage/teams", alias="TEAMS_PREVIEW_DIR")
    ai_provider: str = Field(default="fake", alias="AI_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="", alias="OPENAI_BASE_URL")
    openai_chat_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_CHAT_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")
    default_admin_email: str = Field(
        default="admin@ops-ai-demo.example.com", alias="DEFAULT_ADMIN_EMAIL"
    )
    default_admin_password: str = Field(default="AdminPass123!", alias="DEFAULT_ADMIN_PASSWORD")
    default_user_email: str = Field(
        default="analyst@ops-ai-demo.example.com", alias="DEFAULT_USER_EMAIL"
    )
    default_user_password: str = Field(default="UserPass123!", alias="DEFAULT_USER_PASSWORD")
    microsoft_auth_enabled: bool = Field(default=False, alias="MICROSOFT_AUTH_ENABLED")
    microsoft_client_id: str = Field(default="", alias="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: str = Field(default="", alias="MICROSOFT_CLIENT_SECRET")
    microsoft_tenant_id: str = Field(default="organizations", alias="MICROSOFT_TENANT_ID")
    microsoft_graph_base_url_raw: str = Field(
        default="https://graph.microsoft.com/v1.0", alias="MICROSOFT_GRAPH_BASE_URL"
    )
    microsoft_graph_scope: str = Field(
        default="https://graph.microsoft.com/.default", alias="MICROSOFT_GRAPH_SCOPE"
    )
    microsoft_scopes_raw: str = Field(
        default="openid profile email User.Read", alias="MICROSOFT_SCOPES"
    )
    microsoft_oauth_state_expire_minutes: int = Field(
        default=10, alias="MICROSOFT_OAUTH_STATE_EXPIRE_MINUTES"
    )
    microsoft_admin_emails_raw: str = Field(default="", alias="MICROSOFT_ADMIN_EMAILS")
    microsoft_admin_domains_raw: str = Field(default="", alias="MICROSOFT_ADMIN_DOMAINS")
    microsoft_sync_page_size: int = Field(default=100, alias="MICROSOFT_SYNC_PAGE_SIZE")
    microsoft_default_sync_frequency_minutes: int = Field(
        default=1440, alias="MICROSOFT_DEFAULT_SYNC_FREQUENCY_MINUTES"
    )
    background_job_inline_execution: bool = Field(default=True, alias="BACKGROUND_JOB_INLINE_EXECUTION")

    @computed_field
    @property
    def repo_root(self) -> Path:
        return Path(__file__).resolve().parents[4]

    def _split_csv(self, raw: str) -> list[str]:
        return [item.strip() for item in raw.split(",") if item.strip()]

    @computed_field
    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]

    @computed_field
    @property
    def local_storage_root(self) -> Path:
        return (self.repo_root / self.local_storage_root_raw).resolve()

    @computed_field
    @property
    def email_preview_dir(self) -> Path:
        return (self.repo_root / self.email_preview_dir_raw).resolve()

    @computed_field
    @property
    def teams_preview_dir(self) -> Path:
        return (self.repo_root / self.teams_preview_dir_raw).resolve()

    @computed_field
    @property
    def public_api_base_url(self) -> str:
        return self.public_api_base_url_raw.rstrip("/")

    @computed_field
    @property
    def web_base_url(self) -> str:
        return self.web_base_url_raw.rstrip("/")

    @computed_field
    @property
    def microsoft_graph_base_url(self) -> str:
        return self.microsoft_graph_base_url_raw.rstrip("/")

    @computed_field
    @property
    def microsoft_graph_scope_value(self) -> str:
        return self.microsoft_graph_scope.strip() or "https://graph.microsoft.com/.default"

    @computed_field
    @property
    def microsoft_authority_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.microsoft_tenant_id}/v2.0"

    @computed_field
    @property
    def microsoft_openid_configuration_url(self) -> str:
        return f"{self.microsoft_authority_url}/.well-known/openid-configuration"

    @computed_field
    @property
    def microsoft_redirect_uri(self) -> str:
        return f"{self.public_api_base_url}{self.api_v1_prefix}/auth/microsoft/callback"

    @computed_field
    @property
    def microsoft_scopes(self) -> list[str]:
        configured = self._split_csv(self.microsoft_scopes_raw.replace(" ", ","))
        scopes: list[str] = []
        for scope in [*configured, "openid", "profile", "email"]:
            if scope not in scopes:
                scopes.append(scope)
        return scopes

    @computed_field
    @property
    def microsoft_admin_emails(self) -> list[str]:
        return [email.lower() for email in self._split_csv(self.microsoft_admin_emails_raw)]

    @computed_field
    @property
    def microsoft_admin_domains(self) -> list[str]:
        return [domain.lower() for domain in self._split_csv(self.microsoft_admin_domains_raw)]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
