#!/usr/bin/env python3
"""
Google Cloud Run deployment automation.
Requires: google-cloud-run, google-auth
Install: pip install google-cloud-run google-auth
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List

class CloudRunDeploy:
    
    def __init__(self, project_id=None, region='us-central1'):
        """
        Initialize Cloud Run deployment.
        
        Args:
            project_id: GCP project ID (or use GOOGLE_CLOUD_PROJECT env var)
            region: Cloud Run region
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        if not self.project_id:
            raise ValueError("GCP project ID required. Set GOOGLE_CLOUD_PROJECT env var or pass project_id.")
        
        self.region = region
    
    def _run_gcloud(self, args, capture=True):
        """Run gcloud command."""
        cmd = ['gcloud'] + args
        
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"gcloud command failed: {result.stderr}")
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True)
    
    def build_image(self, source_dir, image_name, dockerfile='Dockerfile'):
        """
        Build Docker image using Cloud Build.
        
        Args:
            source_dir: Directory containing source code
            image_name: Image name (e.g., 'my-app')
            dockerfile: Dockerfile path relative to source_dir
        
        Returns:
            Full image URL
        """
        image_url = f"gcr.io/{self.project_id}/{image_name}"
        
        print(f"Building image: {image_url}")
        
        self._run_gcloud([
            'builds', 'submit',
            '--tag', image_url,
            '--project', self.project_id,
            source_dir
        ], capture=False)
        
        print(f"Image built: {image_url}")
        return image_url
    
    def deploy_service(self, service_name, image_url, 
                      env_vars=None, port=8080, 
                      memory='512Mi', cpu='1',
                      min_instances=0, max_instances=10,
                      allow_unauthenticated=True,
                      timeout=300):
        """
        Deploy service to Cloud Run.
        
        Args:
            service_name: Cloud Run service name
            image_url: Docker image URL
            env_vars: Dict of environment variables
            port: Container port
            memory: Memory limit (e.g., '512Mi', '1Gi')
            cpu: CPU limit (e.g., '1', '2')
            min_instances: Minimum instances (0 = scale to zero)
            max_instances: Maximum instances
            allow_unauthenticated: Allow public access
            timeout: Request timeout in seconds
        
        Returns:
            Service URL
        """
        print(f"Deploying service: {service_name}")
        
        args = [
            'run', 'deploy', service_name,
            '--image', image_url,
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id,
            '--port', str(port),
            '--memory', memory,
            '--cpu', cpu,
            '--min-instances', str(min_instances),
            '--max-instances', str(max_instances),
            '--timeout', str(timeout)
        ]
        
        # Add env vars
        if env_vars:
            env_str = ','.join([f"{k}={v}" for k, v in env_vars.items()])
            args.extend(['--set-env-vars', env_str])
        
        # Allow unauthenticated access
        if allow_unauthenticated:
            args.append('--allow-unauthenticated')
        
        self._run_gcloud(args, capture=False)
        
        # Get service URL
        url = self._run_gcloud([
            'run', 'services', 'describe', service_name,
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id,
            '--format', 'value(status.url)'
        ])
        
        print(f"Service deployed: {url}")
        return url
    
    def build_and_deploy(self, source_dir, service_name, 
                        env_vars=None, **deploy_kwargs):
        """
        Build image and deploy service in one step.
        
        Args:
            source_dir: Source code directory
            service_name: Service name
            env_vars: Environment variables
            **deploy_kwargs: Additional deploy options
        
        Returns:
            Service URL
        """
        # Build image
        image_url = self.build_image(source_dir, service_name)
        
        # Deploy
        url = self.deploy_service(service_name, image_url, env_vars, **deploy_kwargs)
        
        return url
    
    def list_services(self):
        """List all Cloud Run services."""
        output = self._run_gcloud([
            'run', 'services', 'list',
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id,
            '--format', 'json'
        ])
        
        return json.loads(output) if output else []
    
    def get_service(self, service_name):
        """Get service details."""
        output = self._run_gcloud([
            'run', 'services', 'describe', service_name,
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id,
            '--format', 'json'
        ])
        
        return json.loads(output)
    
    def delete_service(self, service_name):
        """Delete a Cloud Run service."""
        self._run_gcloud([
            'run', 'services', 'delete', service_name,
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id,
            '--quiet'
        ], capture=False)
        
        print(f"Service deleted: {service_name}")
    
    def update_traffic(self, service_name, revisions):
        """
        Update traffic split between revisions.
        
        Args:
            service_name: Service name
            revisions: Dict of {revision: percentage} (e.g., {'rev1': 50, 'rev2': 50})
        """
        traffic_str = ','.join([f"{rev}={pct}" for rev, pct in revisions.items()])
        
        self._run_gcloud([
            'run', 'services', 'update-traffic', service_name,
            '--to-revisions', traffic_str,
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id
        ], capture=False)
        
        print(f"Traffic updated for {service_name}")
    
    def set_env_vars(self, service_name, env_vars: Dict[str, str]):
        """Update environment variables for existing service."""
        env_str = ','.join([f"{k}={v}" for k, v in env_vars.items()])
        
        self._run_gcloud([
            'run', 'services', 'update', service_name,
            '--set-env-vars', env_str,
            '--platform', 'managed',
            '--region', self.region,
            '--project', self.project_id
        ], capture=False)
        
        print(f"Environment variables updated for {service_name}")
    
    def get_logs(self, service_name, limit=50):
        """Get recent logs for a service."""
        return self._run_gcloud([
            'logging', 'read',
            f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"',
            '--limit', str(limit),
            '--project', self.project_id,
            '--format', 'json'
        ])
    
    def create_dockerfile(self, output_path, app_type='node'):
        """Generate a basic Dockerfile."""
        dockerfiles = {
            'node': '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8080
CMD ["node", "index.js"]
''',
            'python': '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
''',
            'go': '''FROM golang:1.21 AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
'''
        }
        
        content = dockerfiles.get(app_type)
        if not content:
            raise ValueError(f"Unknown app type: {app_type}")
        
        Path(output_path).write_text(content)
        print(f"Created Dockerfile: {output_path}")


def check_gcloud_installed():
    """Check if gcloud CLI is installed."""
    try:
        subprocess.run(['gcloud', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


if __name__ == '__main__':
    import sys
    
    if not check_gcloud_installed():
        print("Error: gcloud CLI not installed.")
        print("Install: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    
    if len(sys.argv) < 3:
        print("Usage: python cloudrun_deploy.py <service_name> <source_directory>")
        sys.exit(1)
    
    service_name = sys.argv[1]
    source_dir = sys.argv[2]
    
    deployer = CloudRunDeploy()
    url = deployer.build_and_deploy(source_dir, service_name)
    
    print(f"\nService URL: {url}")
