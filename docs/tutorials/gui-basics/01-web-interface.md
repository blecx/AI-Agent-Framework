# GUI Web Interface Basics

**Duration:** 10 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Get familiar with the AI-Agent Framework's web interface. This comprehensive guide walks you through accessing the web UI, understanding its layout and components, using browser developer tools, and navigating the API documentation. You'll learn the fundamentals needed for all subsequent GUI tutorials.

## Learning Objectives

By the end of this tutorial, you will:
- Access and navigate the web UI with confidence
- Understand the complete UI layout and component hierarchy
- Use browser developer tools for troubleshooting
- Navigate between projects efficiently
- Access and use the interactive API documentation
- Verify system health and readiness
- Use keyboard shortcuts for improved navigation
- Understand accessibility features

## Prerequisites

- **Docker Compose running:** `docker compose up -d` (or `docker compose up` for logs)
- **Web browser:** Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+ recommended
- **Network access:** Ports 8080 (web UI) and 8000 (API) must be available
- **No coding knowledge required** - this is a visual, browser-based tutorial

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Live demonstration of web interface navigation
> - Overview of all UI components
> - Browser developer tools usage
> - API documentation walkthrough
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

### Quick Verification

Before starting, verify your environment is ready:

```bash
# Check Docker containers are running
docker ps | grep -E "ai-agent.*-(web|api)"

# Expected: Two containers running (web and api)
```

**Expected Output:**
```
CONTAINER ID   IMAGE                STATUS        PORTS
abc123...      ai-agent-web:latest  Up 2 minutes  0.0.0.0:8080->80/tcp
def456...      ai-agent-api:latest  Up 2 minutes  0.0.0.0:8000->8000/tcp
```

✅ **Pre-flight Checkpoint:** Both containers running, ports accessible

## Steps

### Step 1: Access Web Interface

Open your web browser and navigate to:
```
http://localhost:8080
```

**What happens behind the scenes:**
1. Browser sends HTTP GET request to port 8080
2. Nginx (in web container) serves the React application
3. React app loads and initializes
4. App makes API call to `/health` endpoint
5. UI renders based on API response

**Expected Visual Elements:**
- Header with "AI-Agent Framework" title
- Project selector dropdown or list in left sidebar
- Main content area (initially showing "No project selected" or project list)
- Navigation menu or tabs
- Footer with version information

**Expected Page Load Time:** 0.5-2 seconds on typical connection

✅ **Checkpoint 1.1:** Web UI loads without errors, header visible

**Screenshot Reference:** `docs/screenshots/gui-01-homepage.png` (main interface on first load)

### Step 1.1: Verify Page Load Completion

Check browser for complete page load:

**Visual Indicators:**
- No spinner/loading animation
- "AI-Agent Framework" header fully rendered
- Sidebar content visible
- No "Loading..." placeholder text

**Browser Developer Console Check (Optional but Recommended):**
1. Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)
2. Open "Console" tab
3. Look for any red error messages

**Expected Console Output:**
```
[Vite] connected.
React app initialized
API health check: OK
```

**Common Console Warnings (Safe to Ignore):**
```
Download the React DevTools for a better development experience
```

✅ **Checkpoint 1.2:** Page fully loaded, no critical errors in console

**Troubleshooting Step 1:**
- **Symptom:** "Connection refused" or "ERR_CONNECTION_REFUSED"
  - **Cause:** Web container not running
  - **Fix:** `docker compose up -d web` then retry
  
- **Symptom:** Blank white page with no content
  - **Cause:** JavaScript error preventing React render
  - **Fix:** Check browser console (F12) for errors; try hard refresh (Ctrl+Shift+R)
  
- **Symptom:** Page loads but shows "API Unavailable" error
  - **Cause:** API container not running or not reachable
  - **Fix:** Verify API container: `docker ps | grep api`, then navigate to Step 2

### Step 2: UI Layout Deep Dive

The web interface follows a standard three-panel layout optimized for project management workflows:

**Visual Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Header: AI-Agent Framework        [API Status] [Settings]   │
├──────────────┬──────────────────────────────────────────────┤
│   Sidebar    │          Main Content Area                   │
│   (Left)     │                                               │
│              │                                               │
│ □ Projects   │   [Command Panel]                            │
│   List       │   [Proposal Viewer]                          │
│              │   [Artifacts Browser]                        │
│ + Create     │   [RAID Register]                            │
│   New        │   [Workflow State]                           │
│              │                                               │
│ [Selected:]  │                                               │
│ TODO-001     │                                               │
│              │                                               │
├──────────────┴──────────────────────────────────────────────┤
│ Footer: Version 1.0 | Docs | Support                        │
└─────────────────────────────────────────────────────────────┘
```

#### 2.1: Sidebar (Left Panel - 25% width)

**Purpose:** Project selection and quick navigation

**Components:**
1. **Projects List**
   - Shows all accessible projects
   - Click to select/activate a project
   - Selected project highlighted in blue
   - Displays project key (e.g., "TODO-001")

2. **Create New Project Button**
   - Green "+" icon button
   - Opens project creation form
   - Located at top of sidebar

3. **Project Selector Dropdown** (Alternative UI)
   - Dropdown showing current project
   - Click to switch projects
   - Shows project count (e.g., "5 projects")

**Keyboard Navigation:**
- `Tab` to focus sidebar
- `↑↓` arrow keys to navigate projects
- `Enter` to select project
- `Ctrl+N` to create new project (if focus in sidebar)

**Screenshot Reference:** `docs/screenshots/gui-01-sidebar.png`

✅ **Checkpoint 2.1:** Sidebar visible, understand project selection

#### 2.2: Main Content Area (Center Panel - 70% width)

**Purpose:** Display project details, execute commands, review artifacts

**Dynamic Content Sections (vary based on selected project):**

1. **Command Panel** (When project selected)
   - Command dropdown (e.g., "create_charter", "assess_gaps")
   - Description textarea for command context
   - "Propose" button to execute command
   - Recent proposals list below

2. **Artifacts Browser**
   - Tree view of project artifacts
   - File/folder structure
   - Click to view file content
   - Download/export buttons

3. **Proposal Viewer** (Overlay/Modal)
   - Appears after proposing command
   - Shows proposed changes
   - Apply/Reject action buttons
   - Diff viewer for file changes

4. **Project Details Dashboard** (When no section selected)
   - Project metadata (key, name, description)
   - Current phase (e.g., "Initiating", "Planning")
   - Artifact count
   - Recent activity feed

5. **RAID Register** (Tab/Section)
   - Risks, Actions, Issues, Decisions table
   - Add new RAID entry form
   - Filter/sort capabilities

6. **Workflow State Diagram** (Tab/Section)
   - Visual ISO 21500 phase diagram
   - Current phase highlighted
   - Transition buttons
   - Progress indicators

**Content Area States:**
- **No Project Selected:** Shows "Select a project to begin" placeholder
- **Project Selected:** Shows command panel + artifacts browser
- **Proposal Active:** Shows proposal modal overlay
- **Loading:** Shows spinner with "Loading project..." message

**Screenshot Reference:** `docs/screenshots/gui-01-main-content.png`

✅ **Checkpoint 2.2:** Main content area visible, understand dynamic sections

#### 2.3: Header (Top Bar - 100% width, fixed position)

**Purpose:** Global navigation and system status

**Components:**

1. **Application Title (Left)**
   - "AI-Agent Framework" text
   - Clickable logo/icon
   - Links to home/dashboard

2. **API Status Indicator (Center-Right)**
   - Green dot: API healthy
   - Red dot: API unavailable
   - Yellow dot: API degraded performance
   - Tooltip shows last health check time
   - Refreshes every 30 seconds

3. **Settings/Config Icon (Right)**
   - Gear icon button
   - Opens configuration panel
   - Shows: theme toggle, LLM settings, API endpoint config

4. **Help/Documentation Link (Right)**
   - Question mark icon
   - Links to API docs or tutorial index

**API Status Indicator Details:**
```
●  API Healthy        (Green  - Last check: 2s ago)
●  API Unavailable    (Red    - Last check: 45s ago)
●  API Slow           (Yellow - Response time: 3.2s)
```

**Screenshot Reference:** `docs/screenshots/gui-01-header-status.png`

✅ **Checkpoint 2.3:** Header visible, API status indicator working

#### 2.4: Footer (Bottom Bar - 100% width)

**Purpose:** Version info, links, and quick access

**Components:**
- Version number (e.g., "v1.0.0-beta")
- Link to documentation
- Link to GitHub repository
- Support/contact link
- Last update timestamp

**Example Footer Content:**
```
AI-Agent Framework v1.0.0 | Docs | GitHub | Support | Last updated: 2026-02-06 14:32
```

✅ **Checkpoint 2.4:** Complete UI layout understood

**Keyboard Shortcuts Reference:**
| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New project (when sidebar focused) |
| `Ctrl+K` | Focus command panel search |
| `Ctrl+P` | Open project switcher |
| `/` | Focus search/filter |
| `Esc` | Close modal/drawer |
| `?` | Show keyboard shortcuts help |

**Accessibility Features:**
- Screen reader compatible (ARIA labels on all interactive elements)
- High contrast mode support
- Keyboard-only navigation possible
- Focus indicators on all interactive elements
- Skip to content link for screen readers

### Step 3: Navigate to API Documentation

The API documentation provides interactive exploration of all backend endpoints.

#### 3.1: Access Swagger UI

**Option A: Via Header Link**
1. Look for "API Docs" link in header (may be in help menu or settings)
2. Click the link
3. New tab opens to Swagger UI

**Option B: Direct URL**
Navigate directly to:
```
http://localhost:8000/docs
```

**Expected Swagger UI Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ AI-Agent Framework API                                 v1.0.0│
│ ISO 21500 Project Management with AI                        │
├─────────────────────────────────────────────────────────────┤
│ Endpoints:                                                   │
│                                                              │
│ ▼ projects - Project management endpoints                   │
│   GET    /projects          List all projects               │
│   POST   /projects          Create new project              │
│   GET    /projects/{key}    Get project details             │
│                                                              │
│ ▼ commands - Command execution                              │
│   POST   /commands/propose  Propose a command               │
│   POST   /commands/apply    Apply a proposal                │
│   GET    /commands/list     List proposals                  │
│                                                              │
│ ▼ artifacts - Artifact management                           │
│   GET    /artifacts         List artifacts                  │
│   GET    /artifacts/{path}  Get artifact content            │
│                                                              │
│ ▼ health - System health                                    │
│   GET    /health            Health check                    │
│                                                              │
│ Schemas:                                                     │
│   ProjectCreate, ProjectResponse, ProposalRequest, ...      │
└─────────────────────────────────────────────────────────────┘
```

