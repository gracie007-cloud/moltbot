#!/usr/bin/env python3
"""
Netlify deployment automation.
Requires: requests
Install: pip install requests
"""

import os
import subprocess
import json
import requests
from pathlib import Path
from typing import Optional, Dict

class NetlifyDeploy:
    
    def __init__(self, token=None):
        """
        Initialize Netlify deployment.
        
        Args:
            token: Netlify personal access token (or use NETLIFY_AUTH_TOKEN env var)
        """
        self.token = token or os.getenv('NETLIFY_AUTH_TOKEN')
        if not self.token:
            raise ValueError("Netlify token required. Set NETLIFY_AUTH_TOKEN env var or pass token.")
        
        self.api_base = 'https://api.netlify.com/api/v1'
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method, endpoint, **kwargs):
        """Make API request."""
        url = f"{self.api_base}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def list_sites(self):
        """List all Netlify sites."""
        return self._request('GET', '/sites')
    
    def get_site(self, site_id):
        """Get site details."""
        return self._request('GET', f'/sites/{site_id}')
    
    def create_site(self, name, custom_domain=None):
        """
        Create a new Netlify site.
        
        Args:
            name: Site name (will be name.netlify.app)
            custom_domain: Optional custom domain
        
        Returns:
            Site object with id, url, etc.
        """
        data = {'name': name}
        if custom_domain:
            data['custom_domain'] = custom_domain
        
        return self._request('POST', '/sites', json=data)
    
    def deploy_directory(self, site_id, directory, message='Deploy'):
        """
        Deploy a directory to Netlify site.
        
        Args:
            site_id: Netlify site ID
            directory: Path to build directory
            message: Deploy message
        
        Returns:
            Deploy object
        """
        print(f"Deploying {directory} to site {site_id}...")
        
        # Use Netlify CLI for directory deploy
        cmd = [
            'netlify', 'deploy',
            '--site', site_id,
            '--dir', directory,
            '--prod',
            '--message', message,
            '--auth', self.token
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Deploy failed: {result.stderr}")
        
        print(result.stdout)
        
        # Get deploy info
        deploys = self._request('GET', f'/sites/{site_id}/deploys')
        return deploys[0] if deploys else None
    
    def deploy_from_git(self, site_id, repo_url, branch='main', build_command='npm run build', publish_dir='dist'):
        """
        Configure continuous deployment from Git.
        
        Args:
            site_id: Netlify site ID
            repo_url: Git repository URL
            branch: Branch to deploy from
            build_command: Build command
            publish_dir: Directory to publish after build
        """
        data = {
            'repo': {
                'url': repo_url,
                'branch': branch,
                'cmd': build_command,
                'dir': publish_dir
            }
        }
        
        return self._request('PUT', f'/sites/{site_id}', json=data)
    
    def set_env_vars(self, site_id, env_vars: Dict[str, str]):
        """
        Set environment variables for build.
        
        Args:
            site_id: Netlify site ID
            env_vars: Dict of key-value pairs
        """
        for key, value in env_vars.items():
            data = {
                'key': key,
                'values': [{'value': value, 'context': 'all'}]
            }
            self._request('POST', f'/sites/{site_id}/env', json=data)
        
        print(f"Set {len(env_vars)} environment variables")
    
    def list_deploys(self, site_id, limit=10):
        """List recent deploys for a site."""
        return self._request('GET', f'/sites/{site_id}/deploys?per_page={limit}')
    
    def rollback(self, site_id, deploy_id):
        """Rollback to a previous deploy."""
        return self._request('POST', f'/sites/{site_id}/deploys/{deploy_id}/restore')
    
    def delete_site(self, site_id):
        """Delete a site."""
        return self._request('DELETE', f'/sites/{site_id}')
    
    def add_domain(self, site_id, domain):
        """Add custom domain to site."""
        return self._request('POST', f'/sites/{site_id}/domains', json={'domain': domain})
    
    def enable_ssl(self, site_id):
        """Enable SSL certificate for site."""
        return self._request('POST', f'/sites/{site_id}/ssl')
    
    # High-level workflow methods
    
    def quick_deploy(self, directory, site_name=None, site_id=None, env_vars=None):
        """
        Quick deploy workflow: create site (if needed) and deploy.
        
        Args:
            directory: Build directory to deploy
            site_name: Name for new site (if creating)
            site_id: Existing site ID (if deploying to existing)
            env_vars: Environment variables dict
        
        Returns:
            Dict with site info and deploy info
        """
        # Create site if needed
        if not site_id:
            if not site_name:
                raise ValueError("Must provide either site_id or site_name")
            
            print(f"Creating site: {site_name}")
            site = self.create_site(site_name)
            site_id = site['id']
            print(f"Created site: {site['url']}")
        else:
            site = self.get_site(site_id)
        
        # Set env vars if provided
        if env_vars:
            self.set_env_vars(site_id, env_vars)
        
        # Deploy
        deploy = self.deploy_directory(site_id, directory)
        
        return {
            'site': site,
            'deploy': deploy,
            'url': site.get('url')
        }


def install_netlify_cli():
    """Install Netlify CLI if not present."""
    try:
        subprocess.run(['netlify', '--version'], capture_output=True, check=True)
        print("Netlify CLI already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing Netlify CLI...")
        subprocess.run(['npm', 'install', '-g', 'netlify-cli'], check=True)
        print("Netlify CLI installed")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python netlify_deploy.py <site_id_or_name> <build_directory>")
        sys.exit(1)
    
    site_arg = sys.argv[1]
    directory = sys.argv[2]
    
    # Check if Netlify CLI is installed
    install_netlify_cli()
    
    # Deploy
    deployer = NetlifyDeploy()
    
    # Determine if site_arg is ID or name
    if site_arg.startswith('site-'):
        # Looks like site ID
        result = deployer.quick_deploy(directory, site_id=site_arg)
    else:
        # Treat as site name
        result = deployer.quick_deploy(directory, site_name=site_arg)
    
    print(f"\nDeployed to: {result['url']}")
