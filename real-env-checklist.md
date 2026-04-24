# Real Environment Checklist

Use this checklist before validating the app against a real Microsoft tenant and real delivery endpoints.

## Goal

Confirm that the environment is configured for:

- Microsoft / Entra login
- SharePoint sync
- OneDrive sync
- Outlook delivery through Microsoft Graph
- Teams delivery through webhook mode
- Power BI references in the UI and reports

## 1. Core App Configuration

These variables should be reviewed first in every real environment.

| Variable | Required | Notes |
| --- | --- | --- |
| `APP_ENV` | Yes | Set to a non-local value such as `staging` or `production`. |
| `PUBLIC_API_BASE_URL` | Yes | Public API origin, no trailing `/api/v1`. Example: `https://api.example.com`. |
| `WEB_BASE_URL` | Yes | Public web app origin. Example: `https://app.example.com`. |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Full frontend API prefix. Example: `https://api.example.com/api/v1`. |
| `DATABASE_URL` | Yes | Real Postgres connection string. |
| `JWT_SECRET_KEY` | Yes | Replace the default value with a strong secret. |
| `ALLOWED_ORIGINS` | Yes | Include the deployed web origin and any approved admin/test origins. |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Recommended | Keep enabled for pilot validation. |
| `MAX_UPLOAD_SIZE_MB` | Recommended | Confirm it matches the real document profile. |
| `BACKGROUND_JOB_INLINE_EXECUTION` | Yes | `true` is acceptable for a pilot. For a real worker model, document the change separately. |

Checklist:

- [ ] `PUBLIC_API_BASE_URL`, `WEB_BASE_URL`, and `NEXT_PUBLIC_API_BASE_URL` all point to the same deployment pair.
- [ ] `JWT_SECRET_KEY` is not the default placeholder.
- [ ] `DATABASE_URL` points to the intended Postgres instance.
- [ ] The database has the `vector` extension enabled if Postgres + pgvector is used.
- [ ] `ALLOWED_ORIGINS` includes the real web hostname.

## 2. AI Provider Configuration

The app can run with the fake provider, but real environment validation of chat/report quality should use a real model provider.

| Variable | Required | Notes |
| --- | --- | --- |
| `AI_PROVIDER` | Yes | Set to `openai` for real LLM validation. |
| `OPENAI_API_KEY` | Yes if `AI_PROVIDER=openai` | Required for real chat/report generation. |
| `OPENAI_BASE_URL` | Optional | Leave empty for default OpenAI routing. |
| `OPENAI_CHAT_MODEL` | Recommended | Current default is `gpt-4.1-mini`. |
| `OPENAI_EMBEDDING_MODEL` | Recommended | Current default is `text-embedding-3-small`. |
| `EMBEDDING_DIMENSION` | Required with real embeddings | Must match the embedding model. Default is `1536`. |

Checklist:

- [ ] `AI_PROVIDER` is intentionally set for the environment.
- [ ] If using OpenAI, `OPENAI_API_KEY` is present and valid.
- [ ] `EMBEDDING_DIMENSION` matches the selected embedding model.

## 3. Microsoft Login / Entra ID

These values control the Microsoft sign-in flow and internal role mapping scaffold.

| Variable | Required | Notes |
| --- | --- | --- |
| `MICROSOFT_AUTH_ENABLED` | Yes | Must be `true` for Microsoft login validation. |
| `MICROSOFT_CLIENT_ID` | Yes | Entra app registration client ID. |
| `MICROSOFT_CLIENT_SECRET` | Yes | Entra app registration secret. |
| `MICROSOFT_TENANT_ID` | Yes | Use a specific tenant for real validation. `organizations` is fine for early sign-in pilots but not ideal for Graph mail. |
| `MICROSOFT_SCOPES` | Yes | Current delegated sign-in scopes should include `openid profile email User.Read`. |
| `MICROSOFT_GRAPH_BASE_URL` | Usually yes | Keep the default `https://graph.microsoft.com/v1.0` unless intentionally overridden. |
| `MICROSOFT_OAUTH_STATE_EXPIRE_MINUTES` | Recommended | Keep default unless you have a reason to change it. |
| `MICROSOFT_ADMIN_EMAILS` | Optional | Comma-separated explicit admin mappings. |
| `MICROSOFT_ADMIN_DOMAINS` | Optional | Comma-separated domain-based admin mappings. |

Checklist:

- [ ] Redirect URI in Entra matches `{PUBLIC_API_BASE_URL}/api/v1/auth/microsoft/callback`.
- [ ] `MICROSOFT_AUTH_ENABLED=true`.
- [ ] `MICROSOFT_CLIENT_ID` and `MICROSOFT_CLIENT_SECRET` are set for the correct app registration.
- [ ] `MICROSOFT_TENANT_ID` is correct for the customer tenant.
- [ ] `MICROSOFT_SCOPES` includes the delegated sign-in scopes.
- [ ] Any intended admin users or domains are listed in `MICROSOFT_ADMIN_EMAILS` and/or `MICROSOFT_ADMIN_DOMAINS`.

