---
name: cloud-deployment
description: Multi-tier cloud deployment automation for Netlify (frontend), Google Cloud Run (serverless APIs), and VPS (Hostinger/any Linux VPS for databases and persistent apps). Automates builds, deployments, SSL setup, Docker Compose orchestration, and Nginx reverse proxy configuration. Use when deploying web applications, APIs, microservices, or managing infrastructure across multiple platforms for cost-optimized hosting.
---

# Cloud Deployment

Automated deployment across Netlify, Google Cloud Run, and VPS (Hostinger) with cost optimization.

## Quick Start

```python
from scripts.netlify_deploy import NetlifyDeploy
from scripts.cloudrun_deploy import CloudRunDeploy
from scripts.vps_manager import VPSManager

# Deploy frontend to Netlify
netlify = NetlifyDeploy()
netlify.quick_deploy('./dist', site_name='my-app')

# Deploy API to Cloud Run
cloudrun = CloudRunDeploy(project_id='my-project')
cloudrun.build_and_deploy('./api', 'my-api')

# Deploy database to VPS
vps = VPSManager(host='vps.example.com', key_path='~/.ssh/id_rsa')
vps.setup_postgres('mydb', 'user', 'password')
```

## Architecture Overview

```
Frontend (Netlify - Free)
    ↓
API Layer (Cloud Run - $5-10/mo)
    ↓
Database + Internal Tools (Hostinger VPS - $9/mo)
```

**Total cost: ~$10-15/mo for production-ready stack**

## Setup

### Dependencies

```bash
# Python packages
pip install requests google-cloud-run google-auth paramiko fabric

# Netlify CLI (Node.js required)
npm install -g netlify-cli

# Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install
```

### Environment Variables

```bash
# Netlify
export NETLIFY_AUTH_TOKEN="your_token"

# Google Cloud
export GOOGLE_CLOUD_PROJECT="your-project-id"
# or use: gcloud auth login

# VPS (optional, can pass directly)
export VPS_HOST="your-vps-ip"
export VPS_USER="root"
export VPS_KEY_PATH="~/.ssh/id_rsa"
```

## Netlify Deployment (Frontend)

### Quick Deploy

```python
from scripts.netlify_deploy import NetlifyDeploy

netlify = NetlifyDeploy()

# Deploy to new site
result = netlify.quick_deploy(
    directory='./build',
    site_name='my-app'
)

print(f"Deployed to: {result['url']}")
```

### Deploy to Existing Site

```python
# Using site ID
result = netlify.quick_deploy(
    directory='./dist',
    site_id='site-abc123'
)
```

### Set Environment Variables

```python
netlify.set_env_vars('site-abc123', {
    'API_URL': 'https://api.example.com',
    'PUBLIC_KEY': 'pk_...'
})
```

### Configure Git Deployment

```python
netlify.deploy_from_git(
    site_id='site-abc123',
    repo_url='https://github.com/user/repo',
    branch='main',
    build_command='npm run build',
    publish_dir='dist'
)
```

### Add Custom Domain

```python
netlify.add_domain('site-abc123', 'app.example.com')
netlify.enable_ssl('site-abc123')
```

### List Sites

```python
sites = netlify.list_sites()
for site in sites:
    print(f"{site['name']}: {site['url']}")
```

## Google Cloud Run Deployment (APIs)

### Build and Deploy

```python
from scripts.cloudrun_deploy import CloudRunDeploy

cloudrun = CloudRunDeploy(
    project_id='my-project',
    region='us-central1'
)

# Build image and deploy service
url = cloudrun.build_and_deploy(
    source_dir='./api',
    service_name='my-api',
    env_vars={
        'DATABASE_URL': 'postgresql://...',
        'API_KEY': 'secret'
    }
)

print(f"API deployed: {url}")
```

### Custom Configuration

```python
url = cloudrun.deploy_service(
    service_name='my-api',
    image_url='gcr.io/project/my-api',
    memory='1Gi',
    cpu='2',
    min_instances=0,  # Scale to zero
    max_instances=10,
    allow_unauthenticated=True,
    timeout=300
)
```

### Separate Build and Deploy

```python
# Build image
image_url = cloudrun.build_image('./api', 'my-api')

# Deploy later
url = cloudrun.deploy_service('my-api', image_url)
```

### List Services

```python
services = cloudrun.list_services()
for service in services:
    print(f"{service['metadata']['name']}: {service['status']['url']}")
```

### Update Environment Variables

```python
cloudrun.set_env_vars('my-api', {
    'NEW_VAR': 'value'
})
```

