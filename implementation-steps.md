# Implementation Steps

## Phase 1: Foundations

1. Create monorepo layout for `apps/api` and `apps/web`
2. Add root developer tooling, environment examples, and shared scripts
3. Build FastAPI app skeleton with config, database session, and auth primitives
4. Create SQLAlchemy models, Alembic migration, and seed baseline users/tags/templates
5. Scaffold Next.js app shell with login flow, sidebar, dashboard, and guarded routes

## Phase 2: Documents

1. Add storage abstraction and local file backend
2. Implement file validation, parser strategies, chunking, and ingestion services
3. Persist documents, versions, chunks, tags, and audit events
4. Build documents page for upload, list, search, and delete actions

## Phase 3: Knowledge Chat

1. Add embedding abstraction and retrieval service
2. Implement chat conversations and message persistence
3. Build cited answer generation with source excerpts and uncertainty handling
4. Add chat UI with conversation history, source panel, and follow-up prompts

## Phase 4: Reports

1. Add prompt template loading and template overrides
2. Implement report generation service and report persistence
3. Add markdown and HTML export endpoints
4. Build reports UI for generating, browsing, and exporting summaries

## Phase 5: Automations

1. Model rules, runs, triggers, and actions
2. Evaluate rules on document upload and report generation
3. Add email preview / SMTP abstraction and document flagging action
4. Build automation management UI

## Phase 6: Admin and Polish

1. Add admin settings for tags, templates, and rules
2. Surface audit logs and usage/activity data
3. Tighten error handling, guardrails, and empty states
4. Refine the dashboard for demo readiness

## Phase 7: Finalization

1. Add unit and integration tests for critical flows
2. Finalize Dockerfiles and `docker-compose.yml`
3. Complete README, architecture notes, demo script, and roadmap
4. Run linting/tests as far as the local environment allows and document any gaps
