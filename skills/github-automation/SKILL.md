---
name: github-automation
description: Comprehensive GitHub automation for repository management, issues, pull requests, code reviews, and workflow monitoring. Use when tasks involve managing GitHub repositories, creating/updating issues or PRs, reviewing code, searching repositories, monitoring CI/CD workflows, or any GitHub-related automation. Requires GitHub Personal Access Token.
---

# GitHub Automation

Automate GitHub operations including repositories, issues, pull requests, code reviews, and workflow monitoring.

## Quick Start

```python
from scripts.github_client import GitHubClient

# Initialize (requires GITHUB_TOKEN env var or pass token directly)
gh = GitHubClient()

# List repositories
repos = gh.list_repos(max_results=10)

# Create an issue
issue = gh.create_issue(
    repo_name='owner/repo',
    title='Bug: Login not working',
    body='Description of the bug...',
    labels=['bug', 'priority-high']
)

# List pull requests
prs = gh.list_pulls('owner/repo', state='open')
```

## Setup

**First time?** See [setup.md](references/setup.md) for:

- Creating a GitHub Personal Access Token
- Configuring authentication
- Scope selection guide

Quick setup:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
pip install PyGithub
```

## Repository Operations

### List Repositories

```python
# Your repos (owner)
repos = gh.list_repos(affiliation='owner', max_results=30)

# Repos you collaborate on
repos = gh.list_repos(affiliation='collaborator')

# All accessible repos
repos = gh.list_repos(affiliation='owner,collaborator,organization_member')

# Sort by last updated
repos = gh.list_repos(sort='updated')
```

### Get Repository Details

```python
# Full repo name
repo = gh.get_repo('owner/repo')

# Short name (uses authenticated user)
repo = gh.get_repo('repo-name')

print(f"{repo['full_name']}: {repo['stars']} stars, {repo['open_issues']} open issues")
```

### Create Repository

```python
repo = gh.create_repo(
    name='my-new-repo',
    description='A cool project',
    private=True,
    auto_init=True  # Initialize with README
)
```

## Issue Management

### List Issues

```python
# Open issues
issues = gh.list_issues('owner/repo', state='open')

# Closed issues
issues = gh.list_issues('owner/repo', state='closed')

# Filter by labels
issues = gh.list_issues('owner/repo', labels=['bug', 'urgent'])

# Filter by assignee
issues = gh.list_issues('owner/repo', assignee='username')

# All issues
issues = gh.list_issues('owner/repo', state='all', max_results=100)
```

### Get Issue Details

```python
issue = gh.get_issue('owner/repo', 123)

print(f"#{issue['number']}: {issue['title']}")
print(f"Status: {issue['state']}")
print(f"Labels: {', '.join(issue['labels'])}")
print(f"Body: {issue['body']}")
```

### Create Issue

```python
issue = gh.create_issue(
    repo_name='owner/repo',
    title='Feature: Add dark mode',
    body='Users are requesting dark mode support...',
    labels=['enhancement', 'ui'],
    assignees=['developer1', 'developer2']
)

print(f"Created issue #{issue['number']}: {issue['url']}")
```

### Update Issue

```python
# Update title/body
gh.update_issue('owner/repo', 123,
    title='Updated Title',
    body='Updated description'
)

# Close issue
gh.update_issue('owner/repo', 123, state='closed')

# Change labels
gh.update_issue('owner/repo', 123, labels=['bug', 'fixed'])

# Change assignees
gh.update_issue('owner/repo', 123, assignees=['new-assignee'])
```

### Comment on Issue

```python
comment = gh.comment_on_issue(
    repo_name='owner/repo',
    issue_number=123,
    comment='Fixed in PR #456'
)
```

## Pull Request Operations

### List Pull Requests

```python
# Open PRs
prs = gh.list_pulls('owner/repo', state='open')

# Merged PRs
prs = gh.list_pulls('owner/repo', state='closed')

# Filter by base branch
prs = gh.list_pulls('owner/repo', base='main')

# Filter by head branch
prs = gh.list_pulls('owner/repo', head='feature-branch')
```

### Get PR Details

```python
pr = gh.get_pull('owner/repo', 456)

print(f"PR #{pr['number']}: {pr['title']}")
print(f"From: {pr['head']} → {pr['base']}")
print(f"Mergeable: {pr['mergeable']}")
print(f"Changes: +{pr['additions']} -{pr['deletions']} in {pr['changed_files']} files")
```

### Create Pull Request

```python
pr = gh.create_pull(
    repo_name='owner/repo',
    title='Add new feature',
    head='feature-branch',
    base='main',
    body='## Changes\n- Added X\n- Fixed Y',
    draft=False
)

print(f"Created PR #{pr['number']}: {pr['url']}")
```

### Merge Pull Request

```python
# Default merge
result = gh.merge_pull('owner/repo', 456)

# Squash merge
result = gh.merge_pull('owner/repo', 456, merge_method='squash')

# Rebase merge
result = gh.merge_pull('owner/repo', 456, merge_method='rebase')

# Custom commit message
result = gh.merge_pull(
    'owner/repo', 456,
    commit_message='Merge: Add feature X (#456)',
    merge_method='merge'
)

print(f"Merged: {result['merged']}, SHA: {result['sha']}")
```

### Review Pull Request

```python
# Approve PR
review = gh.review_pull(
    repo_name='owner/repo',
    pr_number=456,
    event='APPROVE',
    body='LGTM! Great work!'
)