### Generate Dockerfile

```python
# Create Dockerfile for Node.js app
cloudrun.create_dockerfile('./api/Dockerfile', app_type='node')

# For Python
cloudrun.create_dockerfile('./api/Dockerfile', app_type='python')

# For Go
cloudrun.create_dockerfile('./api/Dockerfile', app_type='go')
```

## VPS Management (Hostinger)

### Initial Setup

```python
from scripts.vps_manager import VPSManager

vps = VPSManager(
    host='123.456.789.0',
    user='root',
    key_path='~/.ssh/id_rsa'
)

# Complete initial setup
vps.initial_setup(domain='api.example.com')
```

This installs:

- Docker & Docker Compose
- Nginx
- Certbot (SSL)
- Firewall configuration

### Deploy PostgreSQL

```python
vps.setup_postgres(
    db_name='myapp',
    db_user='dbuser',
    db_password='secure_password',
    port=5432
)
```

### Deploy Docker Compose App

```python
vps.deploy_compose(
    local_compose_file='./docker-compose.yml',
    app_name='my-app',
    env_vars={
        'DB_PASSWORD': 'secret',
        'API_KEY': 'key'
    }
)
```

### Configure Nginx Reverse Proxy

```python
vps.configure_nginx_proxy(
    domain='app.example.com',
    app_name='my-app',
    port=8080
)
```

### Setup SSL Certificate

```python
vps.setup_ssl(
    domain='app.example.com',
    email='admin@example.com'
)
```

### Update Running App

```python
# Pull new images and restart
vps.update_compose_app('my-app')
```

### View Logs

```python
vps.logs_compose_app('my-app', tail=100)

# Follow logs
vps.logs_compose_app('my-app', follow=True)
```

### List Apps

```python
apps = vps.list_apps()
print("Deployed apps:", apps)
```

### System Information

```python
info = vps.get_system_info()
print(info['disk'])      # Disk usage
print(info['memory'])    # RAM usage
print(info['containers']) # Running containers
```

### Stop/Remove App

```python
# Stop app
vps.stop_compose_app('my-app')

# Remove completely (including volumes)
vps.remove_compose_app('my-app')
```

## Complete Deployment Workflows

### Full-Stack App Deployment

```python
# 1. Deploy frontend to Netlify
netlify = NetlifyDeploy()
frontend_url = netlify.quick_deploy('./frontend/dist', site_name='myapp')['url']

# 2. Deploy API to Cloud Run
cloudrun = CloudRunDeploy(project_id='my-project')
api_url = cloudrun.build_and_deploy('./backend', 'myapp-api')

# 3. Setup database on VPS
vps = VPSManager(host='vps.example.com', key_path='~/.ssh/id_rsa')
vps.setup_postgres('myapp', 'dbuser', 'dbpass')

# 4. Update frontend with API URL
netlify.set_env_vars(site_id, {'API_URL': api_url})

print(f"Frontend: {frontend_url}")
print(f"API: {api_url}")
```

### Deploy Internal Admin Panel to VPS

```python
vps = VPSManager(host='vps.example.com', key_path='~/.ssh/id_rsa')

# Deploy with Docker Compose
vps.deploy_compose(
    local_compose_file='./admin/docker-compose.yml',
    app_name='admin-panel',
    env_vars={
        'DATABASE_URL': 'postgresql://dbuser:dbpass@localhost:5432/myapp',
        'SESSION_SECRET': 'random_secret'
    }
)

# Setup Nginx proxy
vps.configure_nginx_proxy(
    domain='admin.example.com',
    app_name='admin-panel',
    port=3000
)

# Enable SSL
vps.setup_ssl('admin.example.com')
```

### Multi-Service VPS Deployment

```python
vps = VPSManager(host='vps.example.com', key_path='~/.ssh/id_rsa')

# Deploy multiple services
services = [
    {'name': 'postgres', 'compose': './compose/postgres.yml', 'port': None},
    {'name': 'redis', 'compose': './compose/redis.yml', 'port': None},
    {'name': 'admin', 'compose': './compose/admin.yml', 'port': 3000},
    {'name': 'worker', 'compose': './compose/worker.yml', 'port': None}
]

for service in services:
    vps.deploy_compose(service['compose'], service['name'])

    if service['port']:
        vps.configure_nginx_proxy(
            domain=f"{service['name']}.example.com",
            app_name=service['name'],
            port=service['port']
        )
```

## Docker Compose Templates

See [assets/docker-compose-fullstack.yml](assets/docker-compose-fullstack.yml) for a complete example including:

