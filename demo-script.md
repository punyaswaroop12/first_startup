# Demo Script

## Goal

Show a prospect that the MVP can ingest internal documents, answer cited questions, generate structured reports, and automate a simple internal workflow.

## Demo Flow

1. Start on the login page.
   Use `admin@ops-ai-demo.example.com / AdminPass123!`.

2. Open the dashboard.
   Show that the app already has seeded documents, reports, and activity visible in one B2B-style control center.

3. Go to Documents.
   Point out the supported formats, tag metadata, version labels, and ingest status.
   Mention that seeded documents are already indexed.
   Optionally upload a new TXT or CSV file with the `safety` tag.

4. Move to Chat Assistant.
   Ask a grounded question such as:
   `What is the escalation requirement for hydraulic pressure issues?`
   Then ask:
   `What follow-up action should the operations manager take?`
   Open the source panel and highlight the cited chunks and match scores.

5. Move to Reports.
   Generate an `Operational Summary`.
   Select one or two documents and add a short note such as:
   `Focus on safety compliance and unresolved maintenance backlog.`
   Show the structured output:
   top themes, risks/issues, action items, and notable updates.
   Export the report to Markdown or HTML.

6. Move to Automations.
   Show the seeded rule:
   `Safety upload summary + notify`
   Explain the trigger, condition, and actions.
   If you uploaded a `safety` document earlier, point to the recent automation run.

7. Move to Admin Settings.
   Show tag management, template defaults/overrides, and audit logs.
   Point out that upload, report generation, and automation events are all captured.

8. Close with deployment posture.
   Mention the `Next.js + FastAPI + Postgres/pgvector` stack, the provider abstractions, the Docker Compose path, and the clear v2 roadmap.

## Suggested Narrative

- This is built for operations-heavy teams that live in SOPs, policy docs, and repetitive internal follow-up.
- The MVP is intentionally pragmatic: it handles ingestion, cited Q&A, reporting, and one simple workflow engine cleanly.
- The architecture leaves room for SSO, cloud storage, stronger observability, and more advanced workflow logic without a rewrite.

