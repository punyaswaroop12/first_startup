# Microsoft Graph Permissions

## Current Feature Matrix

Use least privilege and only grant the scopes needed for enabled features.

## Delegated Sign-In Permissions

Used for Entra login:

- `openid`
- `profile`
- `email`
- `User.Read`

These are sufficient for Microsoft login and profile-backed user mapping.

## Application Permissions For Connectors

Used by SharePoint and OneDrive sync jobs:

- `Sites.Read.All`
- `Files.Read.All`

These are app-only permissions because scheduled syncs should not depend on a live delegated user session.

## Application Permissions For Outlook Delivery

Used when `EMAIL_PROVIDER=graph`:

- `Mail.Send`

Operational note:

- configure a specific `MICROSOFT_TENANT_ID`
- configure `MICROSOFT_OUTLOOK_SENDER`
- ensure the mailbox identity is valid for the tenant

## Teams Delivery

Current MVP behavior:

- preview mode requires no Graph permissions
- webhook mode uses Teams webhook infrastructure rather than Graph posting

Future Teams bot/app delivery will likely require additional Graph and Teams app permissions and should be evaluated separately.

## Power BI References

Current scope stores metadata and URLs only. No Graph or embed-token permissions are required for the current implementation.

Future embedding or workspace metadata sync will require a separate review of Power BI and Graph permission boundaries.

## Least-Privilege Guidance

- Keep sign-in permissions separate from connector permissions
- Prefer a specific tenant for production mail delivery
- Start with a narrow SharePoint library or OneDrive folder during pilot rollout
- Avoid broad directory permissions for features that only need file access or mail send
- Review consent and mailbox ownership with the customer’s Microsoft admin before enabling app-only mail

## References

- Graph permissions overview:
  https://learn.microsoft.com/en-us/graph/permissions-overview
- Graph permissions reference:
  https://learn.microsoft.com/en-us/graph/permissions-reference
- Drive and file APIs:
  https://learn.microsoft.com/en-us/graph/api/resources/driveitem
- Send mail:
  https://learn.microsoft.com/en-us/graph/api/user-sendmail
- Teams incoming webhook guidance:
  https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
