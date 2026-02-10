# Outlook / Microsoft Graph API Setup Guide

## Prerequisites

- Python 3.7+
- Microsoft account (personal) or Microsoft 365 account (work/school)
- Azure AD application

## Installation

```bash
pip install msal requests
```

## Azure AD Configuration

### 1. Register Application

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory > App registrations**
3. Click **New registration**
4. Fill in details:
   - **Name**: Your application name (e.g., "Email Integration")
   - **Supported account types**: Choose based on use case:
     - Single tenant (your org only)
     - Multitenant (any org)
     - Multitenant + personal accounts (recommended)
   - **Redirect URI**:
     - For desktop apps: `http://localhost`
     - For web apps: Your app's callback URL
5. Click **Register**
6. Note the **Application (client) ID** and **Directory (tenant) ID**

### 2. Create Client Secret (Optional - for service/daemon apps)

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add description and choose expiration
4. Click **Add**
5. **Copy the secret value immediately** (it won't be shown again)

### 3. Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Choose **Microsoft Graph**
4. Select **Delegated permissions** (for user context) or **Application permissions** (for service context)
5. Add required permissions:
   - `Mail.Read` - Read user mail
   - `Mail.ReadWrite` - Read and write access to user mail
   - `Mail.Send` - Send mail as the user
6. Click **Add permissions**
7. For application permissions, click **Grant admin consent** (requires admin)

## Authentication Flows

### Interactive Flow (User Context)

Used when running on behalf of a user (desktop apps, scripts):

```python
from outlook_client import OutlookClient

client = OutlookClient(
    client_id='YOUR_CLIENT_ID',
    tenant_id='common'  # or your specific tenant ID
)
```

First run will open browser for user login.

### Service/Daemon Flow (App Context)

Used for automated services without user interaction:

```python
from outlook_client import OutlookClient

client = OutlookClient(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    tenant_id='YOUR_TENANT_ID'
)
```

Requires application permissions and admin consent.

## Permission Scopes

### Delegated Permissions (User Context)

- `Mail.Read` - Read user's mailbox
- `Mail.ReadWrite` - Read and modify user's mailbox
- `Mail.Send` - Send email as the user
- `Mail.ReadBasic` - Read basic mail properties (no body)

### Application Permissions (Service Context)

- `Mail.Read` - Read mail in all mailboxes
- `Mail.ReadWrite` - Read and write mail in all mailboxes
- `Mail.Send` - Send mail as any user

## Environment Variables (Recommended)

Store credentials securely using environment variables:

```bash
export OUTLOOK_CLIENT_ID="your-client-id"
export OUTLOOK_CLIENT_SECRET="your-client-secret"  # if using
export OUTLOOK_TENANT_ID="your-tenant-id"
```

Then in code:

```python
import os
client = OutlookClient(
    client_id=os.getenv('OUTLOOK_CLIENT_ID'),
    client_secret=os.getenv('OUTLOOK_CLIENT_SECRET'),
    tenant_id=os.getenv('OUTLOOK_TENANT_ID')
)
```

## Token Caching

Tokens are cached in `outlook_token_cache.json` by default to avoid repeated logins.

**Security**: Add to `.gitignore`:

```
outlook_token_cache.json
```

## OData Filter Examples

Microsoft Graph uses OData for filtering:

```python
# Unread messages
client.list_messages(filter_query="isRead eq false")

# From specific sender
client.list_messages(filter_query="from/emailAddress/address eq 'user@example.com'")

# Messages with attachments
client.list_messages(filter_query="hasAttachments eq true")

# Received after date
client.list_messages(filter_query="receivedDateTime ge 2024-01-01T00:00:00Z")

# Complex filters (combine with 'and', 'or')
client.list_messages(filter_query="isRead eq false and hasAttachments eq true")
```

## Search Query Examples

Microsoft Graph search uses KQL (Keyword Query Language):

```python
# Subject search
client.search("subject:meeting")

# From sender
client.search("from:boss@company.com")

# Has attachment
client.search("hasAttachments:true")

# Date range
client.search("received>=2024-01-01")

# Boolean operators
client.search("subject:invoice AND from:finance@company.com")
```

## API Limits

### Throttling Limits

- **Personal accounts**: 10,000 API requests per 10 minutes per user
- **Work/school accounts**: Varies by license (typically 2000-10000 per 10 minutes)

### Rate Limit Headers

Microsoft Graph returns these headers:

- `Retry-After` - Seconds to wait before retrying
- `RateLimit-Limit` - Total requests allowed in window
- `RateLimit-Remaining` - Requests remaining in window

## Troubleshooting

### "AADSTS65001: The user or administrator has not consented"

- Ensure API permissions are added
- Grant admin consent for application permissions
- For delegated permissions, user will consent on first login

### "ErrorAccessDenied: Access is denied"

- Check that required permissions are granted
- Verify token has correct scopes
- Clear token cache and re-authenticate

### "InvalidAuthenticationToken: Access token is empty"

- Token expired - the client will auto-refresh
- Clear `outlook_token_cache.json` and re-authenticate

### "ResourceNotFound: The specified folder could not be found"

- Folder names are case-sensitive
- Use `list_folders()` to see available folders
- Use folder IDs instead of names for reliability

## Security Best Practices

1. **Never commit secrets to version control**
2. Use environment variables for credentials
3. Minimize permissions (principle of least privilege)
4. Rotate client secrets regularly (every 6-12 months)
5. Monitor app usage in Azure AD logs
6. Use certificate-based authentication for production services
7. Implement proper token caching and refresh logic

## Testing

Test with your account first:

```python
# List folders
folders = client.list_folders()
for folder in folders:
    print(f"{folder['displayName']}: {folder['id']}")

# Test search
results = client.search("subject:test", max_results=1)
print(f"Found {len(results)} messages")
```

## Additional Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [OData Query Parameters](https://docs.microsoft.com/en-us/graph/query-parameters)
- [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) - Interactive API testing
