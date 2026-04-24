# AI Knowledge + Reporting Assistant for Operations Teams

Production-minded MVP for operations-heavy teams to upload internal documents, ask cited questions over SOPs and policies, generate weekly reports, and automate simple internal workflows.

## What’s Included

- Document ingestion for `PDF`, `DOCX`, `TXT`, and `CSV`
- RAG chat with conversation history, citations, source panel, and follow-up questions
- Structured report generation for executive, operational, and document-change summaries
- Outlook / Microsoft Graph email delivery with preview, SMTP, and Graph provider abstraction
- Teams delivery with preview and webhook provider abstraction
- SharePoint and OneDrive connector management with tracked sync jobs
- Power BI report metadata references surfaced in reports, dashboard cards, and admin settings
- Lightweight rules engine with summary generation, review flagging, report delivery, and Teams/email notifications
- Admin settings for connectors, delivery channels, Power BI references, templates, tags, and audit logs
- Seeded demo users, sample documents, seeded Power BI references, a default Teams channel, and seeded automation rules
- Docker Compose support for `web`, `api`, `db`, and `mailpit`

## Stack

- Frontend: Next.js 15 + TypeScript + Tailwind CSS
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: Postgres 16 + `pgvector`
- AI: provider abstraction with `fake` and `OpenAI` implementations
- Storage: local filesystem abstraction
- Email: preview writer, SMTP, and Microsoft Graph abstraction
- Notifications: Teams preview/webhook abstraction

## Repo Docs

- [project-plan.md](/Users/punyaswaroopsirigiri/first_startup/project-plan.md)
- [architecture.md](/Users/punyaswaroopsirigiri/first_startup/architecture.md)
- [microsoft-integrations.md](/Users/punyaswaroopsirigiri/first_startup/microsoft-integrations.md)
- [azure-setup.md](/Users/punyaswaroopsirigiri/first_startup/azure-setup.md)
- [graph-permissions.md](/Users/punyaswaroopsirigiri/first_startup/graph-permissions.md)
- [repo-structure.md](/Users/punyaswaroopsirigiri/first_startup/repo-structure.md)
- [implementation-steps.md](/Users/punyaswaroopsirigiri/first_startup/implementation-steps.md)
- [CHECKLIST.md](/Users/punyaswaroopsirigiri/first_startup/CHECKLIST.md)
- [progress.md](/Users/punyaswaroopsirigiri/first_startup/progress.md)
- [demo-script.md](/Users/punyaswaroopsirigiri/first_startup/demo-script.md)
- [demo-script-v2.md](/Users/punyaswaroopsirigiri/first_startup/demo-script-v2.md)
- [roadmap.md](/Users/punyaswaroopsirigiri/first_startup/roadmap.md)

## Quick Start

### Option 1: Docker Compose

1. Copy the environment file:
   `cp .env.example .env`
2. Start the full stack:
   `docker compose up --build`
3. Open:
   - Web: `http://localhost:3000`
   - API docs: `http://localhost:8000/api/v1/docs`
   - Mailpit: `http://localhost:8025`

The API container seeds demo users, sample docs, templates, Power BI references, Teams preview channel, and sample automation rules on startup.

### Option 2: Local Development

Prerequisites:

- Python `3.12+`
- Node `22+` recommended
- Postgres `16+` with the `vector` extension

1. Copy the environment file:
   `cp .env.example .env`
2. Create the backend virtualenv and install dependencies:
   `cd apps/api && python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'`
3. Install frontend dependencies from the repo root:
   `cd ../.. && npm install`
4. Ensure Postgres is running and create the extension:
   `psql -d ops_ai_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"`
5. Seed the app:
   `cd apps/api && DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ops_ai_assistant .venv/bin/python -m app.db.seed`
6. Start both apps from the repo root:
   `npm run dev`

## Demo Credentials

- Admin: `admin@ops-ai-demo.example.com / AdminPass123!`
- User: `analyst@ops-ai-demo.example.com / UserPass123!`

## Microsoft / Entra ID Setup

The v2 implementation now supports:

- Microsoft organizational sign-in through Entra ID
- SharePoint / OneDrive connector configuration and sync
- Graph-backed Outlook delivery when `EMAIL_PROVIDER=graph`
- Teams channel delivery through preview or webhook providers
- Power BI report metadata linking for reports and dashboard cards

Required environment variables:

- `PUBLIC_API_BASE_URL`
- `WEB_BASE_URL`
- `MICROSOFT_AUTH_ENABLED=true`
- `MICROSOFT_CLIENT_ID`
- `MICROSOFT_CLIENT_SECRET`
- `MICROSOFT_TENANT_ID=organizations` or a specific tenant GUID/domain
- `MICROSOFT_GRAPH_SCOPE=https://graph.microsoft.com/.default`
- `MICROSOFT_OUTLOOK_SENDER` when using `EMAIL_PROVIDER=graph`
- `TEAMS_PROVIDER=preview` for local preview files or `TEAMS_PROVIDER=webhook` for real Teams posting

Related docs:

- [azure-setup.md](/Users/punyaswaroopsirigiri/first_startup/azure-setup.md)
- [graph-permissions.md](/Users/punyaswaroopsirigiri/first_startup/graph-permissions.md)
- [microsoft-integrations.md](/Users/punyaswaroopsirigiri/first_startup/microsoft-integrations.md)

## Useful Commands

- Backend tests:
  `cd apps/api && .venv/bin/pytest tests -q`
- Backend lint:
  `cd apps/api && .venv/bin/ruff check .`
- Frontend lint:
  `npm --workspace apps/web run lint`
- Frontend typecheck:
  `npm --workspace apps/web run typecheck`
- Frontend build:
  `npm --workspace apps/web run build`
- Docker availability check:
  `docker --version`
- Seed data:
  `cd apps/api && .venv/bin/python -m app.db.seed`

## Environment Notes

- Default `AI_PROVIDER=fake` keeps the app runnable without an external model key.
- Set `AI_PROVIDER=openai` and `OPENAI_API_KEY=...` to use OpenAI for chat and reporting.
- Default `EMAIL_PROVIDER=preview` writes HTML previews into `storage/emails`.
- Default `TEAMS_PROVIDER=preview` writes Teams preview messages into `storage/teams`.
- Microsoft sign-in uses a backend OAuth callback at `{PUBLIC_API_BASE_URL}/api/v1/auth/microsoft/callback`.
- `MICROSOFT_ADMIN_EMAILS` and `MICROSOFT_ADMIN_DOMAINS` provide the initial role-mapping scaffold for Entra users.
- Markdown and HTML export are implemented. PDF export is still deferred.
- `BACKGROUND_JOB_INLINE_EXECUTION=true` keeps sync and delivery jobs runnable in a single-process local MVP.
- The seeded admin page includes a default preview Teams channel and sample Power BI references for demo use.

## Verification

Completed in this workspace:

- Backend lint: passed via `ruff`
- Backend tests: passed via `pytest` with `10` tests
- Frontend lint: passed via `next lint`
- Frontend typecheck: passed via `next build >/dev/null && tsc --noEmit`
- Frontend production build: passed via `next build`

Limitations of this local verification:

- Docker could not be executed from this environment because `docker` is not installed in `PATH` here.
- End-to-end API execution against Postgres was not run in this sandbox because local TCP access to `localhost:5432` is restricted.
- Live Microsoft Graph, SharePoint, OneDrive, Outlook, and Teams calls still require real tenant credentials plus network access in the deployment environment.
