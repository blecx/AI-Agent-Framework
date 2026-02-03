# Tutorial Setup Guide

This guide helps you prepare your environment for the ISO 21500 AI-Agent Framework tutorials.

## 📋 Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker** | 28.0+ | Container runtime |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | 2.23+ | Version control |
| **Web Browser** | Modern | GUI access (Chrome/Firefox/Safari) |
| **Terminal** | Any | Command execution (bash/zsh/PowerShell) |

### Optional Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.10+ | Local TUI usage (without Docker) |
| **Node.js** | 20+ | Frontend development |
| **curl** | Any | API health checks |
| **jq** | Any | JSON parsing |

### Hardware Requirements

- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 10GB free space
- **Network**: Internet connection for Docker images

## 🐳 Docker Installation

### Linux (Ubuntu/Debian)

**Step 1: Remove old versions**

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

**Step 2: Install dependencies**

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
```

**Step 3: Add Docker's official GPG key**

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

**Step 4: Set up repository**

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**Step 5: Install Docker Engine**

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**Step 6: Verify installation**

```bash
sudo docker --version
# Expected: Docker version 28.0.0 or higher

sudo docker compose version
# Expected: Docker Compose version v2.0.0 or higher
```

**Step 7: Add user to docker group (optional, avoids sudo)**

```bash
sudo usermod -aG docker $USER
newgrp docker  # Activate group without logout
```

**Troubleshooting**: If `newgrp` doesn't work, log out and log back in.

### macOS

**Option 1: Docker Desktop (Recommended)**

1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
2. Open downloaded `.dmg` file
3. Drag Docker.app to Applications folder
4. Launch Docker Desktop from Applications
5. Wait for Docker to start (whale icon in menu bar)

**Option 2: Homebrew**

```bash
brew install --cask docker
open /Applications/Docker.app
```

**Verify installation:**

```bash
docker --version
# Expected: Docker version 28.0.0 or higher

docker compose version
# Expected: Docker Compose version v2.0.0 or higher
```

### Windows

**Option 1: Docker Desktop (Recommended)**

1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Run installer `.exe` file
3. Follow installation wizard
4. Restart computer when prompted
5. Launch Docker Desktop
6. Wait for Docker to start (whale icon in system tray)

**Requirements:**
- Windows 10/11 Pro, Enterprise, or Education (for Hyper-V)
- OR Windows 10/11 Home with WSL 2

**Option 2: WSL 2 Backend (Windows Home)**

1. Enable WSL 2:
   ```powershell
   wsl --install
   ```
2. Install Docker Desktop
3. In Docker Desktop settings, enable "Use WSL 2 based engine"
4. Select Ubuntu distro in WSL Integration

**Verify installation (PowerShell or WSL):**

```powershell
docker --version
# Expected: Docker version 28.0.0 or higher

docker compose version
# Expected: Docker Compose version v2.0.0 or higher
```

## 📦 Repository Setup

### Clone Repository

```bash
# HTTPS (recommended)
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework

# SSH (if configured)
git clone git@github.com:blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

### Verify Repository Structure

```bash
ls -la
# Expected directories:
# apps/api/       - Backend API
# apps/web/       - Frontend web UI
# apps/tui/       - Terminal UI
# docker/         - Dockerfiles
# docs/           - Documentation
# projectDocs/    - Project storage (empty initially)
# templates/      - Prompt templates
```

## 🚀 Start Services

### Using Docker Compose (Recommended)

**Step 1: Create projectDocs directory**

```bash
mkdir -p projectDocs
```

**Step 2: Start all services**

```bash
docker compose up -d
```

**Expected output:**

```
[+] Running 3/3
 ✔ Network ai-agent-framework_default  Created
 ✔ Container ai-agent-framework-api-1  Started
 ✔ Container ai-agent-framework-web-1  Started
```

**Step 3: Check service status**

```bash
docker compose ps
```

**Expected output:**

```
NAME                           STATUS   PORTS
ai-agent-framework-api-1       Up       0.0.0.0:8000->8000/tcp
ai-agent-framework-web-1       Up       0.0.0.0:8080->80/tcp
```

**Troubleshooting**: See [Common Issues](#-common-issues) below if services don't start.

## ✅ Verification

### Check Docker

```bash
docker --version
# Expected: Docker version 28.0.0, build XXXXX

docker compose version
# Expected: Docker Compose version v2.0.0
```

### Check Services Running

```bash
docker compose ps
# Both api-1 and web-1 should show "Up" status
```

### Check API Health

**Using curl:**

```bash
curl http://localhost:8000/health
```

**Expected response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "docs_path": "/app/projectDocs",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Troubleshooting**: If connection refused:
1. Wait 10 seconds for services to initialize
2. Check logs: `docker compose logs api`
3. Verify port 8000 not in use: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)

### Check Web UI

**Open browser:**

```bash
# macOS
open http://localhost:8080

# Linux
xdg-open http://localhost:8080

# Windows
start http://localhost:8080

# Or manually open: http://localhost:8080
```

**Expected result:**
- Page loads with "ISO 21500 AI-Agent Framework" title
- Project selector dropdown visible
- No console errors in browser dev tools (F12)

**Troubleshooting**: If page doesn't load:
1. Check service status: `docker compose ps`
2. Check logs: `docker compose logs web`
3. Verify port 8080 not in use: `lsof -i :8080` (macOS/Linux)
4. Try hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on macOS)

### Check API Documentation

**Open browser:**

```bash
open http://localhost:8000/docs
```

**Expected result:**
- Swagger UI loads with endpoint list
- "GET /health" endpoint visible
- "Try it out" buttons functional