## 4. SharePoint And OneDrive Connector Readiness

Connector creation depends on the Microsoft app registration and the target sources being reachable.

| Variable | Required | Notes |
| --- | --- | --- |
| `MICROSOFT_GRAPH_SCOPE` | Yes | Current default is `https://graph.microsoft.com/.default`. |
| `MICROSOFT_SYNC_PAGE_SIZE` | Recommended | Keep default unless you need smaller paging during pilot validation. |
| `MICROSOFT_DEFAULT_SYNC_FREQUENCY_MINUTES` | Recommended | Default connector cadence seed value. |

Required app permissions for connector validation:

- `Sites.Read.All`
- `Files.Read.All`

Checklist:

- [ ] Admin consent has been granted for `Sites.Read.All` and `Files.Read.All`.
- [ ] A test SharePoint site, library, and folder path are available.
- [ ] A test OneDrive user principal name and folder path are available.
- [ ] The app registration is allowed to read those sources.

## 5. Outlook Delivery Through Graph

Use this section only if you want real Outlook delivery validation.

| Variable | Required | Notes |
| --- | --- | --- |
| `EMAIL_PROVIDER` | Yes | Set to `graph` for real Graph mail validation. |
| `MICROSOFT_OUTLOOK_SENDER` | Yes with Graph mail | Must be a valid mailbox or shared mailbox UPN in the tenant. |
| `MAIL_FROM` | Recommended | Still useful as a logical sender label in non-Graph modes. |

Required app permission:

- `Mail.Send`

Checklist:

- [ ] `EMAIL_PROVIDER=graph`.
- [ ] `MICROSOFT_TENANT_ID` is a specific tenant, not `organizations` or `common`.
- [ ] `MICROSOFT_OUTLOOK_SENDER` is valid and licensed for the tenant scenario.
- [ ] Admin consent has been granted for `Mail.Send`.
- [ ] Test recipients are approved for pilot delivery.

## 6. Teams Delivery

The current MVP supports preview or webhook mode. Real environment validation should typically use webhook mode.

| Variable | Required | Notes |
| --- | --- | --- |
| `TEAMS_PROVIDER` | Yes | Set to `webhook` for real channel posting. |
| `TEAMS_PREVIEW_DIR` | Optional | Only used in preview mode. |

Checklist:

- [ ] `TEAMS_PROVIDER=webhook` for real Teams validation.
- [ ] A Teams incoming webhook has been created for the target channel.
- [ ] The webhook URL is entered through Admin Settings when creating the delivery channel.
- [ ] The target channel is appropriate for pilot notifications and weekly summaries.

## 7. File Storage And Upload Validation

| Variable | Required | Notes |
| --- | --- | --- |
| `FILE_STORAGE_PROVIDER` | Yes | Current MVP uses `local`. |
| `LOCAL_STORAGE_ROOT` | Yes with local storage | Must be writable by the API process. |

Checklist:

- [ ] The API process can write to `LOCAL_STORAGE_ROOT`.
- [ ] The upload path is persistent enough for the planned validation window.
- [ ] Sample PDFs, DOCX files, TXT files, and CSV files are ready for testing.

## 8. Seed / Demo Credentials Review

These are not integration blockers, but they should be reviewed before a real validation session.

| Variable | Recommended | Notes |
| --- | --- | --- |
| `DEFAULT_ADMIN_EMAIL` | Yes | Change if you do not want demo-flavored seeded users. |
| `DEFAULT_ADMIN_PASSWORD` | Yes | Do not leave a default password in a shared environment. |
| `DEFAULT_USER_EMAIL` | Yes | Change if needed for pilot cleanup. |
| `DEFAULT_USER_PASSWORD` | Yes | Do not leave a default password in a shared environment. |

Checklist:

- [ ] Seeded credentials are either rotated or intentionally accepted for the pilot.
- [ ] The environment is not exposing default credentials to a broad audience.

## 9. Power BI Reference Readiness

Current Power BI scope is metadata and linking, not embedded reporting.

Checklist:

- [ ] Power BI report URLs are available for the validation workspace.
- [ ] Workspace name, report name, and tags are prepared for admin entry.
- [ ] Stakeholders understand this MVP shows links and references, not embedded report rendering.

## 10. Final Go / No-Go Review

- [ ] Core app URLs are correct.
- [ ] Database is reachable.
- [ ] AI provider is intentionally configured.
- [ ] Microsoft login values are complete.
- [ ] Graph permissions are consented for the enabled features.
- [ ] SharePoint test source is ready.
- [ ] OneDrive test source is ready.
- [ ] Outlook sender mailbox is ready if Graph mail is enabled.
- [ ] Teams webhook is ready if real Teams delivery is enabled.
- [ ] Power BI report metadata is ready for admin entry.
- [ ] Validation users and recipients are confirmed.
