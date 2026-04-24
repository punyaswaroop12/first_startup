# Roadmap

## V2 Priorities

1. Identity and tenancy
   Add SSO/SAML, Microsoft Entra ID support, tenant isolation, and admin-managed user invites.

2. Retrieval quality
   Add hybrid search with keyword + vector ranking, metadata filters in chat/report generation, OCR for scanned PDFs, and better chunk deduplication.

3. Workflow depth
   Add approval steps, schedule-based triggers, rule simulation, retry policies, and richer action types like Teams/Slack/webhooks.

4. Observability and controls
   Add metrics dashboards, cost tracking, usage quotas, hardened rate limiting, and richer admin analytics.

5. Integrations
   Add SharePoint, OneDrive, Azure Blob, S3, Outlook/SMTP providers, and common ticketing/work-order systems.

6. Reporting upgrades
   Add PDF export, saved report schedules, branded report layouts, and side-by-side report comparisons over time.

7. Security and compliance
   Add secret management, audit retention controls, PII redaction options, document-level ACLs, and stronger content moderation policies.

8. Deployment maturity
   Add CI/CD, container vulnerability scanning, managed Postgres migrations, and cloud-specific deployment manifests.

## Product Notes

- Keep the rules engine explicit. Resist turning this into an opaque agent framework too early.
- Preserve the provider abstraction boundaries for LLMs, embeddings, storage, and email.
- Maintain the prompt-template-in-files pattern. It keeps behavior reviewable and versioned.

