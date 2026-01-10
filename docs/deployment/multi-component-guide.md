# Multi-Component Deployment Guide

**Date:** 2026-01-10  
**Status:** Active  
**Last Updated:** 2026-01-10

## Overview

This guide covers deployment options for the AI-Agent-Framework system, including local development, Docker Compose deployment, and production configurations. The system consists of multiple containers that work together to provide a complete ISO 21500 project management solution.

## System Components

### Required Components

1. **API Server** (`api`)
   - FastAPI backend
   - Port: 8000
   - Requires: projectDocs volume

2. **Web UI** (`web`)
   - React/Vite frontend served by nginx
   - Port: 8080
   - Depends on: API server

### Optional Components

3. **TUI Client** (`tui`)
   - Terminal UI for command-line access
   - Tightly coupled to API (same repo)
   - No exposed ports (run on demand)

4. **Legacy Client** (`client`)
   - Standalone CLI API consumer
   - Demonstrates API-first design
   - No exposed ports (run on demand)

## Local Development

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Node.js 20+**
- **Git**
- **Docker 28+** (optional, for containerized development)

### Setup Without Docker

**Step 1: Setup Python Environment**

```bash
# Clone repository
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework

# Run setup script (auto-detects Python version)
./setup.sh  # Linux/macOS
# or
setup.bat   # Windows

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

**Step 2: Create Project Documents Directory**

```bash
# REQUIRED: Create projectDocs directory
mkdir -p projectDocs
```

**Step 3: Configure LLM (Optional)**

```bash
# Copy default configuration
cp configs/llm.default.json configs/llm.json

# Edit llm.json to point to your LLM endpoint
# Default: LM Studio at http://localhost:1234
```

**Step 4: Start API Server**

```bash
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

API will be available at: `http://localhost:8000`  
API documentation: `http://localhost:8000/docs`

**Step 5: Start Frontend (Optional)**

In a new terminal:

```bash
cd apps/web
npm install
npm run dev
```

Web UI will be available at: `http://localhost:5173`

### Setup With Docker

**Step 1: Prerequisites**

```bash
# Create projectDocs directory
mkdir -p projectDocs

# Optional: Copy LLM configuration
cp configs/llm.default.json configs/llm.json
```

**Step 2: Start All Services**

```bash
docker compose up --build
```

**Services:**
- API: `http://localhost:8000`
- Web UI: `http://localhost:8080`
- API Docs: `http://localhost:8000/docs`

**Step 3: Run TUI Client (Optional)**

```bash
# Interactive TUI mode
docker compose run tui python main.py tui

# Direct command execution
docker compose run tui python main.py list-projects
docker compose run tui python main.py create-project PROJECT001 "My Project"
```

**Step 4: Run CLI Client (Optional)**

```bash
# Show help
docker compose run client python -m src.client --help

# List projects
docker compose run client python -m src.client list-projects

# Create project
docker compose run client python -m src.client create-project PROJECT001 "My Project"
```

## Production Deployment

### Option 1: Docker Compose (Single Host)

**Best for:** Small to medium deployments on a single server

#### Prerequisites

- Docker 28+
- Docker Compose
- Persistent storage for projectDocs
- Domain name (optional, for HTTPS)

#### Deployment Steps

**Step 1: Prepare Server**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create project directory
mkdir -p /opt/ai-agent-framework
cd /opt/ai-agent-framework
```

**Step 2: Clone Repository**

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git .
```

**Step 3: Configure Environment**

```bash
# Create projectDocs directory on persistent storage
mkdir -p /data/projectDocs

# Create symbolic link
ln -s /data/projectDocs projectDocs

# Configure LLM endpoint
cp configs/llm.default.json configs/llm.json
nano configs/llm.json  # Edit LLM endpoint for production
```

**Step 4: Create Production Compose File**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./apps/api
      dockerfile: ../../docker/api/Dockerfile
    container_name: iso21500-api-prod
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - /data/projectDocs:/projectDocs
      - ./configs/llm.json:/config/llm.json:ro
    environment:
      - PROJECT_DOCS_PATH=/projectDocs
      - LLM_CONFIG_PATH=/config/llm.json
    networks:
      - iso21500-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  web:
    build:
      context: .
      dockerfile: docker/web/Dockerfile
    container_name: iso21500-web-prod
    restart: unless-stopped
    ports:
      - "8080:80"
    depends_on:
      - api
    networks:
      - iso21500-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  iso21500-network:
    driver: bridge
