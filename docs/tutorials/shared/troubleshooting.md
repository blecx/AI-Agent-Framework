# Tutorial Troubleshooting Guide

This guide helps you resolve common issues when working with the ISO 21500 AI-Agent Framework tutorials.

## 📋 Quick Diagnosis

**Before diving into specific issues, try these quick fixes:**

```bash
# 1. Restart services
docker compose restart

# 2. Full clean and restart
docker compose down -v && docker compose up -d

# 3. Check service health
curl http://localhost:8000/health

# 4. View service logs
docker compose logs --tail=50
```

If issues persist, see specific troubleshooting sections below.

---

## 🐳 Docker Issues

### Port Already in Use

**Error Message:**

```
Error response from daemon: driver failed programming external connectivity on endpoint ai-agent-framework-api-1: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Cause**: Another process is using port 8000 (API) or 8080 (Web)

**Solution (macOS/Linux):**

```bash
# Find process using port 8000
lsof -i :8000

# Output example:
# COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# python  12345 user    3u  IPv4 0x123  0t0  TCP *:8000 (LISTEN)

# Kill the process
kill -9 12345

# Or kill all processes on port
lsof -ti :8000 | xargs kill -9

# Restart Docker services
docker compose up -d
```

**Solution (Windows):**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Output example:
# TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    12345

# Kill the process
taskkill /PID 12345 /F

# Restart Docker services
docker compose up -d
```

**Alternative Solution (Change Ports):**

Edit `docker-compose.yml`:

```yaml
services:
  api:
    ports:
      - "8001:8000"  # Changed from 8000:8000
  web:
    ports:
      - "8081:80"    # Changed from 8080:80
```

Then access API at `http://localhost:8001` and Web at `http://localhost:8081`.

### Volume Permission Errors

**Error Message:**

```
PermissionError: [Errno 13] Permission denied: '/app/projectDocs'
```

**Cause**: Docker container doesn't have write permissions to `projectDocs/` directory

**Solution (Linux):**

```bash
# Option 1: Fix directory permissions
sudo chown -R $USER:$USER projectDocs/
chmod -R 755 projectDocs/

# Option 2: More permissive (if Option 1 doesn't work)
chmod -R 777 projectDocs/

# Restart services
docker compose restart api
```

**Solution (macOS):**

```bash
# Usually not an issue on macOS
# If it occurs, recreate directory
rm -rf projectDocs
mkdir -p projectDocs
docker compose restart api
```

**Solution (Windows):**

```powershell
# Recreate directory with full permissions
Remove-Item -Recurse -Force projectDocs
New-Item -ItemType Directory -Path projectDocs

# Restart services
docker compose restart api
```

### Docker Compose Command Not Found

**Error Message:**

```
docker compose: command not found
```

**Cause**: Using old Docker version without built-in `compose` plugin

**Solution (Update Docker):**

```bash
# Check Docker version
docker --version

# If version < 28.0, update Docker:
# See Setup Guide for installation instructions

# Temporary workaround (use docker-compose v1):
docker-compose up -d   # Note: hyphenated version
```

**Note**: Docker Compose v1 (`docker-compose`) is deprecated. Update to Docker 28+ for best results.

### Docker Daemon Not Running

**Error Message:**

```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

**Solution (Linux):**

```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

**Solution (macOS):**

```
1. Open Docker Desktop from Applications
2. Wait for whale icon to appear in menu bar
3. Click whale icon, verify "Docker Desktop is running"
```

**Solution (Windows):**

```
1. Open Docker Desktop from Start Menu
2. Wait for whale icon to appear in system tray
3. Right-click whale icon, verify "Docker Desktop is running"
```

### Container Exits Immediately

**Error Message:**

```
ai-agent-framework-api-1 exited with code 1
```

**Diagnosis:**

```bash
# View container logs
docker compose logs api

# Common errors:
# - Missing environment variables
# - Python import errors
# - Port conflicts
```

**Solution:**

```bash
# Rebuild containers from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d

# Check logs again
docker compose logs api --tail=50
```

---

## 🌐 API Connection Issues

### Health Check Fails

**Error Message:**

```bash
$ curl http://localhost:8000/health
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Diagnosis Steps:**

```bash
# Step 1: Check if API container is running
docker compose ps

# Expected: ai-agent-framework-api-1 with status "Up"
# If not running, check why:
docker compose logs api

# Step 2: Check if port 8000 is accessible
netstat -an | grep 8000   # Linux/macOS
netstat -an | findstr 8000   # Windows

