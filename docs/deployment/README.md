# Deployment Guide

**AI-Agent-Framework - ISO 21500 Project Management System**

This guide covers various deployment scenarios from single-machine Docker setups to multi-component production deployments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Single-Machine Deployment](#single-machine-deployment)
3. [Multi-Component Deployment](#multi-component-deployment)
4. [Development Setup](#development-setup)
5. [Production Considerations](#production-considerations)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Docker**: Version 28+ (for containerized deployments)
- **Docker Compose**: Version 3.8+
- **Git**: Version 2.x
- **Disk Space**: Minimum 500MB for containers + space for project documents

### Optional

For local development:
- **Python**: 3.10 or higher (3.12 recommended)
- **Node.js**: 20+
- **npm**: 10+

---

## Single-Machine Deployment

### Option 1: Full Docker Compose (Recommended)

**Best for:** Quick start, production-like environment, team deployments

#### Step 1: Clone Repository

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

#### Step 2: Create Project Documents Directory

```bash
mkdir -p projectDocs
```

**Important:** This directory MUST exist before starting Docker. It will be mounted as a volume and initialized as a Git repository automatically.

#### Step 3: Configure LLM (Optional)

```bash
# Copy default configuration
cp configs/llm.default.json configs/llm.json

# Edit if needed
nano configs/llm.json
```

**Configuration example:**
```json
{
  "provider": "lm_studio",
  "base_url": "http://host.docker.internal:1234/v1",
  "model": "local-model",
  "api_key": "not-needed",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

**Note:** Use `host.docker.internal` to access services running on the host machine from within Docker containers.

#### Step 4: Build and Start Services

```bash
docker compose up --build
```

**First-time build:** Takes 2-3 minutes to download images and build containers.

**Subsequent starts:**
```bash
docker compose up
```

#### Step 5: Access the Application

- **Web UI:** http://localhost:8080
- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc

#### Step 6: Test with TUI (Optional)

```bash
# Show help
docker compose run tui --help

# Check health
docker compose run tui health

# Create a project
docker compose run tui projects create --key TEST001 --name "Test Project"

# List projects
docker compose run tui projects list
```

### Option 2: API and Web Only

If you don't need the TUI client:

```bash
# Start only API and Web services
docker compose up api web
```

This reduces resource usage and startup time.

---

## Multi-Component Deployment

Deploy components separately for scalability and flexibility.

### Component 1: API Service

#### Docker Deployment

**Dockerfile:** `docker/api/Dockerfile`

```bash
# Build API image
docker build -f docker/api/Dockerfile -t iso21500-api:latest apps/api

# Run API container
docker run -d \
  --name iso21500-api \
  -p 8000:8000 \
  -v $(pwd)/projectDocs:/projectDocs \
  -v $(pwd)/configs/llm.json:/config/llm.json:ro \
  -e PROJECT_DOCS_PATH=/projectDocs \
  -e LLM_CONFIG_PATH=/config/llm.json \
  iso21500-api:latest
```

#### Manual Deployment

```bash
cd apps/api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROJECT_DOCS_PATH=/path/to/projectDocs
export LLM_CONFIG_PATH=/path/to/llm.json

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Systemd service example:**

Create `/etc/systemd/system/iso21500-api.service`:

```ini
[Unit]
Description=ISO 21500 API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/AI-Agent-Framework/apps/api
Environment="PROJECT_DOCS_PATH=/var/lib/iso21500/projectDocs"
Environment="LLM_CONFIG_PATH=/etc/iso21500/llm.json"
ExecStart=/opt/AI-Agent-Framework/apps/api/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable iso21500-api
sudo systemctl start iso21500-api
```

### Component 2: Web UI

#### Option A: Static Hosting (nginx, Vercel, Netlify)

**Build static files:**

```bash
cd apps/web
npm install
npm run build
```

**Output:** `apps/web/dist/` directory with static files

**nginx configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Serve React app
    root /var/www/iso21500/dist;
    index index.html;
    
    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API requests
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/javascript application/javascript application/json;
}
```

**Vercel deployment:**

Create `vercel.json` in `apps/web/`:
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://your-api-domain.com/$1" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Deploy:
```bash
cd apps/web
vercel deploy --prod
```

**Netlify deployment:**

Create `netlify.toml` in `apps/web/`:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://your-api-domain.com/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### Option B: Docker Deployment

```bash
# Build web image
docker build -f docker/web/Dockerfile -t iso21500-web:latest .

# Run web container
docker run -d \
  --name iso21500-web \
  -p 8080:80 \
  iso21500-web:latest
```

### Component 3: TUI Client

#### As Cron Job

Run automated tasks on a schedule:

```bash
# Add to crontab
crontab -e

# Example: Generate gap assessments daily at 2 AM
0 2 * * * docker compose run --rm tui commands propose --project PROJ001 --command assess_gaps

# Example: Generate weekly reports every Monday at 9 AM
0 9 * * 1 docker compose run --rm tui commands propose --project PROJ001 --command generate_artifact --artifact-name weekly_report.md --artifact-type status_report
```

#### As CLI Tool

Install globally for command-line use:

```bash
cd apps/tui

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export API_BASE_URL=https://your-api-domain.com

# Use from anywhere
alias iso21500-tui="cd /path/to/apps/tui && source .venv/bin/activate && python main.py"

# Run commands
iso21500-tui projects list
iso21500-tui health
```

---

## Development Setup

### Option 1: Local API + Local TUI

**Terminal 1: API**
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p ../../projectDocs
export PROJECT_DOCS_PATH=../../projectDocs
uvicorn main:app --reload
```

**Terminal 2: TUI**
```bash
cd apps/tui
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export API_BASE_URL=http://localhost:8000
python main.py health
```

### Option 2: Local API + Local Web

**Terminal 1: API**
```bash
cd apps/api
source .venv/bin/activate
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

**Terminal 2: Web**
```bash
cd apps/web
npm install
npm run dev
```

**Access:**
- Web UI: http://localhost:5173 (Vite dev server)
- API: http://localhost:8000

### Option 3: Docker API + Local Clients

**Terminal 1: Start API in Docker**
```bash
docker compose up api
```

**Terminal 2: Run Web locally**
```bash
cd apps/web
export API_BASE_URL=http://localhost:8000
npm run dev
```

**Terminal 3: Run TUI locally**
```bash
cd apps/tui
source .venv/bin/activate
export API_BASE_URL=http://localhost:8000
python main.py projects list
```

### Option 4: Full Docker Stack

```bash
# Build and start all services
docker compose up --build

# Access via browser
open http://localhost:8080

# Use TUI
docker compose run tui projects list
```

---

## Production Considerations

### Secrets Management

**Never commit secrets to the repository!**

#### Environment Variables

Use environment variables for sensitive data:

```bash
# .env file (DO NOT COMMIT)
API_KEY=your-secret-api-key
LLM_API_KEY=your-llm-key
DATABASE_URL=postgresql://user:pass@host/db
```

Load in Docker Compose:
```yaml
services:
  api:
    env_file:
      - .env
```

#### Docker Secrets

For Docker Swarm:

```yaml
services:
  api:
    secrets:
      - llm_api_key
      
secrets:
  llm_api_key:
    external: true
```

Create secret:
```bash
echo "your-api-key" | docker secret create llm_api_key -
```

#### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: iso21500-secrets
type: Opaque
data:
  llm-api-key: <base64-encoded-key>
```

### API Authentication

#### Option 1: API Key Authentication

Add middleware in `apps/api/main.py`:

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Add to endpoints
@app.get("/projects", dependencies=[Depends(verify_api_key)])
async def list_projects():
    ...
```

#### Option 2: OAuth2 / JWT

Use FastAPI's OAuth2 support:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate credentials and return JWT
    ...

@app.get("/projects")
async def list_projects(token: str = Depends(oauth2_scheme)):
    # Validate JWT token
    ...
```

### CORS Configuration

**Development (permissive):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production (restrictive):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://app.your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)
```

### Reverse Proxy Setup

#### nginx

```nginx
upstream api_backend {
    server api:8000;
    # Add more servers for load balancing
    # server api2:8000;
    # server api3:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Web UI
    location / {
        root /var/www/iso21500;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

#### Traefik

`docker-compose.yml`:
```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
  
  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.your-domain.com`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=myresolver"
      
  web:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.web.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.web.entrypoints=websecure"
      - "traefik.http.routers.web.tls.certresolver=myresolver"
```

### Scaling Strategies

#### Horizontal Scaling (Multiple API Instances)

```yaml
services:
  api:
    deploy:
      replicas: 3
    # Shared volume for projectDocs
    volumes:
      - projectdocs:/projectDocs
      
volumes:
  projectdocs:
    driver: local
```

**Note:** Git operations require locking. Consider using a distributed lock or dedicated git service for high-concurrency scenarios.

#### Vertical Scaling (Resource Limits)

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Monitoring and Logging

#### Health Checks

Docker Compose:
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### Logging

Centralized logging with Docker:
```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Or use external logging service:
```yaml
services:
  api:
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://logs.example.com:514"
```

### Backup Strategy

#### Project Documents

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backups/iso21500"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf "$BACKUP_DIR/projectDocs_$DATE.tar.gz" projectDocs/

# Keep only last 30 days
find "$BACKUP_DIR" -name "projectDocs_*.tar.gz" -mtime +30 -delete
```

Run via cron:
```bash
# Daily backup at midnight
0 0 * * * /opt/scripts/backup-iso21500.sh
```

#### Database Backup (if added in future)

```bash
docker compose exec api pg_dump -U postgres iso21500 > backup.sql
```

---

## Environment Configuration

### API Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_DOCS_PATH` | Path to project documents directory | `/projectDocs` | Yes |
| `LLM_CONFIG_PATH` | Path to LLM configuration JSON | `/config/llm.json` | No |
| `API_KEY` | API authentication key | _(none)_ | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |

### TUI Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_BASE_URL` | API endpoint URL | `http://localhost:8000` | Yes |
| `API_TIMEOUT` | Request timeout (seconds) | `30` | No |
| `API_KEY` | API authentication key | _(none)_ | No |

### Web Environment Variables

Set at build time in `.env`:

```env
VITE_API_URL=https://api.your-domain.com
```

---

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails

**Error:** `npm error Exit handler never called`

**Solution:** This is a harmless warning in the web build. Ignore it.

---

**Error:** SSL verification failed during pip install

**Solution:** Dockerfile includes `--trusted-host` flags. Try:
```bash
docker compose build --no-cache
```

---

#### 2. projectDocs Permission Issues

**Error:** Permission denied accessing `/projectDocs`

**Solution:**
```bash
# Set permissions
chmod -R 777 projectDocs/

# Or use proper user/group
sudo chown -R 1000:1000 projectDocs/
```

---

#### 3. Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find process using port
lsof -i :8000
# Or on Linux
netstat -tulpn | grep 8000

# Kill process or change port in docker-compose.yml
```

---

#### 4. LLM Connection Failed

**Error:** `Connection refused to LLM service`

**Solution:**
- Verify LLM service is running
- Use `host.docker.internal` for host services
- Check firewall settings
- System falls back to templates automatically

---

#### 5. Git Operations Fail

**Error:** `Git config user.email not set`

**Solution:**
```bash
# Configure git in container
docker compose exec api git config --global user.email "api@example.com"
docker compose exec api git config --global user.name "ISO21500 API"
```

---

### Debug Mode

Enable debug logging:

```bash
# API
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug

# Docker
docker compose up api --env LOG_LEVEL=DEBUG
```

### Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Check API documentation
curl http://localhost:8000/docs

# Test TUI
docker compose run tui health

# Test project creation
docker compose run tui projects create --key TEST --name "Test Project"
```

---

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Quick Start Guide](../../QUICKSTART.md)
- [Development Guide](../development.md)
- [Client Integration Guide](../api/client-integration.md)

---

**Last Updated:** 2026-01-10  
**Version:** 1.0.0  
**Status:** Active
