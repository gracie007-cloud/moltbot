# Gmail API Setup Guide

## Prerequisites

- Python 3.7+
- Google account
- Google Cloud Project

## Installation

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Google Cloud Configuration

### 1. Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note the project ID

### 2. Enable Gmail API

1. In the Cloud Console, navigate to **APIs & Services > Library**
2. Search for "Gmail API"
3. Click **Enable**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Choose application type:
   - **Desktop app** (for local scripts)
   - **Web application** (for web services)
4. Name your OAuth client
5. For desktop apps, no redirect URIs needed
6. Click **Create**
7. Download the JSON file
8. Rename it to `credentials.json`
9. Place it in your working directory

### 4. Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** (unless using Google Workspace)
3. Fill in required fields:
   - App name
   - User support email
   - Developer contact email
4. Add scopes:
   - `.../auth/gmail.modify` (read, compose, send, and permanently delete emails)
   - OR `.../auth/gmail.readonly` (read-only access)
5. Add test users (for testing phase)
6. Save and continue

## First Run Authentication

On first run, the script will:

1. Open a browser window
2. Ask you to sign in to your Google account
3. Request permission for the app to access Gmail
4. Save credentials to `token.pickle` for future use

## Scopes

The skill uses `gmail.modify` scope by default, which allows:

- Read emails
- Send emails
- Modify labels (mark as read, archive, etc.)
- Move emails to trash

## Troubleshooting

### "Access blocked: This app's request is invalid"

- Ensure OAuth consent screen is properly configured
- Check that your email is added as a test user
- Verify redirect URIs match your application type

### "invalid_grant" Error

- Delete `token.pickle` and re-authenticate
- Ensure credentials.json is from the correct project

### "insufficient_permissions" Error

- Check that required scopes are added in OAuth consent screen
- Delete token.pickle and re-authenticate to refresh permissions

## Security Best Practices

1. **Never commit credentials.json or token.pickle to version control**
2. Add to `.gitignore`:
   ```
   credentials.json
   token.pickle
   ```
3. Use environment variables for sensitive data in production
4. Regularly rotate client secrets
5. Use minimal required scopes

## API Limits

- **Quota**: 1 billion quota units per day (free tier)
- **Rate**: 250 quota units per second per user
- Common operations:
  - List messages: 5 units
  - Get message: 5 units
  - Send message: 100 units
  - Modify labels: 5 units

Monitor usage in Google Cloud Console > APIs & Services > Dashboard.