# Step 3: Wait for initialization (containers need ~10 seconds)
sleep 10
curl http://localhost:8000/health
```

**Solution 1: Restart API Service**

```bash
docker compose restart api
sleep 10
curl http://localhost:8000/health
```

**Solution 2: Check Logs for Errors**

```bash
docker compose logs api --tail=100

# Look for:
# - Import errors (missing dependencies)
# - Configuration errors (missing env vars)
# - Port binding errors
```

**Solution 3: Rebuild API Container**

```bash
docker compose down
docker compose build api
docker compose up -d api
```

### API Returns 500 Internal Server Error

**Error Message:**

```bash
$ curl http://localhost:8000/projects
{"detail":"Internal Server Error"}
```

**Diagnosis:**

```bash
# View detailed error logs
docker compose logs api --tail=100

# Look for Python tracebacks
# Common causes:
# - Missing projectDocs directory
# - Git configuration errors
# - LLM service unavailable (OK, should fallback)
```

**Solution (Missing projectDocs):**

```bash
# Ensure projectDocs exists and is writable
mkdir -p projectDocs
chmod 755 projectDocs
docker compose restart api
```

**Solution (Git Configuration):**

```bash
# Configure git (required for projectDocs operations)
git config --global user.name "Tutorial User"
git config --global user.email "tutorial@example.com"

# Restart API
docker compose restart api
```

### CORS Errors (from Web UI)

**Error Message (Browser Console):**

```
Access to fetch at 'http://localhost:8000/projects' from origin 'http://localhost:8080' has been blocked by CORS policy
```

**Cause**: API not configured to allow requests from Web UI origin

**Solution (Temporary - Development Only):**

```bash
# Check API CORS configuration
docker compose logs api | grep -i cors

# Expected: CORS enabled for http://localhost:8080

# If CORS not enabled, rebuild API with correct config
docker compose down
docker compose up -d --build
```

**Note**: CORS is pre-configured in `docker-compose.yml`. This error usually indicates API not running or wrong URL.

---

## 💻 TUI Command Failures

### Command Not Found (python)

**Error Message:**

```bash
$ python apps/tui/cli.py --help
bash: python: command not found
```

**Solution (Use Docker):**

```bash
# Instead of running TUI locally, use Docker:
docker compose exec api python /app/apps/tui/cli.py --help
```

**Solution (Local Setup):**

```bash
# Install Python dependencies
./setup.sh
source .venv/bin/activate

# Use python3 instead of python
python3 apps/tui/cli.py --help

# Or create alias
alias python=python3
```

### TUI Command Returns Error

**Error Message:**

```bash
$ docker compose exec api python /app/apps/tui/cli.py create-project TEST-001 "Test"
Error: Failed to create project
```

**Diagnosis:**

```bash
# Run with verbose logging
docker compose exec api python /app/apps/tui/cli.py create-project TEST-001 "Test" --verbose

# Check API logs
docker compose logs api --tail=50
```

**Common Causes:**

1. **API not responding**: See [API Connection Issues](#-api-connection-issues)
2. **Project already exists**: Choose different project key
3. **Invalid project key format**: Must be uppercase, alphanumeric, 3-10 chars

**Solution (Project Already Exists):**

```bash
# List existing projects
docker compose exec api python /app/apps/tui/cli.py list-projects

# Use different key
docker compose exec api python /app/apps/tui/cli.py create-project TEST-002 "Test Project"
```

### Git Errors in TUI Commands

**Error Message:**

```
Git command failed: 'git' is not recognized as an internal or external command
```

**Cause**: Git not installed in API container (should not happen with provided Docker image)

**Solution:**

```bash
# Verify git is available in container
docker compose exec api git --version

# If not available, rebuild container
docker compose down
docker compose build --no-cache api
docker compose up -d
```

---

## 🖥️ GUI Issues

### Web UI Not Loading

**Error Message (Browser):**

```
This site can't be reached
localhost refused to connect
```

**Diagnosis:**

```bash
# Check if web container is running
docker compose ps

# Expected: ai-agent-framework-web-1 with status "Up"

# Check web container logs
docker compose logs web
```

**Solution 1: Restart Web Service**

```bash
docker compose restart web
sleep 5

# Try accessing again
open http://localhost:8080
```

**Solution 2: Check Port 8080 Availability**

```bash
# Check if port 8080 is in use
lsof -i :8080   # macOS/Linux
netstat -ano | findstr :8080   # Windows