- PostgreSQL database
- Redis cache
- Backend API
- Admin panel

Usage:

```python
vps.deploy_compose(
    'assets/docker-compose-fullstack.yml',
    'myapp',
    env_vars={
        'DB_NAME': 'myapp',
        'DB_USER': 'user',
        'DB_PASSWORD': 'pass',
        'BACKEND_IMAGE': 'gcr.io/project/backend:latest',
        'ADMIN_IMAGE': 'gcr.io/project/admin:latest',
        'BACKEND_PORT': '8080',
        'ADMIN_PORT': '3000'
    }
)
```

## Cost Optimization Tips

1. **Use Cloud Run for APIs with variable traffic**
   - Scales to zero when not in use
   - Only pay for actual usage

2. **Run databases on VPS**
   - Managed databases cost $15-50/mo
   - VPS can run PostgreSQL for $9/mo

3. **Host internal tools on VPS**
   - No need for Cloud Run if traffic is predictable
   - Run 5-10 small apps on one VPS

4. **Use Netlify for static frontends**
   - Free tier is generous
   - Excellent CDN performance

5. **Share resources on VPS**
   - One PostgreSQL instance for multiple apps
   - One Redis for multiple services
   - Single Nginx for all reverse proxying

## Platform Decision Matrix

| Use Case                    | Platform         | Why                    |
| --------------------------- | ---------------- | ---------------------- |
| Marketing website           | Netlify          | Free, fast CDN         |
| React/Vue SaaS frontend     | Netlify          | Auto-deploy, previews  |
| REST API (variable traffic) | Cloud Run        | Pay-per-use            |
| WebSocket server            | VPS              | Persistent connections |
| PostgreSQL database         | VPS              | Much cheaper           |
| Background jobs             | Cloud Run or VPS | Both work well         |
| Internal admin panel        | VPS              | Always-on, low traffic |
| Microservices (high scale)  | Cloud Run        | Auto-scaling           |
| Microservices (low scale)   | VPS              | Cost-effective         |

## Monitoring & Maintenance

### Health Checks

```python
# Check VPS system status
info = vps.get_system_info()

# Check running containers
apps = vps.list_apps()

# View logs
vps.logs_compose_app('myapp', tail=100)
```

### Automated Backups

```python
# Backup PostgreSQL database
vps.run('docker exec postgres-main pg_dump -U user dbname > /backups/db.sql', sudo=True)

# Download backup
vps.conn.get('/backups/db.sql', './db-backup.sql')
```

### SSL Renewal

Certbot automatically renews certificates. Verify:

```python
vps.run('certbot renew --dry-run', sudo=True)
```

## Troubleshooting

### Netlify

**Build fails:**

- Check build command in site settings
- Verify environment variables are set
- Check build logs in Netlify dashboard

**Site not updating:**

- Trigger manual deploy
- Check Git branch is correct
- Verify auto-publish is enabled

### Cloud Run

**Service won't start:**

- Check logs: `cloudrun.get_logs('service-name')`
- Verify Dockerfile exposes correct port (8080)
- Check environment variables

**Timeout errors:**

- Increase timeout: `timeout=600`
- Check service health endpoint

### VPS

**Container won't start:**

- Check logs: `vps.logs_compose_app('app-name')`
- Verify ports aren't in use
- Check environment variables in .env

**Nginx 502 error:**

- Verify backend is running
- Check port configuration
- Test with `curl localhost:PORT` on VPS

**SSL issues:**

- Verify domain DNS points to VPS
- Check firewall allows port 80/443
- Re-run: `vps.setup_ssl('domain.com')`

## Security Best Practices

1. **Use SSH keys, not passwords** for VPS access
2. **Set strong passwords** for databases
3. **Use environment variables** for secrets
4. **Enable firewall** on VPS (done in initial_setup)
5. **Keep systems updated**: `vps.run('apt-get update && apt-get upgrade -y', sudo=True)`
6. **Use SSL/HTTPS** everywhere
7. **Restrict database access** to localhost or VPN
8. **Regular backups** of databases and configs

## Dependencies

```bash
pip install requests google-cloud-run google-auth paramiko fabric
npm install -g netlify-cli
# Install gcloud CLI from: https://cloud.google.com/sdk/docs/install
```

## Additional Resources

- Netlify CLI docs: https://docs.netlify.com/cli/get-started/
- Cloud Run docs: https://cloud.google.com/run/docs
- Docker Compose: https://docs.docker.com/compose/
- Nginx reverse proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
