# Error Messages Catalog

**Quick Reference Guide for Common Errors in the ISO 21500 AI-Agent Framework**

This catalog provides comprehensive error messages, root causes, solutions, and prevention tips to help you diagnose and fix issues quickly.

**Related**: [Troubleshooting Guide](shared/troubleshooting.md) | [Tutorial Index](README.md)

---

## 📊 Quick Reference Table

| Error Pattern | Category | Severity | Quick Fix |
|---------------|----------|----------|-----------|
| `Connection refused` (port 8000) | API | 🔴 Critical | `docker compose restart api` |
| `Connection refused` (port 8080) | GUI | 🔴 Critical | `docker compose restart web` |
| `Port already in use` | Docker | 🔴 Critical | `lsof -ti :8000 \| xargs kill -9` |
| `Project X not found` | API/TUI | 🟡 Medium | Check project key, run `list-projects` |
| `Unknown command: X` | API | 🟡 Medium | Check command name spelling |
| `HTTP 404 error` | API/TUI | 🟡 Medium | Verify resource exists |
| `HTTP 409 error` | API | 🟡 Medium | Resource already exists |
| `HTTP 500 error` | API | 🔴 Critical | Check API logs |
| `CORS policy` error | GUI | 🟡 Medium | Verify API running, check CORS config |
| `Git command failed` | TUI | 🟡 Medium | Configure git user.name/email |
| `Permission denied` | Docker | 🟡 Medium | Fix projectDocs ownership |
| `docker compose: command not found` | Docker | 🔴 Critical | Update Docker to 28+ |
| `Docker daemon not running` | Docker | 🔴 Critical | Start Docker Desktop |
| `Container exited with code 1` | Docker | 🔴 Critical | Check container logs |
| `Proposal X not found` | API/TUI | 🟡 Medium | Verify proposal ID |
| `Template X not found` | API | 🟡 Medium | Check template ID |
| `Blueprint X not found` | API | 🟡 Medium | Check blueprint ID |
| `RAID item X not found` | API | 🟡 Medium | Check RAID ID |
| `Invalid artifact_type` | API | 🟡 Medium | Use valid artifact type |
| `Proposal already applied` | API/TUI | 🟡 Medium | Cannot apply same proposal twice |
| `Failed to fetch` | GUI | 🔴 Critical | API not responding |
| `Blank page` | GUI | 🟡 Medium | Check browser console, API health |
| `React hydration error` | GUI | 🟡 Medium | Clear cache, rebuild |
| `not a git repository` | Git | 🟡 Medium | Don't init git in projectDocs/ |
| `Git merge conflict` | Git | 🟠 High | Reset to HEAD or recreate project |

**Legend**: 🔴 Critical (blocks all work) | 🟠 High (blocks specific feature) | 🟡 Medium (workaround available)

---

## 🌲 Error Diagnosis Decision Tree

```
START: Something's not working
│
├─ Services won't start?
│  ├─ Docker Desktop not running? → Start Docker Desktop
│  ├─ Port already in use? → See "Port Already in Use"
│  ├─ Permission errors? → See "Volume Permission Errors"
│  └─ Container exits immediately? → Check logs: docker compose logs
│
├─ Can't reach API (Connection refused)?
│  ├─ API container not running? → docker compose restart api
│  ├─ Port wrong? → Verify :8000 (API) or :8080 (Web)
│  ├─ Health check fails? → See "API Connection Issues"
│  └─ CORS error in browser? → Verify origin in API config
│
├─ TUI command fails?
│  ├─ Command not found (python)? → Use: docker compose exec api python ...
│  ├─ "Project not found"? → Check key with: list-projects
│  ├─ "Unknown command"? → Check spelling, see API docs
│  ├─ Git error? → Configure git user.name and user.email
│  └─ HTTP error? → See status code in table above
│
├─ Web UI issue?
│  ├─ Blank page? → Check browser console (F12)
│  ├─ "Failed to fetch"? → API not running or wrong URL
│  ├─ React error? → Clear cache, hard refresh
│  └─ 404 on page load? → nginx config issue, rebuild
│
├─ Git/ProjectDocs issue?
│  ├─ Merge conflict? → git reset --hard HEAD
│  ├─ "not a git repository"? → Don't init projectDocs itself
│  ├─ Permission denied? → Fix ownership: chown -R $USER projectDocs
│  └─ User not configured? → git config --global user.name/email
│
└─ Still stuck?
   └─ See [Getting Help](#-getting-help) → Create issue with logs
```

