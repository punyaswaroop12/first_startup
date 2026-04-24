# Project Plan

## Product Goal

Build a deployable MVP for small and mid-sized operations teams that:

1. Ingests internal documents
2. Supports cited question-answering over those documents
3. Generates structured weekly reports
4. Runs lightweight rules-based workflow automations

## Delivery Principles

- Bias toward working software over speculative architecture
- Keep interfaces swappable for AI provider, storage, and email delivery
- Use boring, maintainable defaults where possible
- Preserve a clean path from local MVP to cloud deployment
- Treat prompt injection, validation, and auditability as first-order concerns

## Selected Stack

- Frontend: Next.js 15, App Router, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy 2.x, Pydantic v2
- Database: PostgreSQL 16 + `pgvector`
- Auth: email/password + JWT access tokens
- AI: OpenAI-first provider abstraction for chat and embeddings
- Storage: local filesystem abstraction with cloud-ready interface
- Background execution: simple database-backed job model + FastAPI background tasks for MVP
- Reporting export: Markdown + HTML in v1, PDF deferred to v2
- Dev infra: Docker Compose for web, API, Postgres, Mailpit
- Tests: Pytest for API, Vitest or basic frontend smoke coverage if feasible in MVP

## Scope for v1

### In scope

- Role-based access for `admin` and `user`
- Document upload for PDF, DOCX, TXT, CSV
- Text extraction, chunking, embeddings, retrieval with citations
- Chat assistant with sources and suggested follow-ups
- Structured report generation from documents and events
- Rules engine with three initial triggers/actions
- Admin settings for tags, templates, rules, logs
- Seed data, demo docs, Docker, README, architecture notes

### Intentionally deferred

- SSO / SCIM
- Multi-tenant isolation
- Advanced workflow builder
- Human approval queues
- OCR for scanned PDFs
- True async job runner cluster
- Live collaboration and realtime notifications
- Production-grade rate limiter implementation beyond a clear abstraction

## Implementation Phases

### Phase 1

- Repo scaffold
- API and frontend foundations
- Database schema and migrations
- Auth scaffold
- Base SaaS UI shell

### Phase 2

- Document upload pipeline
- Parsing and chunk storage
- Embedding and retrieval setup
- Document list/detail views

### Phase 3

- Chat conversations
- Retrieval-augmented generation
- Citations and source panel
- Suggested follow-up questions

### Phase 4

- Summary templates
- Report generation flows
- Markdown/HTML export
- Report history

### Phase 5

- Rules engine
- Trigger evaluation
- Email/file notifications
- Admin rule management

### Phase 6

- Admin settings
- Audit/activity logs
- Polish and guardrails

### Phase 7

- Tests
- Docker/dev UX
- Final docs
- Demo readiness

## Success Criteria

- Local boot via documented setup
- Seeded users can log in and navigate the app
- Admin can upload demo docs and configure rules
- User can ask questions and receive cited answers
- User can generate a structured report and export it
- Audit logs show key actions
- Architecture is clean enough for real extension after prospect demos
