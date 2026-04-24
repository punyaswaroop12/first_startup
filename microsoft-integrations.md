# Microsoft Integrations

## Implemented In V2

- Microsoft / Entra ID organizational sign-in with internal user mapping
- Tenant persistence for external identities and future tenant-scoped rollout
- Centralized Microsoft Graph client for auth, connector resolution, sync, and mail delivery
- SharePoint document library and OneDrive folder connectors
- Initial sync, manual re-sync, scheduled sync foundation, and delta-token persistence
- Outlook delivery through Microsoft Graph when `EMAIL_PROVIDER=graph`
- Teams delivery through preview or webhook providers
- Power BI report metadata references surfaced in admin settings, dashboard cards, and generated reports
- Background jobs for connector sync, report delivery, and outbound notifications
- Audit logging for sync, delivery, connector setup, Teams setup, and Power BI configuration events

## Current Admin Surfaces

- `Admin Settings > Microsoft readiness`
  - Entra sign-in status
  - Graph app readiness
  - admin email/domain role mapping scaffold
  - configured delivery providers
  - default Teams channel visibility
- `Admin Settings > Connector sources`
  - create SharePoint and OneDrive sources
  - view last sync, next sync, document counts, and failure reasons
  - queue manual syncs and dispatch due jobs
- `Admin Settings > Teams delivery channels`
  - create preview or webhook channels
  - set default preview channel
- `Admin Settings > Power BI references`
  - create report links/metadata
  - enable or disable references
- `Admin Settings > Audit log`
  - review outbound actions and integration events

## Current User Surfaces

- `Login`
  - email/password or Microsoft sign-in
- `Reports`
  - select linked Power BI references during generation
  - export reports as Markdown or HTML
  - queue email delivery
  - queue Teams delivery
- `Dashboard`
  - recent activity
  - Power BI reference cards
- `Documents` and `Assistant`
  - synced SharePoint / OneDrive source metadata appears in document listings and citations

## Delivery Model

- `EMAIL_PROVIDER=preview`
  - writes HTML previews into `storage/emails`
- `EMAIL_PROVIDER=smtp`
  - uses SMTP relay
- `EMAIL_PROVIDER=graph`
  - uses Microsoft Graph `sendMail`
  - requires a specific `MICROSOFT_TENANT_ID`
  - requires `MICROSOFT_OUTLOOK_SENDER`
- `TEAMS_PROVIDER=preview`
  - writes Markdown previews into `storage/teams`
- `TEAMS_PROVIDER=webhook`
  - posts to configured incoming webhook channels

## Power BI Scope

Current scope is metadata and linking, not true embedding:

- report name
- workspace name / ID
- report ID
- report URL
- optional embed URL
- tags

This keeps the MVP enterprise-relevant without taking on full embed token flow or dataset authorization in the same phase.

## Deferred Follow-Up Work

- true multi-tenant isolation instead of tenant-aware single-tenant foundations
- richer Teams management for webhook rotation and secret masking
- Graph-backed Teams bot/app delivery beyond webhook-style posting
- SharePoint / OneDrive permission-aware document filtering at retrieval time
- Power BI embedding with tenant-aware embed tokens
- external worker process for jobs instead of inline background execution in local MVP mode