---

## 📂 Error Categories

### 1. API/Connection Errors

#### Error: Connection refused (port 8000)

**Message Pattern**:
```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Root Cause**: API container not running or not binding to port 8000

**Diagnostic Steps**:
```bash
# Check if API container is running
docker compose ps

# Expected: ai-agent-framework-api-1 with status "Up"

# Check API logs
docker compose logs api --tail=50
```

**Solution**:
```bash
# Restart API service
docker compose restart api

# Wait for initialization (10s)
sleep 10

# Verify health
curl http://localhost:8000/health
```

**Prevention**:
- Always wait 10-15 seconds after `docker compose up` before accessing API
- Check `docker compose ps` before running TUI/API commands

**Related Errors**: HTTP 500, API health check fails

---

#### Error: HTTP 404 - Project not found

**Message Pattern**:
```
HTTP 404 error
Details: Project 'TEST-123' not found
```

**Root Cause**: Project key doesn't exist in projectDocs

**Diagnostic Steps**:
```bash
# List all projects
python apps/tui/main.py projects list

# Check projectDocs directory
ls -la projectDocs/
```

**Solution**:
```bash
# Option 1: Create the project
python apps/tui/main.py projects create --key TEST-123 --name "My Project"

# Option 2: Use correct project key
# Verify key from list-projects output
```

**Prevention**:
- Always verify project key with `list-projects` before other commands
- Project keys must be 3-10 characters, uppercase, alphanumeric

**Related Errors**: Template not found, Blueprint not found, RAID item not found

---

#### Error: HTTP 409 - Project already exists

**Message Pattern**:
```
HTTP 409 error
Details: Project 'TEST-001' already exists
```

**Root Cause**: Attempting to create project with duplicate key

**Diagnostic Steps**:
```bash
# List existing projects
python apps/tui/main.py projects list
```

**Solution**:
```bash
# Use different project key
python apps/tui/main.py projects create --key TEST-002 --name "My Project"

# Or delete existing project first (caution: destructive)
rm -rf projectDocs/TEST-001
```

**Prevention**:
- Check existing projects before creating
- Use unique, descriptive project keys

**Related Errors**: Template already exists, Blueprint already exists

---

#### Error: HTTP 500 - Internal Server Error

**Message Pattern**:
```
HTTP 500 error
Details: Internal Server Error
```

**Root Cause**: Various backend errors (missing projectDocs, git config, etc.)

**Diagnostic Steps**:
```bash
# View detailed API logs
docker compose logs api --tail=100

# Look for Python tracebacks showing:
# - PermissionError (projectDocs)
# - GitError (git not configured)
# - FileNotFoundError (missing files)
```

**Solution (Missing projectDocs)**:
```bash
# Create and fix permissions
mkdir -p projectDocs
chmod 755 projectDocs
docker compose restart api
```

**Solution (Git not configured)**:
```bash
# Configure git
git config --global user.name "Tutorial User"
git config --global user.email "tutorial@example.com"

# Restart API
docker compose restart api
```

**Prevention**:
- Always create projectDocs directory before starting services
- Configure git user identity in setup

**Related Errors**: Permission denied, Git command failed

---

#### Error: Unknown command

**Message Pattern**:
```
ValueError: Unknown command: invalid_command
```

**Root Cause**: Command name not recognized by API

**Diagnostic Steps**:
```bash
# Check available commands in API docs
open http://localhost:8000/docs

# Or check domain/commands/validators.py for valid commands
```

**Solution**:
```bash
# Use correct command name
# Valid commands: assess_gaps, generate_artifact, generate_plan
# Check API docs for complete list
```

**Prevention**:
- Reference API documentation for command names
- Use code completion/autocomplete if available

**Related Errors**: Invalid artifact_type, Invalid schema

---

#### Error: CORS policy blocked

**Message Pattern (Browser Console)**:
```
Access to fetch at 'http://localhost:8000/projects' from origin 'http://localhost:8080' 
has been blocked by CORS policy
```

**Root Cause**: API not configured to allow Web UI origin

**Diagnostic Steps**:
```bash
# Check if API is running
curl http://localhost:8000/health

