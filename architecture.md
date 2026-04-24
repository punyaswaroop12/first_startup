# Architecture

## High-Level Design

The MVP is a small monorepo with a clear UI/API split:

- `apps/web`: Next.js frontend for login, dashboard, documents, chat, reports, automations, and admin settings
- `apps/api`: FastAPI backend for auth, ingestion, retrieval, reports, automations, and audit logs
- `Postgres + pgvector`: primary system of record plus vector retrieval
- `storage/`: local dev storage for uploaded files and generated email previews
- `storage/teams`: local dev Teams preview messages

The v2 enterprise integration work keeps that shape and extends it with a dedicated Microsoft integration layer instead of mixing Graph concerns into existing auth, documents, or automation services.

## Core Services

### Auth

- Email/password login
- Microsoft / Entra ID organizational sign-in via backend-driven OAuth/OIDC flow
- JWT access token stored client-side in MVP-friendly manner
- Role claims included in token and enforced in API dependencies
- Seeded demo users use a valid `example.com` domain so API validation and local demos behave consistently
- External identity mapping persists provider subject and tenant metadata separately from the core `users` table
- Future path: hardened session middleware, SCIM/SSO expansion, and full org-aware tenancy boundaries

### Document Ingestion

- File validation by extension, MIME type, and size
- Text extraction by parser strategy
- Chunking with metadata preservation
- Embedding generation via provider abstraction
- Chunk and vector persistence in Postgres
- Local fallback for tests stores embeddings in SQLite-compatible JSON via a type abstraction, while Postgres uses `pgvector`
- Trigger rule evaluation after ingestion

### Knowledge Retrieval

- Hybrid-ish MVP approach:
  - metadata filters in SQL
  - dense vector similarity through `pgvector`
- Python cosine fallback for test/local non-Postgres execution
- Retrieved chunks converted into structured citations
- Prompt templates stored in versioned files under `apps/api/app/prompts`
- Guardrails instruct model to ignore document-embedded instructions and only answer from factual content

### Reports

- Templates for executive, operational, and document-change summaries
- Report inputs combine:
  - selected documents
  - recent ingestion/report events
  - optional linked Power BI report references
  - optional custom notes
- Outputs persisted as structured sections for re-render/export
- Markdown and HTML export are implemented
- Delivery actions enqueue tracked background jobs for email and Teams dispatch

### Delivery And Notifications

- Email provider abstraction supports preview, SMTP, and Microsoft Graph
- Teams provider abstraction supports local preview output and webhook posting
- Report delivery and outbound notifications are tracked through the shared `background_jobs` model
- Delivery results persist provider metadata and preview artifact paths for admin review

### Automations

- Rules-based engine with:
  - trigger
  - condition
  - action
- Initial triggers:
  - document uploaded
  - report generated
  - keyword found
- Initial actions:
  - generate summary
  - notify admin or recipients
  - deliver generated reports by email
  - post notifications or reports to Teams
  - flag document for review
- Automation actions enqueue tracked background jobs when they send notifications or deliver reports

### Audit Logging

- Append-only audit events for key user/system actions
- Stored in Postgres and surfaced in Admin Settings

## API Boundaries

Primary backend domains:

- `auth`
- `users`
- `documents`
- `chat`
- `reports`
- `automations`
- `settings`
- `audit`
- `integrations.microsoft`

Each domain exposes:

- SQLAlchemy models
- Pydantic request/response schemas
- service layer for business logic
- API router

## Frontend Design

- App Router layout with auth gate and shared sidebar shell
- Typed API client wrapper
- Professional B2B dashboard with dense but readable information layout
- Source panels and structured summary cards instead of chat-only UI
- Client-side auth storage is acceptable for local MVP/demo use and is documented as an upgrade point

## Data Model Overview

Key tables:

- `users`
- `microsoft_tenants` for Entra tenant metadata and future connector scoping
- `user_identities` for provider-linked sign-in accounts
- `sessions` or JWT-only auth without DB session state for v1
- `tags`
- `documents`
- `document_versions`
- `document_chunks`
- `chat_conversations`
- `chat_messages`
- `reports`
- `summary_templates`
- `automation_rules`
- `automation_runs`
- `audit_logs`
- `background_jobs`
- `microsoft_connectors`
- `microsoft_synced_items`
- `teams_channels`
- `power_bi_report_references`

## Deployment Shape

Local/deployable containers:

- `web`
- `api`
- `db`
- `mailpit`
- `infra/postgres/init.sql` ensures the `vector` extension exists on first boot

Later cloud mapping:

- Next.js on Vercel or container platform
- FastAPI on Fly.io / Render / ECS / Azure App Service
- Managed Postgres with `pgvector`
- S3 or Azure Blob for files
- SMTP provider or notification service
- Microsoft Graph-backed enterprise connectors and delivery services

## V2 Microsoft Integration Design

### Identity Boundary

- The application continues to issue its own JWT for UI/API sessions
- Microsoft sign-in is treated as an external identity provider, not the session authority for the product itself
- External identities map to internal `users` so the rest of the application can stay provider-agnostic
- Entra tenant metadata is persisted now to support future multi-tenant segmentation and connector ownership

### Integration Layer

- Microsoft-specific logic lives under a dedicated integration package
- OAuth discovery, authorization URL construction, token exchange, ID token validation, and future Graph calls remain centralized
- Existing domain services call integration services rather than embedding Graph/OIDC logic directly

### Enterprise Rollout Path

- Phase 1 adds organizational sign-in and identity mapping
- Phase 2 introduces SharePoint and OneDrive sources on top of the same tenant/integration foundation
- Phase 3 adds sync jobs, status visibility, and incremental sync foundations
- Phase 4 adds Outlook delivery, Teams delivery, and delivery job tracking
- Phase 5 adds Power BI metadata references and admin visibility for delivery/role settings
- Phase 6 hardens tests and setup docs for enterprise demos

## Security and Guardrails

- Basic password hashing with `bcrypt`
- Input validation on all write endpoints
- File size limits and extension allowlist
- Prompt injection mitigation:
  - strip obvious control strings
  - isolate retrieved text in marked context blocks
  - system prompts explicitly deny executing instructions from documents
- Role enforcement on admin routes
- Structured logs without leaking secrets
- Basic rule/audit coverage for uploads, deletes, reports, and automation triggers
- Audit coverage for sync runs, email delivery, Teams delivery, and Power BI/Teams configuration changes
- OIDC state/nonce validation for Microsoft sign-in
- Least-privilege design for Microsoft Graph permissions, with delegated auth separated from future application-permission connectors
- Tenant and identity metadata persisted for auditability without making the core product tenant-coupled prematurely
- Report delivery by Microsoft Graph requires a specific tenant and configured sender mailbox; `organizations/common` is intentionally rejected for app-only mail delivery

## Known MVP Tradeoffs

- Background execution is lightweight, not horizontally scalable yet
- PDF export is deferred in favor of Markdown/HTML export
- OCR for scanned PDFs is not included in v1
- Rate limiting is scaffolded, not fully production hardened
- Frontend auth is stored in browser local storage for MVP speed, not hardened session middleware
- Local testing uses SQLite instead of Postgres to keep the test harness fast and dependency-light
- Teams webhook management is create-first in the current admin UX; richer secret rotation flows are a follow-up item
