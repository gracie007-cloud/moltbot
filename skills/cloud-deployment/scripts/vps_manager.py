#!/usr/bin/env python3
"""
VPS management and deployment (Hostinger/any VPS).
Requires: paramiko, fabric
Install: pip install paramiko fabric
"""

import os
import subprocess
from pathlib import Path
from fabric import Connection
from invoke import run as local_run
from typing import Dict, List, Optional

class VPSManager:
    
    def __init__(self, host, user='root', key_path=None, password=None):
        """
        Initialize VPS connection.
        
        Args:
            host: VPS IP or hostname
            user: SSH user
            key_path: Path to SSH private key
            password: SSH password (if not using key)
        """
        self.host = host
        self.user = user
        
        connect_kwargs = {}
        if key_path:
            connect_kwargs['key_filename'] = key_path
        elif password:
            connect_kwargs['password'] = password
        else:
            raise ValueError("Must provide either key_path or password")
        
        self.conn = Connection(host=host, user=user, connect_kwargs=connect_kwargs)
    
    def run(self, command, sudo=False):
        """Run command on VPS."""
        if sudo:
            return self.conn.sudo(command, hide=False)
        return self.conn.run(command, hide=False)
    
    # ===== Initial Setup =====
    
    def initial_setup(self, domain=None):
        """
        Perform initial VPS setup.
        
        - Update system
        - Install Docker & Docker Compose
        - Install Nginx
        - Setup firewall
        - Create app directory
        """
        print("Starting initial VPS setup...")
        
        # Update system
        print("Updating system...")
        self.run('apt-get update', sudo=True)
        self.run('apt-get upgrade -y', sudo=True)
        
        # Install Docker
        print("Installing Docker...")
        self.run('apt-get install -y apt-transport-https ca-certificates curl software-properties-common', sudo=True)
        self.run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -', sudo=True)
        self.run('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"', sudo=True)
        self.run('apt-get update', sudo=True)
        self.run('apt-get install -y docker-ce docker-ce-cli containerd.io', sudo=True)
        
        # Install Docker Compose
        print("Installing Docker Compose...")
        self.run('curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose', sudo=True)
        self.run('chmod +x /usr/local/bin/docker-compose', sudo=True)
        
        # Install Nginx
        print("Installing Nginx...")
        self.run('apt-get install -y nginx', sudo=True)
        self.run('systemctl enable nginx', sudo=True)
        
        # Install Certbot for SSL
        print("Installing Certbot...")
        self.run('apt-get install -y certbot python3-certbot-nginx', sudo=True)
        
        # Setup firewall
        print("Configuring firewall...")
        self.run('ufw allow 22/tcp', sudo=True)  # SSH
        self.run('ufw allow 80/tcp', sudo=True)  # HTTP
        self.run('ufw allow 443/tcp', sudo=True)  # HTTPS
        self.run('ufw --force enable', sudo=True)
        
        # Create app directory
        self.run('mkdir -p /var/www/apps', sudo=True)
        self.run(f'chown {self.user}:{self.user} /var/www/apps', sudo=True)
        
        print("Initial setup complete!")
        
        # Setup SSL if domain provided
        if domain:
            self.setup_ssl(domain)
    
    def setup_ssl(self, domain, email=None):
        """Setup Let's Encrypt SSL certificate."""
        print(f"Setting up SSL for {domain}...")
        
        email_arg = f'--email {email}' if email else '--register-unsafely-without-email'
        
        self.run(f'certbot --nginx -d {domain} {email_arg} --non-interactive --agree-tos', sudo=True)
        
        # Setup auto-renewal
        self.run('systemctl enable certbot.timer', sudo=True)
        
        print(f"SSL certificate installed for {domain}")
    
    # ===== Docker Compose Management =====
    
    def deploy_compose(self, local_compose_file, app_name, env_vars=None):
        """
        Deploy Docker Compose application.
        
        Args:
            local_compose_file: Path to local docker-compose.yml
            app_name: Application name
            env_vars: Dict of environment variables
        
        Returns:
            App directory path on VPS
        """
        app_dir = f"/var/www/apps/{app_name}"
        
        print(f"Deploying {app_name} to VPS...")
        
        # Create app directory
        self.run(f'mkdir -p {app_dir}')
        
        # Upload docker-compose.yml
        self.conn.put(local_compose_file, f'{app_dir}/docker-compose.yml')
        
        # Create .env file if env_vars provided
        if env_vars:
            env_content = '\n'.join([f'{k}={v}' for k, v in env_vars.items()])
            self.run(f"echo '{env_content}' > {app_dir}/.env")
        
        # Pull and start containers
        with self.conn.cd(app_dir):
            self.run('docker-compose pull', sudo=True)
            self.run('docker-compose up -d', sudo=True)
        
        print(f"{app_name} deployed successfully")
        return app_dir
    
    def update_compose_app(self, app_name):
        """Update running Docker Compose app (pull new images, restart)."""
        app_dir = f"/var/www/apps/{app_name}"
        
        print(f"Updating {app_name}...")
        
        with self.conn.cd(app_dir):
            self.run('docker-compose pull', sudo=True)
            self.run('docker-compose up -d', sudo=True)
        
        print(f"{app_name} updated")
    
    def stop_compose_app(self, app_name):
        """Stop Docker Compose app."""
        app_dir = f"/var/www/apps/{app_name}"
        
        with self.conn.cd(app_dir):
            self.run('docker-compose down', sudo=True)
        
        print(f"{app_name} stopped")
    
    def remove_compose_app(self, app_name):
        """Remove Docker Compose app completely."""
        app_dir = f"/var/www/apps/{app_name}"
        
        with self.conn.cd(app_dir):
            self.run('docker-compose down -v', sudo=True)
        
        self.run(f'rm -rf {app_dir}', sudo=True)
        print(f"{app_name} removed")
    
    def logs_compose_app(self, app_name, tail=50, follow=False):
        """View logs for Docker Compose app."""
        app_dir = f"/var/www/apps/{app_name}"
        
        follow_flag = '-f' if follow else ''
        
        with self.conn.cd(app_dir):
            self.run(f'docker-compose logs {follow_flag} --tail={tail}', sudo=True)
    
    # ===== Nginx Configuration =====
    
    def configure_nginx_proxy(self, domain, app_name, port):
        """
        Configure Nginx reverse proxy for app.
        
        Args:
            domain: Domain name
            app_name: App name (for config file naming)
            port: Internal port the app runs on
        """
        nginx_config = f'''server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass http://localhost:{port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}'''
        
        config_path = f'/etc/nginx/sites-available/{app_name}'
        
        # Upload config
        self.run(f"echo '{nginx_config}' | sudo tee {config_path}")
        
        # Enable site
        self.run(f'ln -sf {config_path} /etc/nginx/sites-enabled/{app_name}', sudo=True)
        
        # Test and reload
        self.run('nginx -t', sudo=True)
        self.run('systemctl reload nginx', sudo=True)
        
        print(f"Nginx configured for {domain} -> port {port}")
    
    # ===== System Info =====
    
    def get_system_info(self):
        """Get system information."""
        info = {}
        
        # Disk usage
        result = self.run('df -h /')
        info['disk'] = result.stdout
        
        # Memory
        result = self.run('free -h')
        info['memory'] = result.stdout
        
        # Docker containers
        result = self.run('docker ps', sudo=True)
        info['containers'] = result.stdout
        
        # Docker images
        result = self.run('docker images', sudo=True)
        info['images'] = result.stdout
        
        return info
    
    def list_apps(self):
        """List deployed apps."""
        result = self.run('ls -1 /var/www/apps')
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    # ===== Database Setup =====
    
    def setup_postgres(self, db_name, db_user, db_password, port=5432):
        """Setup PostgreSQL container."""
        compose_content = f'''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres-main
    restart: always
    environment:
      POSTGRES_DB: {db_name}
      POSTGRES_USER: {db_user}
      POSTGRES_PASSWORD: {db_password}
    ports:
      - "{port}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
        
        return self.deploy_compose_from_string(compose_content, 'postgres')
    
    def deploy_compose_from_string(self, compose_content, app_name):
        """Deploy from compose content string."""
        app_dir = f"/var/www/apps/{app_name}"
        
        self.run(f'mkdir -p {app_dir}')
        self.run(f"echo '{compose_content}' > {app_dir}/docker-compose.yml")
        
        with self.conn.cd(app_dir):
            self.run('docker-compose up -d', sudo=True)
        
        print(f"{app_name} deployed")
        return app_dir


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python vps_manager.py <host> <command>")
        print("Commands: setup, info, list-apps")
        sys.exit(1)
    
    host = sys.argv[1]
    command = sys.argv[2]
    
    # Try to use SSH key from default location
    key_path = os.path.expanduser('~/.ssh/id_rsa')
    if not os.path.exists(key_path):
        key_path = None
        password = input("SSH password: ")
    else:
        password = None
    
    vps = VPSManager(host, key_path=key_path, password=password)
    
    if command == 'setup':
        domain = sys.argv[3] if len(sys.argv) > 3 else None
        vps.initial_setup(domain=domain)
    
    elif command == 'info':
        info = vps.get_system_info()
        for key, value in info.items():
            print(f"\n=== {key.upper()} ===")
            print(value)
    
    elif command == 'list-apps':
        apps = vps.list_apps()
        print("Deployed apps:")
        for app in apps:
            print(f"  - {app}")