# Check API CORS logs
docker compose logs api | grep -i cors
```

**Solution**:
```bash
# CORS should be pre-configured in docker-compose.yml
# If error persists, rebuild services
docker compose down
docker compose up -d --build
```

**Prevention**:
- Use provided docker-compose.yml (CORS pre-configured)
- Don't modify CORS settings unless deploying to production

**Related Errors**: Failed to fetch, Network error

---

### 2. TUI Command Errors

#### Error: Command not found (python)

**Message Pattern**:
```bash
bash: python: command not found
```

**Root Cause**: Python not installed or not in PATH

**Solution (Use Docker - Recommended)**:
```bash
# Run TUI via Docker (no local Python needed)
python apps/tui/main.py --help
```

**Solution (Local Setup)**:
```bash
# Install Python 3.10+ and dependencies
./setup.sh
source .venv/bin/activate

# Use python3 instead of python
python3 apps/tui/cli.py --help
```

**Prevention**:
- Use Docker for consistent environment
- If running locally, always activate venv first

**Related Errors**: Module not found, Import error

---

#### Error: Git command failed

**Message Pattern**:
```
Git command failed: fatal: not a git repository
```
OR
```
*** Please tell me who you are.
Run: git config --global user.email "you@example.com"
```

**Root Cause**: Git user identity not configured

**Diagnostic Steps**:
```bash
# Check git configuration
git config --global user.name
git config --global user.email

# If empty, need to configure
```

**Solution**:
```bash
# Configure git globally
git config --global user.name "Tutorial User"
git config --global user.email "tutorial@example.com"

# Restart API to pick up configuration
docker compose restart api
```

**Prevention**:
- Configure git as part of initial setup
- Add to setup.sh script if automating

**Related Errors**: Permission denied (git), Not a git repository

---

#### Error: Invalid project key format

**Message Pattern**:
```
ValueError: Invalid project key format
```

**Root Cause**: Project key doesn't match requirements (3-10 chars, uppercase, alphanumeric)

**Diagnostic Steps**:
```bash
# Check project key requirements:
# - Length: 3-10 characters
# - Case: UPPERCASE only
# - Characters: A-Z, 0-9 only (no special chars)
```

**Solution**:
```bash
# ❌ Invalid examples
TEST-123    # Contains hyphen
test001     # Lowercase
AB          # Too short
VERYLONGKEY # Too long (11 chars)

# ✅ Valid examples
TEST001
PROJECT1
ABC123
```

**Prevention**:
- Use 3-10 uppercase alphanumeric characters only
- No hyphens, underscores, or special characters

**Related Errors**: Invalid artifact_type, Invalid schema

---

#### Error: Proposal not found

**Message Pattern**:
```
HTTP 404 error
Details: Proposal 'proposal-123' not found
```

**Root Cause**: Proposal ID doesn't exist for the project

**Diagnostic Steps**:
```bash
# List proposals for project
ls -la projectDocs/TEST-001/.proposals/

# Check proposal file exists
ls -la projectDocs/TEST-001/.proposals/
```

**Solution**:
```bash
# Option 1: Use correct proposal ID from list
ls -la projectDocs/TEST-001/.proposals/

# Option 2: Create proposal first
python apps/tui/main.py commands propose --project TEST-001 --command generate_plan
```

**Prevention**:
- Always verify proposal IDs from `.proposals/` metadata before applying
- Copy proposal ID exactly from list output

**Related Errors**: Proposal already applied, Target artifact not found

---

#### Error: Proposal already applied

**Message Pattern**:
```
HTTP 400 error
Details: Proposal 'proposal-123' is already applied: cannot apply twice
```

**Root Cause**: Attempting to apply proposal that's already been applied

**Diagnostic Steps**:
```bash
# Check proposal status
ls -la projectDocs/TEST-001/.proposals/

# Status should be "applied" or "pending"
```

**Solution**:
```bash
# Cannot re-apply proposals
# Options:
# 1. Create new proposal for changes
# 2. Manually edit artifact in projectDocs (not recommended)
```

**Prevention**:
- Review proposal before applying
- Check status before running apply command

**Related Errors**: Proposal rejected, Invalid proposal state

---

### 3. Docker Errors

#### Error: Port already in use

**Message Pattern**:
```
Error response from daemon: driver failed programming external connectivity 
on endpoint ai-agent-framework-api-1: Bind for 0.0.0.0:8000 failed: 
port is already allocated
```

**Root Cause**: Another process using port 8000 (API) or 8080 (Web)

**Diagnostic Steps**:
```bash
# macOS/Linux: Find process using port
lsof -i :8000

# Windows: Find process using port
netstat -ano | findstr :8000
```

**Solution (macOS/Linux)**:
```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9

