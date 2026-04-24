# V2 Enterprise Integrations Checklist

## Discovery And Planning

- [x] Inspect the existing repo and current architecture
- [x] Summarize the current v1 architecture
- [x] Write the v2 Microsoft integrations plan
- [x] Keep `progress.md` updated after each milestone

## Phase 1: Identity Foundation

- [x] Update architecture and integration docs for Microsoft enterprise support
- [x] Add Microsoft / Entra ID configuration and provider scaffolding
- [x] Add tenant and external identity data models
- [x] Add Azure AD login flow and internal user mapping
- [x] Add frontend Microsoft sign-in and callback handling
- [x] Run Phase 1 linting and tests

## Phase 2: SharePoint And OneDrive Connectors

- [x] Add Microsoft Graph client/service layer
- [x] Add connector source models and schemas
- [x] Add SharePoint and OneDrive source management APIs
- [x] Add initial sync and manual re-sync foundations
- [x] Add source attribution metadata for citations

## Phase 3: Sync Jobs And Source Management

- [x] Add background job model and queue orchestration for syncs
- [x] Add sync status tracking and failure logging
- [x] Add admin UI for connector management and sync visibility
- [x] Add incremental update foundation

## Phase 4: Outlook Email And Teams Delivery

- [x] Add Outlook / Graph email delivery provider
- [x] Add Teams delivery provider abstraction
- [x] Add automation actions for Outlook and Teams
- [x] Add admin delivery settings UI

## Phase 5: Power BI And Enterprise Admin

- [x] Add Power BI report metadata model and service layer
- [x] Add dashboard/admin surfaces for Power BI references
- [x] Add Microsoft permissions and role mapping admin visibility
- [x] Expand audit logs for integrations and outbound actions

## Phase 6: Hardening And Demo Readiness

- [x] Add targeted tests for auth, connectors, and delivery paths
- [x] Finalize Microsoft setup and permissions docs
- [x] Update README, architecture, and v2 demo script
- [x] Verify local/dev workflow and Docker guidance

## Phase 7: Final Verification

- [x] Run backend lint and tests after the final changes
- [x] Run frontend lint, typecheck, and production build
- [x] Update `progress.md` with final completion notes and blockers
