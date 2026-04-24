# Real Environment Test Plan

Manual validation plan for the real Microsoft-enabled environment.

## Scope

Validate:

- Microsoft login
- SharePoint sync
- OneDrive sync
- Outlook delivery
- Teams delivery
- Power BI references

This plan assumes the environment has already been prepared using [real-env-checklist.md](/Users/punyaswaroopsirigiri/first_startup/real-env-checklist.md).

## Test Preconditions

Before starting, confirm:

- The web app and API are running in the real target environment.
- `MICROSOFT_AUTH_ENABLED=true`.
- If real AI behavior is being tested, `AI_PROVIDER=openai` with a valid `OPENAI_API_KEY`.
- The Entra app registration has the delegated and application permissions required by the enabled features.
- At least one admin test user exists or will be role-mapped on first Microsoft sign-in.
- A SharePoint site/library/folder is ready with a small set of known files.
- A OneDrive user and folder are ready with a small set of known files.
- A sender mailbox exists for Graph mail validation if `EMAIL_PROVIDER=graph`.
- A Teams incoming webhook exists if `TEAMS_PROVIDER=webhook`.
- At least one Power BI report URL is available for admin entry.

Recommended test assets:

- 2 to 5 documents in SharePoint with recognizable text and distinct tags
- 2 to 5 documents in OneDrive with recognizable text and distinct tags
- 1 test report recipient list
- 1 Teams validation channel
- 1 to 2 Power BI report links

## Evidence To Capture

For each section below, capture:

- Screenshot of the relevant UI state
- Timestamp of the action
- Any API/UI error text
- The expected result and the actual result

## 1. Microsoft Login

### Purpose

Verify Entra sign-in, user mapping, and role assignment behavior.

### Steps

1. Open the login page.
2. Confirm the Microsoft sign-in option is visible.
3. Sign in with a standard tenant user.
4. Confirm the user lands in the app successfully.
5. Confirm the user profile appears in the sidebar or authenticated shell.
6. Sign out.
7. Sign in with a user expected to become an admin through `MICROSOFT_ADMIN_EMAILS` or `MICROSOFT_ADMIN_DOMAINS`.
8. Confirm the admin user can access `Admin Settings`.

### Expected Results

- Microsoft sign-in starts without redirect errors.
- The callback completes successfully.
- The user record is created or refreshed in the app.
- The role mapping scaffold behaves as configured.
- The admin-mapped user can access admin-only pages.

### Failure Checks

- Missing Microsoft button
- Redirect URI mismatch
- Consent or permission error during sign-in
- User signs in but cannot complete callback
- Admin mapping does not apply as expected

## 2. SharePoint Sync

### Purpose

Verify SharePoint connector creation, sync execution, indexing, and source attribution.

### Steps

1. Sign in as an admin user.
2. Go to `Admin Settings`.
3. Create a new SharePoint connector with:
   - connector type `SharePoint document library`
   - tenant
   - site hostname
   - site path
   - library name
   - folder path
   - default tags
4. Enable `Run initial sync immediately`.
5. Save the connector.
6. Confirm a sync job is created and eventually reaches a successful state.
7. Open `Documents`.
8. Confirm synced SharePoint files appear.
9. Open `Chat Assistant` and ask a question whose answer should come from one synced SharePoint file.
10. Confirm the response cites the synced document and preserves source attribution.
11. Change or add one document in SharePoint.
12. Trigger a manual re-sync from `Admin Settings`.
13. Confirm the document list and retrieval results reflect the update.

### Expected Results

- Connector saves successfully.
- Sync job status is visible.
- SharePoint documents are ingested into the knowledge base.
- Citations reference the correct document and source metadata.
- Manual re-sync updates the indexed content.

### Failure Checks

- Connector save fails
- Sync job fails with Graph or path error
- Documents sync but do not appear in search/chat
- Citations lose source path or source URL context
- Re-sync does not pick up a changed file

## 3. OneDrive Sync

### Purpose

Verify OneDrive connector creation and retrieval over OneDrive-sourced content.

### Steps

1. Sign in as an admin user.
2. Go to `Admin Settings`.
3. Create a new OneDrive connector with:
   - connector type `OneDrive folder`
   - tenant
   - user principal name
   - folder path
   - default tags
4. Enable `Run initial sync immediately`.
5. Save the connector.
6. Confirm a sync job is created and completes.
7. Open `Documents`.
8. Confirm synced OneDrive files appear.
9. Ask a question in `Chat Assistant` that should only be answerable from OneDrive content.
10. Confirm the answer cites the OneDrive-synced document.
11. Trigger a manual re-sync after updating one OneDrive file.
12. Confirm the changes appear in retrieval results.