# Restart services
docker compose up -d
```

**Solution (Windows)**:
```powershell
# Find PID from netstat output
netstat -ano | findstr :8000

# Kill process (replace 12345 with actual PID)
taskkill /PID 12345 /F

# Restart services
docker compose up -d
```

**Solution (Change Ports)**:
```yaml
# Edit docker-compose.yml
services:
  api:
    ports:
      - "8001:8000"  # Changed port
  web:
    ports:
      - "8081:80"    # Changed port
```

**Prevention**:
- Stop services before starting new ones
- Use non-standard ports if 8000/8080 conflict

**Related Errors**: Address already in use, Bind failed

---

#### Error: docker compose command not found

**Message Pattern**:
```
docker compose: command not found
```

**Root Cause**: Using old Docker version (< 28.0) without built-in compose plugin

**Diagnostic Steps**:
```bash
# Check Docker version
docker --version

# If version < 28.0, need to update or use workaround
```

**Solution (Update Docker)**:
```bash
# See Setup Guide for Docker 28+ installation
# https://docs.docker.com/engine/install/
```

**Solution (Temporary Workaround)**:
```bash
# Use docker-compose v1 (deprecated, hyphenated)
docker-compose up -d

# Note: May have compatibility issues
```

**Prevention**:
- Use Docker 28+ for best compatibility
- Update Docker regularly

**Related Errors**: docker-compose: command not found

---

#### Error: Docker daemon not running

**Message Pattern**:
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. 
Is the docker daemon running?
```

**Root Cause**: Docker Desktop/service not started

**Solution (Linux)**:
```bash
# Start Docker service
sudo systemctl start docker

# Enable on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

**Solution (macOS/Windows)**:
```
1. Open Docker Desktop from Applications/Start Menu
2. Wait for whale icon to appear in menu bar/system tray
3. Click icon, verify "Docker Desktop is running"
```

**Prevention**:
- Configure Docker Desktop to start automatically on login
- Check whale icon before running docker commands

**Related Errors**: Connection refused (docker socket)

---

#### Error: Volume permission errors

**Message Pattern**:
```
PermissionError: [Errno 13] Permission denied: '/app/projectDocs'
```

**Root Cause**: Docker container doesn't have write permissions to projectDocs

**Diagnostic Steps**:
```bash
# Check directory ownership
ls -la projectDocs/

# Should be owned by your user, not root
```

**Solution (Linux)**:
```bash
# Fix ownership
sudo chown -R $USER:$USER projectDocs/
chmod -R 755 projectDocs/

# Restart API
docker compose restart api
```

**Solution (macOS/Windows)**:
```bash
# Usually not an issue
# If occurs, recreate directory
rm -rf projectDocs
mkdir -p projectDocs
docker compose restart api
```

**Prevention**:
- Create projectDocs before starting Docker services
- Don't run docker with sudo (adds to docker group instead)

**Related Errors**: Permission denied (various), EACCES

---

#### Error: Container exits immediately

**Message Pattern**:
```
ai-agent-framework-api-1 exited with code 1
```

**Root Cause**: Various startup errors (env vars, imports, config)

**Diagnostic Steps**:
```bash
# View container logs for error details
docker compose logs api --tail=100

# Common causes:
# - Missing environment variables
# - Python import errors (missing deps)
# - Configuration file errors
# - Port conflicts
```

**Solution (Rebuild from scratch)**:
```bash
# Nuclear option: clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d

# Check logs after restart
docker compose logs api --tail=50
```

**Prevention**:
- Check logs immediately after `docker compose up`
- Ensure all prerequisites met (git config, projectDocs, etc.)

**Related Errors**: Exit code 137 (OOM), Exit code 139 (segfault)

---

### 4. Git/ProjectDocs Errors

#### Error: Not a git repository

**Message Pattern**:
```
fatal: not a git repository (or any of the parent directories): .git
```

**Root Cause**: Running git command in wrong directory OR projectDocs itself initialized as repo

**Diagnostic Steps**:
```bash
# Check if projectDocs has .git (SHOULD NOT)
ls -la projectDocs/.git

# Individual projects should have .git
ls -la projectDocs/TEST-001/.git
```

**Solution**:
```bash
# If projectDocs/.git exists, remove it
rm -rf projectDocs/.git

# Each project is auto-initialized by API
# Don't manually run 'git init' in projectDocs/

