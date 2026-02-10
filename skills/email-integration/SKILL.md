---
name: email-integration
description: Comprehensive email integration for Gmail and Outlook/Microsoft 365 with full support for reading, sending, searching, and managing emails. Use when tasks involve checking inbox, sending emails, managing email (archive/delete/mark as read), searching emails, or any email-related operations. Supports both personal (Gmail, Outlook.com) and enterprise (Google Workspace, Microsoft 365) accounts.
---

# Email Integration

Comprehensive email client supporting Gmail and Outlook with all core email operations.

## Quick Start

### Gmail

```python
from scripts.gmail_client import GmailClient

# Initialize (requires credentials.json in working directory)
gmail = GmailClient()

# List unread messages
unread = gmail.list_messages(query='is:unread', max_results=10)

# Send email
gmail.send_message(
    to='recipient@example.com',
    subject='Hello',
    body='This is a test email'
)
```

### Outlook

```python
from scripts.outlook_client import OutlookClient

# Initialize with Azure AD app credentials
outlook = OutlookClient(
    client_id='YOUR_CLIENT_ID',
    tenant_id='common'  # or specific tenant ID
)

# List unread messages
unread = outlook.list_messages(filter_query="isRead eq false", max_results=10)

# Send email
outlook.send_message(
    to='recipient@example.com',
    subject='Hello',
    body='This is a test email'
)
```

## Setup

**First time using this skill?** Read the setup guides:

- **Gmail**: See [gmail-setup.md](references/gmail-setup.md) for Google Cloud configuration
- **Outlook**: See [outlook-setup.md](references/outlook-setup.md) for Azure AD configuration

Both clients require initial API setup and authentication. The setup guides provide step-by-step instructions.

## Core Operations

### List Messages

**Gmail:**

```python
# Unread messages
messages = gmail.list_messages(query='is:unread', max_results=20)

# Messages from specific sender
messages = gmail.list_messages(query='from:boss@company.com', max_results=10)

# With labels
messages = gmail.list_messages(label_ids=['INBOX', 'IMPORTANT'], max_results=10)
```

**Outlook:**

```python
# Unread messages
messages = outlook.list_messages(filter_query="isRead eq false", max_results=20)

# Messages from specific sender
messages = outlook.list_messages(
    filter_query="from/emailAddress/address eq 'boss@company.com'",
    max_results=10
)

# Different folder
messages = outlook.list_messages(folder='sentitems', max_results=10)
```

### Get Message Details

**Gmail:**

```python
message = gmail.get_message(message_id)
print(f"From: {message['from']}")
print(f"Subject: {message['subject']}")
print(f"Body: {message['body']}")
```

**Outlook:**

```python
message = outlook.get_message(message_id)
print(f"From: {message['from']['emailAddress']['address']}")
print(f"Subject: {message['subject']}")
print(f"Body: {message['body']['content']}")
```

### Send Email

**Gmail:**

```python
gmail.send_message(
    to='recipient@example.com',
    subject='Project Update',
    body='Here is the latest update...',
    cc='manager@example.com',  # optional
    attachments=['report.pdf', 'data.xlsx']  # optional
)
```

**Outlook:**

```python
outlook.send_message(
    to='recipient@example.com',
    subject='Project Update',
    body='Here is the latest update...',
    cc='manager@example.com',  # optional
    attachments=['report.pdf'],  # optional
    body_type='Text'  # or 'HTML'
)
```

### Search

**Gmail (uses Gmail search syntax):**

```python
# Subject search
results = gmail.search('subject:invoice')

# From sender with date range
results = gmail.search('from:finance@company.com after:2024/01/01')

# Has attachment
results = gmail.search('has:attachment')

# Complex queries
results = gmail.search('subject:meeting is:unread has:attachment')
```

**Outlook (uses KQL syntax):**

```python
# Subject search
results = outlook.search('subject:invoice')

# From sender
results = outlook.search('from:finance@company.com')

# Has attachment and date
results = outlook.search('hasAttachments:true received>=2024-01-01')

# Boolean operators
results = outlook.search('subject:meeting AND from:boss@company.com')
```

### Mark as Read/Unread

**Gmail:**

```python
# Single message
gmail.mark_as_read(message_id)

# Multiple messages
gmail.mark_as_read([msg_id1, msg_id2, msg_id3])

# Mark as unread
gmail.mark_as_unread(message_id)
```

**Outlook:**

```python
# Single message
outlook.mark_as_read(message_id)

# Multiple messages
outlook.mark_as_read([msg_id1, msg_id2, msg_id3])

# Mark as unread
outlook.mark_as_unread(message_id)
```

### Archive

**Gmail:**

```python
# Archives by removing INBOX label
gmail.archive(message_id)
gmail.archive([msg_id1, msg_id2])
```

**Outlook:**

```python
# Moves to Archive folder (must exist)
outlook.archive(message_id)
outlook.archive([msg_id1, msg_id2])
```

### Delete

**Gmail:**

```python
# Moves to Trash (recoverable)
gmail.delete(message_id)
gmail.delete([msg_id1, msg_id2])
```

**Outlook:**

```python
# Moves to Deleted Items (recoverable)
outlook.delete(message_id)
outlook.delete([msg_id1, msg_id2])
```

## Common Patterns

### Check for Urgent Emails

```python
# Gmail
urgent = gmail.list_messages(query='is:unread label:important', max_results=5)

# Outlook
urgent = outlook.list_messages(
    filter_query="isRead eq false and importance eq 'high'",
    max_results=5
)

for msg in urgent:
    print(f"URGENT: {msg['subject']} from {msg['from']}")
```