# If in use, kill process or change port in docker-compose.yml
```

**Solution 3: Clear Browser Cache**

```
1. Open browser DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"
4. Or try incognito/private window
```

### Web UI Shows Blank Page

**Error Message**: Browser shows blank page, no content, no errors

**Diagnosis:**

```bash
# Check browser console (F12)
# Look for JavaScript errors or API connection failures

# Common errors:
# - "Failed to fetch" (API not responding)
# - "Unexpected token <" (HTML returned instead of JSON)
# - CORS errors
```

**Solution 1: Verify API Connectivity**

```bash
# From your machine (not inside container)
curl http://localhost:8000/health

# Expected: {"status":"healthy",...}

# If fails, see API Connection Issues section
```

**Solution 2: Check Web Container Nginx Config**

```bash
# View nginx logs
docker compose logs web --tail=50

# Look for:
# - Port binding errors
# - File permission errors
# - Proxy configuration errors
```

**Solution 3: Rebuild Web Container**

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### Web UI Can't Connect to API

**Error Message (Browser Console):**

```
GET http://localhost:8000/health net::ERR_CONNECTION_REFUSED
```

**Cause**: Web UI running but API not accessible

**Solution:**

```bash
# Verify API is running
docker compose ps

# Restart API if not running
docker compose restart api
sleep 10

# Refresh browser
```

**Note**: Web UI proxies API requests through nginx. If direct `curl` works but Web UI doesn't:

```bash
# Check nginx proxy configuration
docker compose exec web cat /etc/nginx/conf.d/default.conf

# Look for:
# location /api {
#   proxy_pass http://api:8000;
# }
```

### React Component Not Rendering

**Error Message (Browser Console):**

```
Uncaught Error: Minified React error #130
```

**Cause**: React hydration mismatch or incompatible versions

**Solution:**

```bash
# Rebuild web container with fresh dependencies
docker compose down
docker compose build --no-cache web
docker compose up -d web

# Hard refresh browser
# Chrome/Firefox: Ctrl+Shift+R
# Safari: Cmd+Option+R
```

---

## 📂 Git Issues (projectDocs)

### Git Conflicts in projectDocs

**Error Message:**

```
Git merge conflict in projectDocs/TEST-001/.raid-register.md
```

**Cause**: Rare, but can occur if manually editing files in projectDocs or running multiple commands simultaneously

**Solution:**

```bash
# Option 1: Reset to clean state
cd projectDocs/TEST-001
git reset --hard HEAD

# Option 2: Delete and recreate project
cd ../..
rm -rf projectDocs/TEST-001
docker compose exec api python /app/apps/tui/cli.py create-project TEST-001 "Test Project"
```

**Prevention**: Never manually edit files in `projectDocs/`. Always use TUI/API commands.

### projectDocs Not a Git Repository

**Error Message:**

```
fatal: not a git repository (or any of the parent directories): .git
```

**Cause**: `projectDocs/` itself should NOT be a git repository. Individual project directories (e.g., `TEST-001/`) are git repos.

**Solution:**

```bash
# Do NOT run 'git init' in projectDocs/
# Each project is auto-initialized by API

# If you accidentally initialized projectDocs:
rm -rf projectDocs/.git

# Restart API
docker compose restart api
```

### Git User Not Configured

**Error Message:**

```
*** Please tell me who you are.
Run: git config --global user.email "you@example.com"
     git config --global user.name "Your Name"
```

**Cause**: Git needs user identity for commits (API creates commits for each command)

**Solution:**

```bash
# Configure git globally
git config --global user.name "Tutorial User"
git config --global user.email "tutorial@example.com"

# Restart API to pick up configuration
docker compose restart api
```

**Note**: These credentials are only for local commits, not pushed anywhere.

---

## 🐌 Performance Issues

### Slow API Responses

**Symptom**: API requests take 5+ seconds to respond

**Diagnosis:**

```bash
# Check system resources
docker stats

# Look for high CPU or memory usage
# API container should use < 500MB RAM, < 50% CPU
```

**Solution 1: Increase Docker Resources**

```
Docker Desktop > Settings > Resources