# Restart API
docker compose restart api
```

**Prevention**:
- Never run `git init` in projectDocs directory
- Individual project dirs (TEST-001/) are auto-initialized

**Related Errors**: Git command failed, Not a git directory

---

#### Error: Git merge conflict

**Message Pattern**:
```
Git merge conflict in projectDocs/TEST-001/.raid-register.md
CONFLICT (content): Merge conflict in .raid-register.md
```

**Root Cause**: Rare, caused by simultaneous commands or manual editing

**Diagnostic Steps**:
```bash
# Check git status in project
cd projectDocs/TEST-001
git status

# Will show conflicted files
```

**Solution (Reset to clean state)**:
```bash
cd projectDocs/TEST-001
git reset --hard HEAD

# Or recreate project (nuclear option)
cd ../..
rm -rf projectDocs/TEST-001
python apps/tui/main.py projects create --key TEST-001 --name "Test"
```

**Prevention**:
- Never manually edit files in projectDocs
- Don't run multiple commands simultaneously on same project

**Related Errors**: Unmerged paths, Conflicted files

---

#### Error: Permission denied (Git operations)

**Message Pattern**:
```
fatal: unable to write file: Permission denied
```

**Root Cause**: Git operations can't write to projectDocs files

**Diagnostic Steps**:
```bash
# Check file permissions
ls -la projectDocs/TEST-001/

# Check directory ownership
ls -ld projectDocs/
```

**Solution (Linux)**:
```bash
# Fix ownership recursively
sudo chown -R $USER:$USER projectDocs/
chmod -R 755 projectDocs/

# Restart API
docker compose restart api
```

**Solution (macOS/Windows)**:
```bash
# Recreate with correct permissions
rm -rf projectDocs
mkdir -p projectDocs
docker compose restart api
```

**Prevention**:
- Don't use sudo when creating projectDocs
- Ensure user has write permissions

**Related Errors**: EACCES, Operation not permitted

---

### 5. GUI/Web UI Errors

#### Error: Web UI not loading (Connection refused)

**Message Pattern (Browser)**:
```
This site can't be reached
localhost refused to connect
```

**Root Cause**: Web container not running

**Diagnostic Steps**:
```bash
# Check if web container is running
docker compose ps

# Expected: ai-agent-framework-web-1 with status "Up"

# Check web logs
docker compose logs web --tail=50
```

**Solution**:
```bash
# Restart web service
docker compose restart web
sleep 5

# Open in browser
open http://localhost:8080
```

**Prevention**:
- Verify `docker compose ps` shows all services "Up"
- Wait 10-15 seconds after starting services

**Related Errors**: ERR_CONNECTION_REFUSED, Connection timed out

---

#### Error: Web UI shows blank page

**Message Pattern**: Browser displays blank page with no content or errors

**Root Cause**: JavaScript errors, API not responding, or build issues

**Diagnostic Steps**:
```bash
# Open browser DevTools (F12)
# Check Console tab for errors:
# - "Failed to fetch" (API not responding)
# - "Unexpected token <" (HTML returned instead of JSON)
# - CORS errors
# - React errors

# Verify API is accessible
curl http://localhost:8000/health
```

**Solution (API not responding)**:
```bash
# Restart API
docker compose restart api
sleep 10

# Refresh browser (hard refresh)
# Chrome/Firefox: Ctrl+Shift+R
# Safari: Cmd+Option+R
```

**Solution (Rebuild web container)**:
```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

**Prevention**:
- Check browser console immediately if page blank
- Verify API health before accessing web UI

**Related Errors**: White screen, Empty page, No content

---

#### Error: Failed to fetch

**Message Pattern (Browser Console)**:
```
GET http://localhost:8000/health net::ERR_FAILED
Failed to fetch
```

**Root Cause**: API not running or not accessible from browser

**Diagnostic Steps**:
```bash
# Verify API is running
docker compose ps

# Test API directly
curl http://localhost:8000/health

# If curl works but browser doesn't, check nginx proxy
```

**Solution**:
```bash
# Restart both services
docker compose restart api web
sleep 10

# Refresh browser
```

**Prevention**:
- Ensure API starts before web UI
- Check `docker compose logs` for startup errors

**Related Errors**: Network error, TypeError: Failed to fetch

---

#### Error: React hydration error

**Message Pattern (Browser Console)**:
```
Uncaught Error: Minified React error #130
Warning: Expected server HTML to contain a matching <div>
```

**Root Cause**: React hydration mismatch or version incompatibility

