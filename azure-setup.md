# Azure / Entra Setup

## Scope

This document covers the current v2 setup for:

- Microsoft organizational sign-in
- SharePoint / OneDrive sync
- Outlook delivery through Microsoft Graph

## 1. Create The Entra App Registration

Configure a Microsoft Entra app registration with:

- Supported account types:
  organizational accounts in this directory only, or organizational accounts in any directory for pilot usage
- Redirect URI:
  `http://localhost:8000/api/v1/auth/microsoft/callback`
  Replace with your deployed API URL in non-local environments.
- Client secret:
  store this in `MICROSOFT_CLIENT_SECRET`

Recommended environment defaults for local development:

- `MICROSOFT_AUTH_ENABLED=true`
- `MICROSOFT_TENANT_ID=organizations`
- `PUBLIC_API_BASE_URL=http://localhost:8000`
- `WEB_BASE_URL=http://localhost:3000`

## 2. Configure Environment Variables

Required:

- `MICROSOFT_CLIENT_ID`
- `MICROSOFT_CLIENT_SECRET`
- `MICROSOFT_TENANT_ID`
- `MICROSOFT_GRAPH_SCOPE=https://graph.microsoft.com/.default`

Required for Graph mail delivery:

- `EMAIL_PROVIDER=graph`
- `MICROSOFT_OUTLOOK_SENDER=<licensed mailbox or shared mailbox UPN>`

Recommended for role mapping:

- `MICROSOFT_ADMIN_EMAILS=user1@contoso.com,user2@contoso.com`
- `MICROSOFT_ADMIN_DOMAINS=contoso.com`

## 3. Add Microsoft Graph Permissions

The app currently needs different permission sets for different features:

- sign-in:
  delegated `openid`, `profile`, `email`, `User.Read`
- SharePoint / OneDrive connectors:
  application `Sites.Read.All`, `Files.Read.All`
- Outlook delivery:
  application `Mail.Send`

Grant admin consent only for the features you plan to use.

## 4. Tenant Choice

- `MICROSOFT_TENANT_ID=organizations`
  good for pilot sign-in and initial setup
- specific tenant GUID or primary domain
  required for app-only Outlook delivery and preferred for production connector rollout

The app intentionally rejects `organizations` / `common` for Graph mail delivery because app-only mailbox operations should be pinned to a specific tenant.

## 5. SharePoint / OneDrive Connector Notes

Before creating connectors in Admin Settings:

- confirm the app registration has application consent for the file/site scopes
- confirm the target SharePoint sites and OneDrive users are reachable by the tenant/app
- start with a narrow library or folder path for initial validation

## 6. Teams Notes

Current Teams delivery is intentionally lightweight:

- local preview mode for development
- webhook-based posting for MVP external delivery

Future bot-based Teams support is intentionally deferred.

## References

- OpenID Connect with Microsoft identity platform:
  https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc
- Access tokens:
  https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens
- Client credentials flow:
  https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow
