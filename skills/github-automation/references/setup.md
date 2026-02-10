# GitHub API Setup Guide

## Prerequisites

- GitHub account
- Python 3.7+

## Installation

```bash
pip install PyGithub
```

## Creating a Personal Access Token

1. Go to GitHub Settings → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Name your token (e.g., "OpenClaw Automation")
4. Select expiration (recommend 90 days for security)
5. Select scopes based on needs:

### Recommended Scopes

**Minimum (read-only):**

- `repo` (full control of private repositories)
  - Includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`

**Full automation:**

- `repo` (full repository access)
- `workflow` (update GitHub Actions workflows)
- `admin:org` → `read:org` (read org data)
- `admin:repo_hook` → `write:repo_hook` (manage webhooks)
- `delete_repo` (delete repositories - optional, use with caution)

6. Click **Generate token**
7. **Copy the token immediately** (you won't see it again)

## Configuration

### Option 1: Environment Variable (Recommended)

```bash
# Linux/Mac
export GITHUB_TOKEN="ghp_your_token_here"

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_your_token_here"

# Windows Command Prompt
set GITHUB_TOKEN=ghp_your_token_here
```

Add to shell profile (~/.bashrc, ~/.zshrc, etc.) for persistence.

### Option 2: Pass Directly to Client

```python
from github_client import GitHubClient

client = GitHubClient(token='ghp_your_token_here')
```

**⚠️ Never commit tokens to version control!**

## Testing the Setup

```python
from scripts.github_client import GitHubClient

# Initialize
client = GitHubClient()

# Test by listing repos
repos = client.list_repos(max_results=5)
print(f"Successfully authenticated! Found {len(repos)} repositories")

# Check rate limit
rate_limit = client.get_rate_limit()
print(f"API calls remaining: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']}")
```

## API Rate Limits

GitHub API has rate limits:

- **Authenticated requests**: 5,000 requests per hour
- **Search API**: 30 requests per minute
- **GraphQL API**: 5,000 points per hour

Check current limit:

```python
rate_limit = client.get_rate_limit()
```

When limit exceeded, requests will fail until reset time.

## Security Best Practices

1. **Use environment variables** - Never hardcode tokens
2. **Minimal scopes** - Only grant necessary permissions
3. **Regular rotation** - Regenerate tokens every 90 days
4. **Separate tokens** - Different tokens for different automation
5. **Monitor usage** - Review token usage in Settings → Developer settings
6. **Revoke unused tokens** - Delete old/unused tokens immediately
7. **Use secrets in CI/CD** - GitHub Actions secrets, not env vars in code

## Troubleshooting

### "Bad credentials" error

- Token expired or invalid
- Regenerate token in GitHub settings
- Verify `GITHUB_TOKEN` environment variable is set correctly

### "Resource not accessible by integration"

- Token missing required scope
- Regenerate token with additional scopes

### "API rate limit exceeded"

- Too many requests in short time
- Wait until reset time (check `get_rate_limit()`)
- Consider using conditional requests (ETags) for efficiency

### "Not Found" for private repositories

- Token needs `repo` scope for private repo access
- Verify you have access to the repository

## GitHub Apps vs Personal Access Tokens

**Personal Access Tokens** (what this skill uses):

- ✅ Simple setup
- ✅ User-level permissions
- ❌ Tied to personal account
- ❌ Limited to 5,000 requests/hour

**GitHub Apps** (alternative for high-volume use):

- ✅ Higher rate limits (5,000 per installation)
- ✅ Fine-grained permissions
- ✅ Organization-level automation
- ❌ More complex setup
- ❌ Requires webhook endpoint

For personal/small team use, Personal Access Tokens are sufficient.

## Additional Resources

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [GitHub API Best Practices](https://docs.github.com/en/rest/guides/best-practices-for-integrators)
- [Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