**Diagnostic Steps**:
```bash
# Check web container build logs
docker compose logs web --tail=100

# Look for:
# - Build warnings
# - Version mismatches
# - Missing dependencies
```

**Solution**:
```bash
# Rebuild web container with fresh dependencies
docker compose down
docker compose build --no-cache web
docker compose up -d web

# Clear browser cache
# DevTools > Application > Clear Storage > Clear site data
```

**Prevention**:
- Don't modify package.json without testing
- Use provided docker-compose.yml

**Related Errors**: Hydration mismatch, React error #418, #423

---

## 🔧 Advanced Diagnostics

### Enable Debug Logging

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
# Add --verbose flag (if supported)
python apps/tui/main.py projects create --key TEST-001 --name "Test"
```

### Interactive Container Shell

**API Container:**
```bash
# Start bash shell
docker compose exec api bash

# Inside container:
python --version        # Check Python
ls -la /app/projectDocs # Check files
cd /app && pytest       # Run tests

exit
```

**Web Container:**
```bash
# Alpine Linux uses sh, not bash
docker compose exec web sh

# Inside container:
nginx -t  # Test nginx config
cat /etc/nginx/conf.d/default.conf

exit
```

### Network Debugging

**Test API from Web Container:**
```bash
# Access web container
docker compose exec web sh

# Test API endpoint (should use internal docker network)
wget -O- http://api:8000/health

# Expected: {"status":"healthy",...}
exit
```

**Inspect Docker Network:**
```bash
# List networks
docker network ls

# Inspect project network
docker network inspect ai-agent-framework_default

# Verify both containers on same network
```

---

## 🆘 Getting Help

### Before Creating an Issue

1. ✅ **Check this error catalog** (you are here!)
2. ✅ **Search existing issues**: [GitHub Issues](https://github.com/blecx/AI-Agent-Framework/issues)
3. ✅ **Try clean environment**: `docker compose down -v && docker compose up -d`
4. ✅ **Check troubleshooting guide**: [troubleshooting.md](shared/troubleshooting.md)

### Creating a Support Issue

**Template:**

```markdown
**Environment:**
- OS: [e.g., Ubuntu 22.04, macOS 13.0, Windows 11]
- Docker version: [output of `docker --version`]
- Docker Compose version: [output of `docker compose version`]

**Error Message:**
[Exact error message from this catalog, if applicable]

**Problem:**
[Clear description of issue]

**Steps to Reproduce:**
1. Run `docker compose up -d`
2. Navigate to tutorial XYZ
3. Execute command ABC
4. Observe error DEF

**Logs:**
```
[Output of `docker compose logs --tail=100`]
```

**Diagnostic Steps Tried:**
- [ ] Checked error catalog
- [ ] Tried suggested solutions
- [ ] Restarted services
- [ ] Checked logs
- [ ] Clean rebuild (down -v, up)

**Additional Context:**
[Any other relevant information]
```

### Community Resources

- **GitHub Discussions**: [Ask questions](https://github.com/blecx/AI-Agent-Framework/discussions)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (when running)
- **Development Guide**: [docs/development.md](../development.md)
- **Tutorial Index**: [README.md](README.md)

---

## ✅ Quick Health Check

Run this checklist to verify everything works:

```bash
# Services running
docker compose ps
# ✅ All services "Up"

# API health
curl http://localhost:8000/health
# ✅ Returns {"status":"healthy"}

# Web UI accessible
open http://localhost:8080
# ✅ Page loads

# TUI works
python apps/tui/main.py --help
# ✅ Shows help text

# Can create project
python apps/tui/main.py projects create --key TEST999 --name "Test"
# ✅ Returns project info

# No errors in logs
docker compose logs --tail=20
# ✅ No ERROR or CRITICAL messages
```

If all checks pass: **System healthy!** 🎉

---

## 📚 Related Documentation

- **[Troubleshooting Guide](shared/troubleshooting.md)**: Step-by-step solutions for common issues
- **[Setup Guide](shared/00-setup-guide.md)**: Initial environment setup
- **[Tutorial Index](README.md)**: All available tutorials
- **[Development Guide](../development.md)**: Contributing and development
- **[API Error Messages](../api/domain/errors.py)**: Backend error definitions

---

**Last Updated**: 2026-02-06 | **Version**: 1.0.0

**Found an error not listed here?** [Open an issue](https://github.com/blecx/AI-Agent-Framework/issues/new) or [contribute a fix](../CONTRIBUTING.md)!