**Expected Page Load Time:** < 1 second

✅ **Checkpoint 3.1:** API documentation loads in Swagger UI

**Screenshot Reference:** `docs/screenshots/gui-01-swagger-overview.png`

#### 3.2: Explore Endpoint Categories

Swagger UI groups endpoints by tags. Click to expand each category:

**Available Categories:**
1. **projects** (4 endpoints)
   - Create, read, update, delete projects
   - List all projects with filters

2. **commands** (6 endpoints)
   - Propose commands
   - Apply/reject proposals
   - List proposals by project
   - View proposal details

3. **artifacts** (3 endpoints)
   - List artifacts by project
   - Get artifact content
   - Export artifacts as ZIP

4. **health** (1 endpoint)
   - System health check
   - Returns API status and configuration

5. **raid** (5 endpoints - Step 2 feature)
   - CRUD operations for RAID entries
   - Filter and search RAID items

6. **workflow** (3 endpoints - Step 2 feature)
   - Get workflow state
   - Update project phase
   - List allowed transitions

**Exploring an Endpoint:**
1. Click on any endpoint (e.g., "GET /projects")
2. Endpoint expands showing:
   - Description
   - Parameters (query, path, body)
   - Request body schema (for POST/PUT)
   - Response schema with examples
   - "Try it out" button

✅ **Checkpoint 3.2:** Understand endpoint categories, expanded at least one endpoint

### Step 4: Execute Health Check Endpoint (Interactive)

Now let's test an API endpoint interactively using Swagger UI.

#### 4.1: Locate Health Endpoint