```

**Step 5: Deploy**

```bash
# Build and start services
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Verify services
curl http://localhost:8000/health
curl http://localhost:8080
```

**Step 6: Setup Reverse Proxy (Optional)**

For HTTPS access, setup nginx reverse proxy:

```nginx
# /etc/nginx/sites-available/ai-agent-framework

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Web UI
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart nginx:

```bash
sudo ln -s /etc/nginx/sites-available/ai-agent-framework /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Step 7: Setup SSL with Let's Encrypt**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

#### Maintenance

**Update Application:**

```bash
cd /opt/ai-agent-framework
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d
```

**Backup projectDocs:**

```bash
# Create backup
tar -czf projectDocs-$(date +%Y%m%d).tar.gz /data/projectDocs

# Restore backup
tar -xzf projectDocs-20260110.tar.gz -C /
```

**View Logs:**

```bash
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f web
```

### Option 2: Kubernetes Deployment

**Best for:** Large deployments, high availability, auto-scaling

#### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Persistent volume provisioner
- Ingress controller (nginx-ingress)

#### Kubernetes Manifests

**Namespace:**

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-agent-framework
```

**Persistent Volume Claim:**

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: projectdocs-pvc
  namespace: ai-agent-framework
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

**ConfigMap for LLM Configuration:**

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-config
  namespace: ai-agent-framework
data:
  llm.json: |
    {
      "provider": "lmstudio",
      "base_url": "http://lmstudio-service:1234/v1",
      "model": "local-model",
      "temperature": 0.7,
      "max_tokens": 2000
    }
```

**API Deployment:**

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ai-agent-framework
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: your-registry/ai-agent-framework-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: PROJECT_DOCS_PATH
          value: /projectDocs
        - name: LLM_CONFIG_PATH
          value: /config/llm.json
        volumeMounts:
        - name: projectdocs
          mountPath: /projectDocs
        - name: llm-config
          mountPath: /config
          readOnly: true
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: projectdocs
        persistentVolumeClaim:
          claimName: projectdocs-pvc
      - name: llm-config
        configMap:
          name: llm-config
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: ai-agent-framework
spec:
  selector:
    app: api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Web Deployment:**

```yaml
# web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: ai-agent-framework
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: your-registry/ai-agent-framework-web:latest
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: ai-agent-framework
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

**Ingress:**

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-agent-framework
  namespace: ai-agent-framework
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    secretName: ai-agent-framework-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

**Deploy to Kubernetes:**

```bash
kubectl apply -f namespace.yaml
kubectl apply -f pvc.yaml
kubectl apply -f configmap.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get all -n ai-agent-framework
kubectl logs -n ai-agent-framework -l app=api -f
```

### Option 3: Cloud Platform Deployment

#### AWS Deployment

**Architecture:**
- ECS Fargate for containers
- EFS for projectDocs storage
- ALB for load balancing
- Route 53 for DNS
- ACM for SSL certificates

**Key Services:**
1. Create EFS file system for projectDocs
2. Create ECS cluster
3. Define task definitions for API and Web
4. Create ALB with target groups
5. Configure CloudWatch for logging

#### Google Cloud Platform

**Architecture:**
- Cloud Run for containers
- Cloud Filestore for projectDocs
- Cloud Load Balancing
- Cloud DNS
- Managed SSL certificates

#### Azure Deployment

**Architecture:**
- Azure Container Instances
- Azure Files for projectDocs
- Application Gateway
- Azure DNS
- App Service Certificates

## Networking Configuration

### Docker Network

All containers communicate via Docker network:

```yaml
networks:
  iso21500-network:
    driver: bridge
```

**Internal URLs:**
- API from Web: `http://api:8000`
- API from TUI: `http://api:8000`
- API from Client: `http://api:8000`

### Port Mapping

| Service | Internal Port | External Port | Access |
|---------|--------------|---------------|---------|
| API | 8000 | 8000 | Public (dev) / Private (prod) |
| Web | 80 | 8080 | Public |
| TUI | - | - | Run on demand |
| Client | - | - | Run on demand |

### CORS Configuration

**Development:** Allow all origins

```python
allow_origins=["*"]
```

**Production:** Specific origins only

Edit `apps/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://www.your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Environment Variables

### API Server

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_DOCS_PATH` | Path to projectDocs directory | `/projectDocs` | Yes |
| `LLM_CONFIG_PATH` | Path to LLM configuration | `/config/llm.json` | No |

### Web UI

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_BASE_URL` | API server URL (for build time proxy config) | `http://api:8000` | No |

### TUI/Client

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_BASE_URL` | API server URL | `http://api:8000` | Yes |
| `API_TIMEOUT` | Request timeout (seconds) | `30` | No |

## Secrets Management

### Development