### Expected Results

- OneDrive connector saves and syncs.
- Documents are retrievable and cited correctly.
- Manual sync reflects updated content.

### Failure Checks

- UPN or folder path resolution fails
- OneDrive files ingest but cannot be cited
- Updated files do not refresh after re-sync

## 4. Outlook Delivery

### Purpose

Verify report delivery through Microsoft Graph mail.

### Steps

1. Confirm `EMAIL_PROVIDER=graph` in the environment.
2. Confirm `MICROSOFT_OUTLOOK_SENDER` is configured to a valid mailbox.
3. Sign in as a user who can generate reports.
4. Open `Reports`.
5. Generate an executive or operational report from real content.
6. Enter one or more approved recipient addresses.
7. Trigger `Email` delivery from the report history card.
8. Confirm the UI reports that the delivery job was queued.
9. Go to `Admin Settings` and inspect recent jobs or audit events.
10. Confirm the email arrives in the target mailbox.

### Expected Results

- The report delivery action queues successfully.
- Background job status updates appropriately.
- Audit log records the outbound action.
- The email arrives with expected subject/body content.

### Failure Checks

- Delivery job fails immediately
- Graph mail permission error
- Sender mailbox error
- Recipient receives nothing despite a successful UI message

## 5. Teams Delivery

### Purpose

Verify Teams delivery through the configured channel.

### Steps

1. Confirm `TEAMS_PROVIDER=webhook` in the environment.
2. Sign in as an admin user.
3. Open `Admin Settings`.
4. Create or confirm a Teams delivery channel with:
   - delivery type appropriate to the environment
   - webhook URL if using webhook mode
   - active status
5. Mark the channel as the default channel if desired.
6. Generate a report from `Reports`.
7. Trigger `Teams` delivery from the report history card.
8. Confirm the UI reports that the delivery job was queued.
9. Confirm the message appears in the target Teams channel.
10. Optionally trigger an automation path that posts to Teams and confirm the message appears.

### Expected Results

- Teams channel configuration saves.
- Report delivery queues successfully.
- The message is posted to the expected Teams channel.
- Audit/job tracking reflects the outbound action.

### Failure Checks

- Webhook URL rejected or invalid
- Teams delivery job fails
- No channel message appears
- Wrong channel receives the notification

## 6. Power BI References

### Purpose

Verify admin-managed Power BI metadata appears in the correct user surfaces.

### Steps

1. Sign in as an admin user.
2. Go to `Admin Settings`.
3. Create one or more Power BI references with:
   - name
   - workspace name
   - report URL
   - optional embed URL
   - tags
4. Save the references.
5. Open `Dashboard`.
6. Confirm Power BI cards appear.
7. Open `Reports`.
8. Confirm the Power BI references can be selected for report generation.
9. Generate a report with one or more Power BI references selected.
10. Confirm the generated report includes linked Power BI references.

### Expected Results

- Power BI references save successfully.
- Dashboard cards render with the correct labels and links.
- Report generation supports linked Power BI context.
- Generated report output includes the selected references.

### Failure Checks

- Reference save fails
- Dashboard cards do not render
- Reports page cannot select references
- Report output omits selected references

## 7. Cross-Feature Regression Checks

Run these after the targeted tests above.

### Steps

1. Confirm `Documents` shows both manually uploaded and Microsoft-synced documents.
2. Ask at least one question that should cite SharePoint content and one that should cite OneDrive content.
3. Generate one report after connector syncs complete.
4. Trigger one Outlook delivery and one Teams delivery from the final report.
5. Review `Admin Settings > Audit log` and `Sync jobs`.

### Expected Results

- Mixed source documents coexist correctly.
- Retrieval still cites the correct source after multiple syncs.
- Audit entries exist for sync, report generation, email delivery, and Teams delivery.
- No blocking runtime or UI errors appear.

## Exit Criteria

The environment is ready for broader pilot use when all of the following are true:

- Microsoft login succeeds for both standard and admin-mapped users.
- At least one SharePoint connector sync completes and produces searchable content.
- At least one OneDrive connector sync completes and produces searchable content.
- Outlook delivery succeeds end to end.
- Teams delivery succeeds end to end.
- Power BI references are visible in dashboard and report flows.
- Audit logs and job status surfaces reflect the actions taken.