1. Scroll to the **health** section (usually at bottom)
2. Click to expand the section
3. Find `GET /health` endpoint
4. Click on the endpoint row to expand details

**Endpoint Details Shown:**
```
GET /health

Returns system health status and configuration

Responses:
  200 Successful Response
    {
      "status": "healthy",
      "docs_path": "string",
      "timestamp": "string"
    }
```

✅ **Checkpoint 4.1:** Health endpoint expanded, see response schema

#### 4.2: Execute "Try it out"

1. Click the blue "Try it out" button (top right of endpoint panel)
2. UI changes to execution mode (button becomes "Execute")
3. No parameters needed for `/health` (it's a simple GET request)
4. Click the blue "Execute" button

**What happens:**
1. Swagger UI sends GET request to `http://localhost:8000/health`
2. API receives request and executes health check
3. Response returned to browser
4. Swagger UI displays response below

**Expected Response (Status: 200 OK):**
```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "timestamp": "2026-02-06T14:35:22.123Z"
}
```

**Response Headers (Typical):**
```
content-type: application/json
content-length: 85
date: Thu, 06 Feb 2026 14:35:22 GMT
server: uvicorn
```

**Request URL (Shown in Swagger UI):**
```
http://localhost:8000/health
```

**Response Time:** Typically 5-50ms

✅ **Checkpoint 4.2:** Health check executed successfully, received 200 OK response

**Screenshot Reference:** `docs/screenshots/gui-01-health-check-response.png`

#### 4.3: Interpret Health Response Fields

**Field Descriptions:**
| Field | Type | Description | Expected Value |
|-------|------|-------------|----------------|
| `status` | string | Overall API health | "healthy" or "degraded" or "unavailable" |
| `docs_path` | string | Path to project documents directory | "/projectDocs" or custom path |
| `timestamp` | string | ISO 8601 timestamp of check | Current UTC time |

**Possible Status Values:**
- **"healthy"** - All systems operational, API ready to serve requests
- **"degraded"** - API running but with issues (e.g., slow LLM responses, disk space low)
- **unavailable"** - Critical failure (e.g., database unreachable, disk full)

**Troubleshooting Unhealthy Responses:**

If you receive `"status": "degraded"` or `"unavailable"`:
1. Check Docker logs: `docker compose logs api --tail=50`
2. Verify `projectDocs/` directory exists and is writable
3. Check disk space: `df -h`
4. Verify environment variables: `docker compose config`

✅ **Checkpoint 4.3:** Understand health response meaning, API confirmed healthy

#### 4.4: Test Error Response (Optional)

To understand error responses, try accessing a non-existent project:

1. Expand `GET /projects/{key}`
2. Click "Try it out"
3. Enter invalid key: `INVALID-999`
4. Click "Execute"

**Expected Error Response (Status: 404 Not Found):**
```json
{
  "detail": "Project not found: INVALID-999"
}
```

**Common HTTP Status Codes in API:**
- **200 OK** - Successful request
- **201 Created** - Resource created successfully (e.g., new project)
- **400 Bad Request** - Invalid input (e.g., missing required field)
- **404 Not Found** - Resource doesn't exist
- **422 Unprocessable Entity** - Validation error (e.g., invalid project key format)
- **500 Internal Server Error** - Server-side error

✅ **Checkpoint 4.4:** Understand error responses, tested 404 behavior

### Step 5: Return to Web UI and Verify Integration

Now that we've verified the API is healthy, return to the main web UI to see integration.

#### 5.1: Navigate Back to Web UI

1. Open new browser tab (or switch to existing tab)
2. Navigate to `http://localhost:8080`
3. Web UI should show updated API status

**API Status Indicator Check:**
- Look for green dot indicator in header (if visible)
- Tooltip should show "API Healthy - Last check: Xs ago"
- If red dot, the UI detected API issues during your absence

✅ **Checkpoint 5.1:** Web UI shows healthy API connection

#### 5.2: Open Browser Developer Tools (Advanced)

For debugging and learning, open browser DevTools:

**How to Open:**
- **Chrome/Edge:** F12 or Ctrl+Shift+I (Windows/Linux), Cmd+Option+I (Mac)
- **Firefox:** F12 or Ctrl+Shift+I (Windows/Linux), Cmd+Option+I (Mac)
- **Safari:** Cmd+Option+I (Mac, requires enabling developer menu first)

**DevTools Tabs to Explore:**
1. **Console** - JavaScript logs, errors, warnings
2. **Network** - HTTP requests to API (see all `/api/*` calls)
3. **Elements** - HTML structure (inspect React components)
4. **Application** - Local storage, session storage, cookies

**Example Console Output (Normal Operation):**
```javascript
[Vite] connected.
✓ React app initialized
ℹ API health check: OK (23ms)
ℹ Fetching projects list...
✓ Projects loaded: 0 projects
```

**Example Network Tab (Filter by "api"):**
```
Name                    Status  Type    Size    Time
/health                 200     json    85 B    23ms
/projects               200     json    2 B     45ms
```

✅ **Checkpoint 5.2:** DevTools open, console shows no errors

**Screenshot Reference:** `docs/screenshots/gui-01-devtools-console.png`

#### 5.3: Test API Connection from DevTools Console

Advanced users can test API directly from browser console:

**Open Console tab in DevTools, then run:**
```javascript
fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log('API Health:', data))
  .catch(err => console.error('API Error:', err));
```

**Expected Console Output:**
```javascript
API Health: {status: 'healthy', docs_path: '/projectDocs', timestamp: '2026-02-06T...'}
```

This confirms the browser can directly reach the API (bypassing the React app).

✅ **Checkpoint 5.3:** Direct API test successful from browser console

## UI Components Reference

Detailed reference for all components you'll encounter in GUI tutorials:

| Component | Purpose | Location | Key Features |
|-----------|---------|----------|-------------|
| **ProjectSelector** | Choose/create projects | Sidebar (left) | Dropdown or list view, click to select, shows project count |
| **CommandPanel** | Execute commands | Main content | Command dropdown, description field, "Propose" button, recent proposals list |
| **ArtifactsList** | Browse generated files | Main content (tab/section) | Tree view, file preview, download buttons, folder navigation |
| **ProposalModal** | Review/apply proposals | Overlay (modal) | Proposal details, artifact previews, diff viewer, Apply/Reject buttons |
| **RAIDRegister** | Manage risks/actions/issues/decisions | Main content (tab/section) | Table view, add entry form, filter/sort controls |
| **WorkflowStateDiagram** | Visualize ISO 21500 phases | Main content (tab/section) | Phase diagram, current phase highlighted, transition buttons |
| **ArtifactViewer** | View file content | Modal or drawer | Markdown rendering, syntax highlighting, raw view toggle |

**Component Interaction Flow:**
```
ProjectSelector (select project)
    ↓
CommandPanel (propose command)
    ↓
ProposalModal (review proposal)
    ↓
Apply → ArtifactsList (view created artifacts)
    ↓
ArtifactViewer (read artifact content)
```

## What You've Learned

By completing this tutorial, you can now:

✅ Access web UI at http://localhost:8080 with confidence  
✅ Navigate complete UI layout (sidebar, main content, header, footer)  
✅ Understand each UI component's purpose and location  
✅ Access and use interactive API documentation (Swagger UI)  
✅ Execute health check endpoint and interpret responses  
✅ Use browser developer tools for troubleshooting  
✅ Verify API-UI integration is working  
✅ Understand keyboard shortcuts and accessibility features  
✅ Know all main UI components for upcoming tutorials  

**Key Concepts Mastered:**
- Three-panel UI layout pattern
- API status monitoring
- Interactive API documentation (Swagger/OpenAPI)
- HTTP status codes (200, 404, 422, 500)
- Health check endpoint pattern
- Browser DevTools for debugging

## Next Steps

Now that you understand the web interface fundamentals:

1. **[Tutorial 02: Project Creation](02-project-creation.md)** ✨ NEXT - Create projects via GUI (15 min)
2. **[TUI Quick Start](../tui-basics/01-quick-start.md)** - Command-line alternative for comparison (10 min)
3. **[Tutorial 03: Commands and Proposals](03-commands-and-proposals.md)** - Execute workflow (20 min)

**Recommended Path:** Complete all GUI Basics tutorials (01-05) before exploring advanced topics.

## TUI Equivalent

The TUI (Terminal UI) provides the same functionality via command-line:

**Access TUI:**
```bash
python apps/tui/main.py --help
```

**Health Check (TUI):**
```bash
python apps/tui/main.py health
```

**List Projects (TUI):**
```bash
python apps/tui/main.py projects list
```

See [TUI Quick Start](../tui-basics/01-quick-start.md) for full command-line tutorial.

**GUI vs TUI Comparison:**
| Feature | GUI (Web) | TUI (CLI) |
|---------|-----------|-----------|
| **Access** | Browser (port 8080) | Terminal command |
| **Visualization** | Visual components, colors | Text output, tables |
| **Navigation** | Mouse clicks | Keyboard commands |
| **Learning Curve** | Easier for beginners | Faster for experts |
| **Remote Access** | Requires port forwarding | Works over SSH |
| **Automation** | Limited (manual clicks) | Excellent (scriptable) |

## Troubleshooting

Comprehensive troubleshooting guide for common web UI issues:

### Issue 1: Web UI Not Loading

**Symptoms:**
- Browser shows "Connection refused"
- Error: `ERR_CONNECTION_REFUSED`
- Page times out or never loads

**Diagnostic Steps:**
```bash
# 1. Check if web container is running
docker ps | grep web

# Expected: ai-agent-web container with "Up" status

# 2. Check web container logs
docker compose logs web --tail=50

# Look for: "Listening on port 80" or startup errors

# 3. Verify port 8080 is exposed
docker port $(docker compose ps -q web)

# Expected: 80/tcp -> 0.0.0.0:8080
```

**Solutions:**
- **Container not running:** `docker compose up -d web`
- **Port conflict:** Check if another service uses port 8080: `lsof -i :8080` (Linux/Mac) or `netstat -ano | findstr :8080` (Windows). Stop conflicting service or change port in `docker-compose.yml`
- **Container crashing:** Check logs for errors, ensure all dependencies present

**Expected Resolution Time:** 2-5 minutes

### Issue 2: API Docs Not Accessible

**Symptoms:**
- Clicking "API Docs" link gives 404
- Direct navigation to `:8000/docs` fails
- Error: "This site can't be reached"

**Diagnostic Steps:**
```bash
# 1. Check if API container is running
docker ps | grep api

# 2. Test API directly with curl
curl http://localhost:8000/health

# Expected: {"status":"healthy",...}

# 3. Check API container logs
docker compose logs api --tail=50

# Look for: "Uvicorn running on http://0.0.0.0:8000"
```

**Solutions:**
- **API container not running:** `docker compose up -d api`
- **Port 8000 conflict:** Change API port in `docker-compose.yml` (update both web proxy config and API binding)
- **Firewall blocking:** Temporarily disable firewall or add rule allowing port 8000
- **API startup failure:** Check logs for Python errors or missing `PROJECT_DOCS_PATH`

**Expected Resolution Time:** 3-8 minutes

### Issue 3: Blank White Page (React Error)

**Symptoms:**
- Page loads but shows only white background
- No content, no header, no sidebar
- Browser title shows page name but body is empty

**Diagnostic Steps:**
1. Open browser DevTools (F12)
2. Check Console tab for red errors
3. Look for JavaScript exceptions or module loading failures

**Common Error Messages:**
```
Uncaught ReferenceError: React is not defined
Failed to load module: [module-name]
Uncaught TypeError: Cannot read property 'X' of undefined
```

**Solutions:**
- **React module error:** Hard refresh browser (Ctrl+Shift+R) to clear cached JS
- **Build error:** Rebuild web container: `docker compose build web --no-cache`
- **Environment mismatch:** Check Node version in Dockerfile matches package.json requirements
- **Corrupted build:** Delete `apps/web/dist/` and rebuild: `cd apps/web && npm run build`

**Expected Resolution Time:** 5-10 minutes

### Issue 4: "API Unavailable" Error in UI

**Symptoms:**
- Web UI loads correctly
- Red dot indicator in header
- Error banner: "Cannot connect to API"
- Console shows `fetch failed` errors

**Diagnostic Steps:**
```bash
# 1. Test API health directly
curl http://localhost:8000/health

# 2. Check network connectivity from browser
# Open DevTools → Network tab → Filter "api" → Refresh page
# Look for failed requests (red status)

# 3. Check CORS configuration
docker compose logs api | grep CORS
```

**Solutions:**
- **API container down:** Restart API: `docker compose restart api`
- **CORS misconfiguration:** Verify `CORS_ORIGINS` in API environment includes `http://localhost:8080`
- **Proxy misconfiguration:** Check Nginx config in `docker/web/nginx.conf` - ensure `proxy_pass http://api:8000` is correct
- **Network issue:** Verify both containers on same Docker network: `docker network inspect ai-agent-network`

**Expected Resolution Time:** 5-15 minutes

### Issue 5: Slow Performance / Timeouts

**Symptoms:**
- Page loads but very slowly (> 10 seconds)
- API requests timeout after 30+ seconds
- UI feels unresponsive

**Diagnostic Steps:**
```bash
# 1. Check system resources
docker stats

# Look for: High CPU% or Memory% on containers

# 2. Check API response times
time curl http://localhost:8000/health

# Expected: < 100ms; Slow: > 1000ms

# 3. Check disk space (projectDocs/ grows over time)
df -h
du -sh projectDocs/
```

**Solutions:**
- **High resource usage:** Stop other Docker containers or increase Docker resource limits
- **Large projectDocs:** Archive old projects: `mv projectDocs/OLD-* ~/archived-projects/`
- **LLM timeout:** Check LLM service status (LM Studio, etc.) or disable LLM features temporarily
- **Network latency:** Ensure localhost connections (not over network)

**Expected Resolution Time:** 10-30 minutes

### Issue 6: Browser Developer Console Errors

**Common Console Warnings (Safe to Ignore):**
```javascript
Download the React DevTools for a better development experience
[HMR] Waiting for update signal from WDS...
```

**Critical Errors (Require Fixing):**
```javascript
Failed to fetch /api/projects - NetworkError
Uncaught (in promise) TypeError: Failed to fetch
CORS error: Response not allowed by Access-Control-Allow-Origin
```

**Solutions for Critical Errors:**
- **Failed to fetch:** API not running or wrong API URL configured
- **CORS error:** Update API CORS settings in `apps/api/main.py`
- **Promise rejection:** React component error, check browser console for stack trace

## Success Checklist

Before proceeding to Tutorial 02, verify you can:

- [ ] Access web UI at http://localhost:8080 without errors
- [ ] Web UI loads in < 5 seconds
- [ ] Header shows "AI-Agent Framework" title
- [ ] Sidebar is visible (even if empty with no projects)
- [ ] Navigate to API docs at http://localhost:8000/docs
- [ ] Execute `/health` endpoint and receive 200 OK response
- [ ] Understand health response fields (status, docs_path, timestamp)
- [ ] Return to web UI successfully
- [ ] Open browser DevTools and see no critical errors
- [ ] API status indicator shows green (healthy)
- [ ] Understand all main UI components (sidebar, main content, header)
- [ ] Know where to find command panel, artifacts browser, proposal viewer
- [ ] Can identify keyboard shortcuts for common actions

**Estimated Total Time:** 10-15 minutes (25-45 minutes with troubleshooting)

**If all checkpoints passed:** ✅ Ready for Tutorial 02!

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Next:** [02 - Project Creation](02-project-creation.md)

**Related Tutorials:**
- [TUI Quick Start](../tui-basics/01-quick-start.md) - Command-line interface equivalent
- [Setup Guide](../shared/00-setup-guide.md) - Initial installation and configuration

**Additional Resources:**
- [API Documentation](http://localhost:8000/docs) - Interactive endpoint reference
- [Web UI Component Guide](../../architecture/web-ui-components.md) - Detailed React component docs
- [Docker Deployment Guide](../../deployment/docker-deployment.md) - Container architecture
- [Troubleshooting Guide](../ERROR-CATALOG.md) - Comprehensive error solutions