### Process Inbox

```python
# Gmail
unread = gmail.list_messages(query='is:unread', max_results=50)

for msg in unread:
    print(f"Processing: {msg['subject']}")

    # Your processing logic here

    # Mark as read when done
    gmail.mark_as_read(msg['id'])
```

### Bulk Archive Old Emails

```python
# Gmail - archive emails older than 30 days
old_emails = gmail.search('in:inbox older_than:30d', max_results=100)
message_ids = [msg['id'] for msg in old_emails]

if message_ids:
    gmail.archive(message_ids)
    print(f"Archived {len(message_ids)} old emails")
```

### Send with Multiple Recipients

```python
# Gmail - accepts list or comma-separated string
gmail.send_message(
    to=['user1@example.com', 'user2@example.com'],
    cc='manager@example.com',
    bcc=['archive@company.com'],
    subject='Team Update',
    body='Weekly status report...'
)

# Outlook - same pattern
outlook.send_message(
    to=['user1@example.com', 'user2@example.com'],
    cc='manager@example.com',
    subject='Team Update',
    body='Weekly status report...'
)
```

## Query Syntax Reference

### Gmail Search Operators

Common operators:

- `is:unread` / `is:read` - Read status
- `is:starred` - Starred emails
- `has:attachment` - Has attachments
- `from:user@example.com` - From sender
- `to:user@example.com` - To recipient
- `subject:keyword` - Subject contains keyword
- `after:YYYY/MM/DD` - After date
- `before:YYYY/MM/DD` - Before date
- `older_than:Xd` - Older than X days
- `newer_than:Xd` - Newer than X days
- `label:labelname` - Has label
- `in:inbox` / `in:sent` / `in:trash` - Location

Combine with AND (space) or OR:

```python
gmail.search('from:boss@company.com subject:urgent')  # AND
gmail.search('from:boss@company.com OR from:manager@company.com')  # OR
```

### Outlook OData Filters

Common filters for `list_messages()`:

- `isRead eq false` - Unread
- `isRead eq true` - Read
- `hasAttachments eq true` - Has attachments
- `from/emailAddress/address eq 'user@example.com'` - From sender
- `receivedDateTime ge 2024-01-01T00:00:00Z` - After date
- `importance eq 'high'` - High importance

Combine with `and` / `or`:

```python
outlook.list_messages(filter_query="isRead eq false and hasAttachments eq true")
```

### Outlook KQL Search

Common search operators for `search()`:

- `from:user@example.com` - From sender
- `to:user@example.com` - To recipient
- `subject:keyword` - Subject contains
- `hasAttachments:true` - Has attachments
- `received>=YYYY-MM-DD` - Received after date
- `received<=YYYY-MM-DD` - Received before date
- `importance:high` - High importance

Combine with AND / OR:

```python
outlook.search('from:boss@company.com AND subject:urgent')
```

## Credential Management

### Gmail

- Requires `credentials.json` (from Google Cloud Console)
- Stores token in `token.pickle` after first authentication
- Add to `.gitignore`: `credentials.json`, `token.pickle`

### Outlook

- Requires Azure AD app credentials (client ID, optional secret)
- Stores token in `outlook_token_cache.json`
- Add to `.gitignore`: `outlook_token_cache.json`

**Environment variables (recommended for production):**

```bash
# Gmail
export GMAIL_CREDENTIALS_PATH="/path/to/credentials.json"
export GMAIL_TOKEN_PATH="/path/to/token.pickle"

# Outlook
export OUTLOOK_CLIENT_ID="your-client-id"
export OUTLOOK_CLIENT_SECRET="your-client-secret"  # if using
export OUTLOOK_TENANT_ID="your-tenant-id"
```

## Error Handling

Both clients raise exceptions on errors. Wrap calls in try-except:

```python
try:
    gmail.send_message(to='user@example.com', subject='Test', body='Hello')
    print("Email sent successfully")
except Exception as e:
    print(f"Failed to send: {e}")
```

Common errors:

- Authentication failures → Re-run setup, check credentials
- Quota exceeded → Wait and retry, check API limits
- Invalid message ID → Verify the ID exists
- Network errors → Retry with exponential backoff

## Limitations

### Gmail

- Daily quota: 1 billion units (typical usage: thousands of emails)
- Send limit: 500 emails/day (personal), 2000/day (Google Workspace)
- Attachment size: 25MB per email

### Outlook

- Rate limits vary by account type (see setup guide)
- Personal: ~10,000 requests per 10 minutes
- Attachment size: Varies by account (typically 25-150MB)

## Dependencies

```bash
# Gmail
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Outlook
pip install msal requests
```

## Choosing Between Gmail and Outlook

Use **Gmail** when:

- User has Gmail or Google Workspace account
- Need powerful search with Gmail operators
- Integrating with other Google services

Use **Outlook** when:

- User has Outlook.com or Microsoft 365 account
- Enterprise environment using Microsoft services
- Need service/daemon automation (app-only auth)

Both clients provide equivalent functionality. The main differences are authentication setup and query syntax.

## Additional Resources

- [references/gmail-setup.md](references/gmail-setup.md) - Complete Gmail API setup guide
- [references/outlook-setup.md](references/outlook-setup.md) - Complete Outlook/Graph API setup guide
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Microsoft Graph Mail API](https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview)
