# Demo Script V2

## Goal

Show the product as an enterprise-ready operations assistant for Microsoft-centric organizations.

## 1. Sign In

- Open the app and show the standard login plus Microsoft sign-in
- Sign in as `admin@ops-ai-demo.example.com`
- Mention that Entra ID sign-in maps Microsoft identities into internal users and roles

## 2. Show Enterprise Readiness

- Open `Admin Settings`
- Point out:
  - Microsoft sign-in readiness
  - tenant discovery
  - role-mapping scaffold
  - configured email and Teams delivery modes

## 3. Show SharePoint / OneDrive Connectors

- In `Admin Settings`, highlight the connector section
- Show:
  - connector source label
  - last sync
  - next sync
  - document counts
  - failure visibility
- Trigger `Sync now` on a connector
- Show the sync jobs panel updating

## 4. Show Synced Documents And Cited Answers

- Go to `Documents`
- Show that synced documents preserve external source metadata and source links
- Go to `Assistant`
- Ask a question against a synced SOP or policy
- Open the source panel and point out:
  - source document
  - excerpt
  - external source path / URL

## 5. Generate An Executive Report

- Go to `Reports`
- Select a few documents
- Select one or more linked Power BI references
- Generate an executive or operational report
- Show the structured output:
  - top themes
  - risks/issues
  - action items
  - notable updates
- Open one of the linked Power BI references from the report card

## 6. Deliver The Report

- From the report card:
  - queue email delivery
  - queue Teams delivery
- Mention that local dev uses preview artifacts, while production can switch to Graph mail and Teams webhook delivery

## 7. Show Automation

- Open `Automations`
- Show a rule such as:
  - safety upload summary + notify
  - executive report delivery
- Explain that the engine is intentionally rules-based, not opaque agent orchestration

## 8. Close With Auditability

- Return to `Admin Settings`
- Open the audit log / jobs sections
- Show sync runs, delivery jobs, and outbound actions

## Demo Close

Use this close:

“Today this handles Microsoft sign-in, SharePoint and OneDrive sync, cited answers over synced content, report generation, Outlook/Teams delivery, and a lightweight automation layer. The next step is tenant-isolated rollout, permission-aware retrieval, and richer Teams/Power BI enterprise workflows.”