## 🧹 Clean Environment

Before starting each tutorial, clean your environment to ensure consistent results:

### Full Clean (Recommended)

```bash
# Stop services
docker compose down -v

# Remove project data
rm -rf projectDocs/*

# Restart services
docker compose up -d

# Wait for initialization
sleep 5

# Verify health
curl http://localhost:8000/health
```

**What this does:**
- `-v` flag removes Docker volumes (database state)
- `rm -rf projectDocs/*` clears all project files
- Services restart with fresh state

### Quick Clean (Preserve Docker Volumes)

```bash
# Stop services
docker compose down

# Remove project data only
rm -rf projectDocs/*

# Restart services
docker compose up -d
```

**Use when**: Switching between tutorials without needing database reset

### Docker Image Clean (If Issues Persist)

```bash
# Stop services
docker compose down -v

# Remove images
docker compose down --rmi all

# Rebuild from scratch
docker compose up --build -d
```

**Use when**: Suspect stale Docker images causing issues

## 🛠️ Alternative Setup (Local Development)

If you prefer running services locally without Docker:

### Backend API

```bash
# Install Python dependencies
./setup.sh
source .venv/bin/activate

# Create projectDocs directory
mkdir -p projectDocs

# Start API
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

**Expected output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Web UI

```bash
# Install Node dependencies
cd apps/web
npm install

# Start dev server
npm run dev
```

**Expected output:**

```
  VITE v7.2.5  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Note**: Local frontend runs on port 5173, not 8080

## 🚨 Common Issues

### Port Already in Use

**Error:**

```
Error: bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**

```bash
# Find process using port
lsof -i :8000   # macOS/Linux
netstat -ano | findstr :8000   # Windows

# Kill process
kill -9 <PID>   # macOS/Linux
taskkill /PID <PID> /F   # Windows

# Restart services
docker compose up -d
```

### Docker Permission Denied

**Error:**

```
permission denied while trying to connect to the Docker daemon socket
```

**Solution (Linux):**

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Activate group
newgrp docker

# Or log out and log back in
```

**Solution (macOS/Windows):**
- Ensure Docker Desktop is running
- Check whale icon in menu bar/system tray

### Volume Permission Errors

**Error:**

```
PermissionError: [Errno 13] Permission denied: '/app/projectDocs'
```

**Solution:**

```bash
# Ensure projectDocs exists
mkdir -p projectDocs

# Fix permissions (Linux)
chmod -R 777 projectDocs

# Restart services
docker compose restart
```

### API Not Responding

**Error:**

```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Solution:**

```bash
# Check if API container is running
docker compose ps

# If not running, check logs
docker compose logs api

# Restart services
docker compose restart api

# Wait and retry
sleep 10
curl http://localhost:8000/health
```

### Web UI Shows Blank Page

**Error**: Browser shows blank page, no errors

**Solution:**

```bash
# Check web container logs
docker compose logs web

# Check browser console (F12)
# Look for CORS errors or API connection failures

# Restart web service
docker compose restart web

# Hard refresh browser
# Chrome/Firefox: Ctrl+Shift+R
# Safari: Cmd+Option+R
```

### Git Submodule Issues

**Error:**

```
fatal: not a git repository: projectDocs/.git
```

**Solution:**

```bash
# projectDocs is NOT a git submodule
# It's managed by the API service
# Do NOT run git commands inside projectDocs manually

# If corrupted, clean and restart
rm -rf projectDocs
mkdir -p projectDocs
docker compose restart api
```

## 📊 Environment Verification Checklist

Use this checklist before starting tutorials:

- [ ] Docker version 28.0+ installed
- [ ] Docker Compose version 2.0+ installed
- [ ] Repository cloned successfully
- [ ] `projectDocs/` directory exists (can be empty)
- [ ] `docker compose up -d` runs without errors
- [ ] `docker compose ps` shows both services "Up"
- [ ] `curl http://localhost:8000/health` returns healthy status
- [ ] `http://localhost:8080` loads web UI
- [ ] `http://localhost:8000/docs` shows API documentation
- [ ] No error messages in `docker compose logs`

If all checkboxes pass, you're ready for tutorials! 🎉

## 🔧 Development Environment (Optional)

For tutorial development or troubleshooting:

### Install Python Dependencies

```bash
./setup.sh
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Verify installation
python --version
# Expected: Python 3.10.0 or higher

pip list | grep fastapi
# Expected: fastapi 0.109.1 or higher
```

### Install Node Dependencies

```bash
cd apps/web
npm install

# Verify installation
npm --version
# Expected: 10.0.0 or higher

node --version
# Expected: v20.0.0 or higher
```

### Run Tests

```bash
# Backend tests
pytest tests/ -v

# Frontend tests (if available)
cd apps/web
npm test
```

## 📚 Next Steps

Environment ready! Choose your starting point:

1. **[TUI Quick Start](../tui-basics/01-quick-start.md)** - Command-line interface (5 min)
2. **[Web Interface Basics](../gui-basics/01-web-interface.md)** - Visual interface (5 min)
3. **[Learning Paths](../README.md#-learning-paths)** - Structured tutorials

## 🆘 Still Having Issues?

If you've tried everything above and still can't get started:

1. **Check Troubleshooting Guide**: [troubleshooting.md](troubleshooting.md)
2. **Search GitHub Issues**: [https://github.com/blecx/AI-Agent-Framework/issues](https://github.com/blecx/AI-Agent-Framework/issues)
3. **Create New Issue**: Include:
   - Operating system and version
   - Docker version (`docker --version`)
   - Error messages (`docker compose logs`)
   - Steps you've tried

We're here to help! 🙌