# Request changes
review = gh.review_pull(
    repo_name='owner/repo',
    pr_number=456,
    event='REQUEST_CHANGES',
    body='Please address the following issues...'
)

# Comment only (no approval/rejection)
review = gh.review_pull(
    repo_name='owner/repo',
    pr_number=456,
    event='COMMENT',
    body='Some observations...'
)

# Review with inline comments
review = gh.review_pull(
    repo_name='owner/repo',
    pr_number=456,
    event='APPROVE',
    body='Overall looks good!',
    comments=[
        {'path': 'src/app.py', 'position': 10, 'body': 'Nice refactor here!'},
        {'path': 'tests/test.py', 'position': 5, 'body': 'Good test coverage'}
    ]
)
```

## Workflow Monitoring

### List Workflow Runs

```python
# All recent runs
runs = gh.list_workflow_runs('owner/repo', max_results=20)

# Only completed runs
runs = gh.list_workflow_runs('owner/repo', status='completed')

# Failed runs
runs = gh.list_workflow_runs('owner/repo', status='failure')

for run in runs:
    print(f"{run['name']}: {run['status']} - {run['conclusion']}")
    print(f"  Branch: {run['head_branch']}")
    print(f"  URL: {run['url']}")
```

## Code Search

```python
# Search by filename
results = gh.search_code('filename:package.json')

# Search in specific repo
results = gh.search_code('repo:owner/repo TODO')

# Search by language
results = gh.search_code('language:python requests')

# Complex query
results = gh.search_code('language:python class User in:file')

for result in results:
    print(f"{result['repo']}/{result['path']}")
    print(f"  {result['url']}")
```

## Common Workflows

### Triage New Issues

```python
# Get unread issues with specific label
issues = gh.list_issues('owner/repo', labels=['needs-triage'])

for issue in issues:
    print(f"#{issue['number']}: {issue['title']}")
    print(f"  Created by: {issue['user']}")
    print(f"  {issue['url']}")

    # Auto-label based on title keywords
    title_lower = issue['title'].lower()
    new_labels = issue['labels'].copy()

    if 'bug' in title_lower or 'error' in title_lower:
        new_labels.append('bug')
    if 'feature' in title_lower or 'enhancement' in title_lower:
        new_labels.append('enhancement')

    if new_labels != issue['labels']:
        gh.update_issue('owner/repo', issue['number'], labels=new_labels)
        print(f"  → Added labels: {new_labels}")
```

### Auto-Merge Approved PRs

```python
# Get open PRs
prs = gh.list_pulls('owner/repo', state='open')

for pr in prs:
    # Check if mergeable and has approvals
    pr_full = gh.get_pull('owner/repo', pr['number'])

    if pr_full['mergeable'] and not pr_full['draft']:
        # Auto-merge (add logic to check for approvals via reviews)
        print(f"PR #{pr['number']} ready to merge")
        # gh.merge_pull('owner/repo', pr['number'], merge_method='squash')
```

### Monitor Failed Workflows

```python
# Get failed workflow runs from the last day
runs = gh.list_workflow_runs('owner/repo', status='failure', max_results=50)

failed_today = []
from datetime import datetime, timedelta
today = datetime.now() - timedelta(days=1)

for run in runs:
    run_time = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
    if run_time > today:
        failed_today.append(run)

if failed_today:
    print(f"Warning: {len(failed_today)} workflow failures in the last 24 hours:")
    for run in failed_today:
        print(f"  {run['name']} on {run['head_branch']}")
        print(f"    {run['url']}")
```

### Bulk Issue Operations

```python
# Close old stale issues
issues = gh.list_issues('owner/repo', state='open', labels=['stale'])

for issue in issues:
    gh.comment_on_issue(
        'owner/repo',
        issue['number'],
        'Closing due to inactivity. Please reopen if still relevant.'
    )
    gh.update_issue('owner/repo', issue['number'], state='closed')
    print(f"Closed #{issue['number']}")
```

## Rate Limit Management

```python
# Check current rate limit
rate_limit = gh.get_rate_limit()

print(f"Core API: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']}")
print(f"Search API: {rate_limit['search']['remaining']}/{rate_limit['search']['limit']}")
print(f"Resets at: {rate_limit['core']['reset']}")

# Check before expensive operations
if rate_limit['core']['remaining'] < 100:
    print("Warning: Low API calls remaining!")
```

## Error Handling

```python
try:
    issue = gh.create_issue('owner/repo', title='Bug report', body='...')
except Exception as e:
    print(f"Failed to create issue: {e}")
```

Common errors:

- `Bad credentials` → Token expired or invalid
- `Not Found` → Repository doesn't exist or no access
- `Resource not accessible` → Missing required scope on token
- Rate limit exceeded → Wait until reset time

## Tips & Best Practices

1. **Check rate limits** before bulk operations
2. **Use labels** for organization and filtering
3. **Batch operations** when possible to reduce API calls
4. **Cache results** for data that doesn't change frequently
5. **Use webhooks** instead of polling for real-time updates (requires GitHub App)
6. **Validate permissions** before attempting operations

## Limitations

- Personal access tokens limited to 5,000 requests/hour
- Search API: 30 requests/minute
- Cannot access private repos without `repo` scope
- Some admin operations require specific scopes

## Dependencies

```bash
pip install PyGithub
```

## Additional Resources

- [references/setup.md](references/setup.md) - Complete setup guide
- [GitHub REST API Docs](https://docs.github.com/en/rest)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