- CPUs: Increase to 4+
- Memory: Increase to 4GB+
- Restart Docker Desktop
```

**Solution 2: Disable LLM Integration (Faster, No AI)**

Edit `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - DISABLE_LLM=true  # Add this line
```

Then restart: `docker compose up -d`

**Solution 3: Check Disk I/O**

```bash
# Large projectDocs can slow operations
du -sh projectDocs/*

# If any project > 100MB, investigate
# Most projects should be < 5MB
```

### Slow Docker Build

**Symptom**: `docker compose build` takes 10+ minutes

**Solution 1: Use BuildKit (Faster)**

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Rebuild
docker compose build
```

**Solution 2: Use Cache**

```bash
# Build with cache (default)
docker compose build

# Only use --no-cache if you suspect cache corruption
docker compose build --no-cache  # Slower but guaranteed fresh
```

**Solution 3: Check Disk Space**

```bash
# Docker needs significant free space
df -h

# Clean old images/containers if low
docker system prune -a
```

---

## 🔍 Debugging Techniques

### Enable Verbose Logging

**API Container:**

Edit `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - LOG_LEVEL=DEBUG  # Changed from INFO
```

Restart: `docker compose up -d`

View logs: `docker compose logs -f api`

**TUI Commands:**

```bash
# Add --verbose flag
docker compose exec api python /app/apps/tui/cli.py create-project TEST-001 "Test" --verbose
```

### Interactive Shell in Container

**Access API Container:**

```bash
# Start bash shell
docker compose exec api bash

# Now inside container:
python --version
ls -la /app
cd /app/projectDocs
git log --oneline

# Exit shell
exit
```

**Access Web Container:**

```bash
docker compose exec web sh  # Note: sh, not bash (Alpine Linux)

# Inside container:
nginx -t  # Test nginx config
cat /etc/nginx/conf.d/default.conf

# Exit shell
exit
```

### Network Debugging

**Test API Connectivity from Web Container:**

```bash
# Access web container
docker compose exec web sh

# Test API endpoint
wget -O- http://api:8000/health

# Expected: {"status":"healthy",...}

# If fails, network issue between containers
exit
```

**Check Docker Network:**

```bash
# List networks
docker network ls

# Inspect project network
docker network inspect ai-agent-framework_default

# Verify both containers are on same network
```

### Compare Expected vs Actual Output

**Use validation expected outputs:**

```bash
# Expected output for health check
cat docs/tutorials/validation/expected-outputs/tui-basics/01-health-check.json

# Actual output
curl http://localhost:8000/health | jq .

# Compare using diff
curl http://localhost:8000/health | jq . > /tmp/actual.json
diff docs/tutorials/validation/expected-outputs/tui-basics/01-health-check.json /tmp/actual.json
```

---

## 🆘 Getting Help

### Before Creating an Issue

1. **Check this troubleshooting guide** (you are here!)
2. **Search existing issues**: [https://github.com/blecx/AI-Agent-Framework/issues](https://github.com/blecx/AI-Agent-Framework/issues)
3. **Try clean environment**: `docker compose down -v && docker compose up -d`
4. **Check setup guide**: [00-setup-guide.md](00-setup-guide.md)

### Creating a Support Issue

**Include this information:**

```markdown
**Environment:**
- OS: [e.g., Ubuntu 22.04, macOS 13.0, Windows 11]
- Docker version: [output of `docker --version`]
- Docker Compose version: [output of `docker compose version`]

**Problem:**
[Clear description of issue]

**Steps to Reproduce:**
1. Run `docker compose up -d`
2. Navigate to tutorial XYZ
3. Execute command ABC
4. Observe error DEF

**Error Messages:**
```
[Paste complete error messages]
```

**Logs:**
```
[Output of `docker compose logs --tail=50`]
```

**What I've Tried:**
- [List troubleshooting steps you've already attempted]
```

### Community Resources

- **GitHub Discussions**: [https://github.com/blecx/AI-Agent-Framework/discussions](https://github.com/blecx/AI-Agent-Framework/discussions)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Development Guide**: [docs/development.md](../../development.md)

---

## ✅ Issue Resolution Checklist

After resolving an issue, verify everything works:

- [ ] `docker compose ps` shows all services "Up"
- [ ] `curl http://localhost:8000/health` returns `{"status":"healthy"}`
- [ ] `http://localhost:8080` loads Web UI
- [ ] TUI command works: `docker compose exec api python /app/apps/tui/cli.py --help`
- [ ] Can create project via TUI or GUI
- [ ] No errors in `docker compose logs`

If all checkboxes pass, issue is resolved! 🎉

---

## 📚 Related Documentation

- **[Setup Guide](00-setup-guide.md)**: Initial environment setup
- **[Tutorial Index](../README.md)**: All available tutorials
- **[Development Guide](../../development.md)**: Contributing and development
- **[API Reference](../../api/)**: Complete API documentation

---

**Last Updated**: 2024-01-15 | **Version**: 1.0.0

Found a troubleshooting solution not listed here? [Contribute it!](../../CONTRIBUTING.md)
