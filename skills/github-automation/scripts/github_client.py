#!/usr/bin/env python3
"""
GitHub automation client for repository, issue, and PR management.
Requires: PyGithub
Install: pip install PyGithub
"""

import os
from typing import List, Optional, Dict
from github import Github, GithubException
from datetime import datetime, timedelta

class GitHubClient:
    def __init__(self, token=None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (or use GITHUB_TOKEN env var)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var or pass token parameter.")
        
        self.gh = Github(self.token)
        self.user = self.gh.get_user()
    
    # ===== Repository Operations =====
    
    def list_repos(self, affiliation='owner', sort='updated', max_results=30):
        """
        List user's repositories.
        
        Args:
            affiliation: 'owner', 'collaborator', 'organization_member'
            sort: 'created', 'updated', 'pushed', 'full_name'
            max_results: Max repos to return
        """
        repos = self.user.get_repos(affiliation=affiliation, sort=sort)
        return [self._format_repo(repo) for repo in repos[:max_results]]
    
    def get_repo(self, repo_name):
        """
        Get repository details.
        
        Args:
            repo_name: 'owner/repo' or just 'repo' (uses authenticated user)
        """
        if '/' not in repo_name:
            repo_name = f"{self.user.login}/{repo_name}"
        
        repo = self.gh.get_repo(repo_name)
        return self._format_repo(repo)
    
    def create_repo(self, name, description='', private=False, auto_init=False):
        """Create a new repository."""
        repo = self.user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init
        )
        return self._format_repo(repo)
    
    def _format_repo(self, repo):
        """Format repository object."""
        return {
            'name': repo.name,
            'full_name': repo.full_name,
            'description': repo.description,
            'private': repo.private,
            'url': repo.html_url,
            'clone_url': repo.clone_url,
            'default_branch': repo.default_branch,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'open_issues': repo.open_issues_count,
            'language': repo.language,
            'created_at': repo.created_at.isoformat(),
            'updated_at': repo.updated_at.isoformat(),
            'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None
        }
    
    # ===== Issue Operations =====
    
    def list_issues(self, repo_name, state='open', labels=None, assignee=None, max_results=30):
        """
        List issues in a repository.
        
        Args:
            repo_name: 'owner/repo'
            state: 'open', 'closed', 'all'
            labels: List of label names to filter by
            assignee: Username to filter by assignee
            max_results: Max issues to return
        """
        repo = self.gh.get_repo(repo_name)
        
        kwargs = {'state': state}
        if labels:
            kwargs['labels'] = labels
        if assignee:
            kwargs['assignee'] = assignee
        
        issues = repo.get_issues(**kwargs)
        return [self._format_issue(issue) for issue in issues[:max_results]]
    
    def get_issue(self, repo_name, issue_number):
        """Get issue details."""
        repo = self.gh.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        return self._format_issue(issue)
    
    def create_issue(self, repo_name, title, body='', labels=None, assignees=None):
        """
        Create a new issue.
        
        Args:
            repo_name: 'owner/repo'
            title: Issue title
            body: Issue body/description
            labels: List of label names
            assignees: List of usernames to assign
        """
        repo = self.gh.get_repo(repo_name)
        
        kwargs = {'title': title, 'body': body}
        if labels:
            kwargs['labels'] = labels
        if assignees:
            kwargs['assignees'] = assignees
        
        issue = repo.create_issue(**kwargs)
        return self._format_issue(issue)
    
    def update_issue(self, repo_name, issue_number, title=None, body=None, state=None, labels=None, assignees=None):
        """Update an existing issue."""
        repo = self.gh.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        
        if title:
            issue.edit(title=title)
        if body:
            issue.edit(body=body)
        if state:
            issue.edit(state=state)
        if labels is not None:
            issue.set_labels(*labels)
        if assignees is not None:
            issue.edit(assignees=assignees)
        
        return self._format_issue(issue)
    
    def comment_on_issue(self, repo_name, issue_number, comment):
        """Add a comment to an issue."""
        repo = self.gh.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        comment_obj = issue.create_comment(comment)
        return {
            'id': comment_obj.id,
            'body': comment_obj.body,
            'user': comment_obj.user.login,
            'created_at': comment_obj.created_at.isoformat()
        }
    
    def _format_issue(self, issue):
        """Format issue object."""
        return {
            'number': issue.number,
            'title': issue.title,
            'body': issue.body,
            'state': issue.state,
            'url': issue.html_url,
            'user': issue.user.login,
            'labels': [label.name for label in issue.labels],
            'assignees': [assignee.login for assignee in issue.assignees],
            'comments': issue.comments,
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat(),
            'closed_at': issue.closed_at.isoformat() if issue.closed_at else None
        }
    
    # ===== Pull Request Operations =====
    
    def list_pulls(self, repo_name, state='open', base=None, head=None, max_results=30):
        """
        List pull requests.
        
        Args:
            repo_name: 'owner/repo'
            state: 'open', 'closed', 'all'
            base: Base branch to filter by
            head: Head branch to filter by
            max_results: Max PRs to return
        """
        repo = self.gh.get_repo(repo_name)
        
        kwargs = {'state': state}
        if base:
            kwargs['base'] = base
        if head:
            kwargs['head'] = head
        
        pulls = repo.get_pulls(**kwargs)
        return [self._format_pr(pr) for pr in pulls[:max_results]]
    
    def get_pull(self, repo_name, pr_number):
        """Get pull request details."""
        repo = self.gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        return self._format_pr(pr)
    
    def create_pull(self, repo_name, title, head, base, body='', draft=False):
        """
        Create a pull request.
        
        Args:
            repo_name: 'owner/repo'
            title: PR title
            head: Branch containing changes
            base: Branch to merge into
            body: PR description
            draft: Create as draft PR
        """
        repo = self.gh.get_repo(repo_name)
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
            draft=draft
        )
        return self._format_pr(pr)
    
    def merge_pull(self, repo_name, pr_number, commit_message=None, merge_method='merge'):
        """
        Merge a pull request.
        
        Args:
            repo_name: 'owner/repo'
            pr_number: PR number
            commit_message: Custom merge commit message
            merge_method: 'merge', 'squash', 'rebase'
        """
        repo = self.gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        result = pr.merge(
            commit_message=commit_message,
            merge_method=merge_method
        )
        
        return {
            'merged': result.merged,
            'message': result.message,
            'sha': result.sha
        }
    
    def review_pull(self, repo_name, pr_number, event, body='', comments=None):
        """
        Submit a pull request review.
        
        Args:
            repo_name: 'owner/repo'
            pr_number: PR number
            event: 'APPROVE', 'REQUEST_CHANGES', 'COMMENT'
            body: Review summary comment
            comments: List of {path, position, body} for inline comments
        """
        repo = self.gh.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        kwargs = {'event': event}
        if body:
            kwargs['body'] = body
        if comments:
            kwargs['comments'] = comments
        
        review = pr.create_review(**kwargs)
        return {
            'id': review.id,
            'state': review.state,
            'body': review.body,
            'user': review.user.login,
            'submitted_at': review.submitted_at.isoformat()
        }
    
    def _format_pr(self, pr):
        """Format pull request object."""
        return {
            'number': pr.number,
            'title': pr.title,
            'body': pr.body,
            'state': pr.state,
            'url': pr.html_url,
            'user': pr.user.login,
            'head': pr.head.ref,
            'base': pr.base.ref,
            'mergeable': pr.mergeable,
            'merged': pr.merged,
            'draft': pr.draft,
            'labels': [label.name for label in pr.labels],
            'assignees': [assignee.login for assignee in pr.assignees],
            'comments': pr.comments,
            'review_comments': pr.review_comments,
            'commits': pr.commits,
            'additions': pr.additions,
            'deletions': pr.deletions,
            'changed_files': pr.changed_files,
            'created_at': pr.created_at.isoformat(),
            'updated_at': pr.updated_at.isoformat(),
            'merged_at': pr.merged_at.isoformat() if pr.merged_at else None
        }
    
    # ===== Actions / Workflows =====
    
    def list_workflow_runs(self, repo_name, status=None, max_results=30):
        """
        List GitHub Actions workflow runs.
        
        Args:
            repo_name: 'owner/repo'
            status: Filter by status ('completed', 'action_required', 'cancelled', etc.)
            max_results: Max runs to return
        """
        repo = self.gh.get_repo(repo_name)
        
        kwargs = {}
        if status:
            kwargs['status'] = status
        
        runs = repo.get_workflow_runs(**kwargs)
        return [self._format_workflow_run(run) for run in runs[:max_results]]
    
    def _format_workflow_run(self, run):
        """Format workflow run object."""
        return {
            'id': run.id,
            'name': run.name,
            'status': run.status,
            'conclusion': run.conclusion,
            'url': run.html_url,
            'event': run.event,
            'head_branch': run.head_branch,
            'head_sha': run.head_sha,
            'run_number': run.run_number,
            'created_at': run.created_at.isoformat(),
            'updated_at': run.updated_at.isoformat()
        }
    
    # ===== Utility Functions =====
    
    def search_code(self, query, max_results=30):
        """
        Search code across repositories.
        
        Examples:
            'filename:package.json'
            'language:python requests'
            'repo:owner/repo TODO'
        """
        results = self.gh.search_code(query)
        return [self._format_code_result(result) for result in results[:max_results]]
    
    def _format_code_result(self, result):
        """Format code search result."""
        return {
            'name': result.name,
            'path': result.path,
            'repo': result.repository.full_name,
            'url': result.html_url,
            'sha': result.sha
        }
    
    def get_rate_limit(self):
        """Get current API rate limit status."""
        rate_limit = self.gh.get_rate_limit()
        return {
            'core': {
                'limit': rate_limit.core.limit,
                'remaining': rate_limit.core.remaining,
                'reset': datetime.fromtimestamp(rate_limit.core.reset.timestamp()).isoformat()
            },
            'search': {
                'limit': rate_limit.search.limit,
                'remaining': rate_limit.search.remaining,
                'reset': datetime.fromtimestamp(rate_limit.search.reset.timestamp()).isoformat()
            }
        }


if __name__ == '__main__':
    # Example usage
    client = GitHubClient()
    
    # List recent repos
    repos = client.list_repos(max_results=5)
    print(f"Found {len(repos)} repositories")
    for repo in repos:
        print(f"  {repo['full_name']} - {repo['description']}")
    
    # Check rate limit
    rate_limit = client.get_rate_limit()
    print(f"\nAPI rate limit: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']} remaining")