- LLM configuration in `configs/llm.json` (gitignored)
- No authentication required

### Production

**Docker Secrets:**

```yaml
secrets:
  llm_config:
    file: ./secrets/llm.json

services:
  api:
    secrets:
      - llm_config
    environment:
      - LLM_CONFIG_PATH=/run/secrets/llm_config
```

**Kubernetes Secrets:**

```bash
kubectl create secret generic llm-config \
  --from-file=llm.json=./configs/llm.json \
  -n ai-agent-framework
```

**Environment Variables:**

Use `.env` file (not committed):

```bash
# .env
API_KEY=your-api-key
LLM_ENDPOINT=https://your-llm-endpoint.com
```

## Health Checks

### API Health Endpoint

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "docs_exists": true,
  "docs_is_git": true
}
```

### Web UI Health Check

```bash
curl http://localhost:8080/
```

Should return the HTML page (status 200).

## Monitoring & Logging

### Docker Logs

```bash
# View all logs
docker compose logs -f

# View API logs only
docker compose logs -f api

# View last 100 lines
docker compose logs --tail=100 api
```

### Production Logging

**Structured Logging:**

Configure application to output JSON logs:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)
```

**Log Aggregation:**

- **ELK Stack:** Elasticsearch + Logstash + Kibana
- **Cloud Solutions:** CloudWatch (AWS), Cloud Logging (GCP), Log Analytics (Azure)
- **Third-party:** Datadog, New Relic, Splunk

### Metrics

**Recommended Metrics:**
- Request count per endpoint
- Request latency (p50, p95, p99)
- Error rate
- LLM response time
- Git operation duration
- Active projects count

**Tools:**
- Prometheus + Grafana
- Cloud monitoring services
- Application Performance Monitoring (APM) tools

## Backup & Recovery

### Backup Strategy

**What to Backup:**
1. `projectDocs/` directory (critical - all project data)
2. `configs/llm.json` (if customized)
3. Docker volumes (if using named volumes)

**Backup Script:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="projectDocs-backup-${DATE}.tar.gz"

# Create backup
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" /data/projectDocs

# Keep only last 7 days
find ${BACKUP_DIR} -name "projectDocs-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

**Automated Backups:**

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /opt/ai-agent-framework/backup.sh
```

### Recovery

**Restore from Backup:**

```bash
# Stop services
docker compose down

# Restore data
tar -xzf projectDocs-backup-20260110-020000.tar.gz -C /

# Start services
docker compose up -d

# Verify
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

**Issue:** API cannot access projectDocs

**Solution:**
```bash
# Check permissions
ls -la projectDocs/

# Fix permissions
chmod -R 755 projectDocs/
```

**Issue:** Port already in use

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

**Issue:** LLM connection fails

**Solution:**
1. Check LLM service is running
2. Verify endpoint in `configs/llm.json`
3. Test connection: `curl http://localhost:1234/v1/models`
4. System falls back to templates automatically

**Issue:** Docker build fails with SSL errors

**Solution:**

Already handled in Dockerfile with `--trusted-host` flags. If still failing:

```bash
# Build without cache
docker compose build --no-cache

# Or add to Dockerfile
ENV PIP_TRUSTED_HOST=pypi.org,pypi.python.org,files.pythonhosted.org
```

**Issue:** Web UI shows "API not available"

**Solution:**
1. Check API is running: `docker compose ps`
2. Check API health: `curl http://localhost:8000/health`
3. Check browser console for CORS errors
4. Verify nginx proxy configuration in `docker/web/nginx.conf`

## Performance Tuning

### API Server

**Increase workers:**

```yaml
# docker-compose.yml
services:
  api:
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Optimize Git operations:**

```python
# Use shallow clones for large repositories
git_manager.clone(depth=1)
```

### Database (Future Enhancement)

For high-volume deployments, consider adding PostgreSQL:

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_agent
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Security Checklist

- [ ] Change default ports in production
- [ ] Enable HTTPS with valid certificates
- [ ] Configure CORS for specific origins only
- [ ] Use Docker secrets for sensitive data
- [ ] Implement API key authentication
- [ ] Enable rate limiting
- [ ] Regular security updates for base images
- [ ] Backup projectDocs regularly
- [ ] Restrict API documentation access in production
- [ ] Enable audit logging
- [ ] Monitor for suspicious activity

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Client Integration Guide](../api/client-integration-guide.md)
- [Development Guide](../development.md)
- [ADR-0001: Separate Project Documents Repository](../adr/0001-docs-repo-mounted-git.md)

---

**Classification:** Internal  
**Retention:** Indefinite  
**Last Reviewed:** 2026-01-10
