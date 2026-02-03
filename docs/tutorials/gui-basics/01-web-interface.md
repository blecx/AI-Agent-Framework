# GUI Web Interface Basics

**Duration:** 5 minutes | **Difficulty:** Beginner | **Interface:** Web GUI

## Overview

Get familiar with the AI-Agent Framework's web interface. Learn navigation, UI components, and basic operations through the browser.

## Learning Objectives

- Access and navigate the web UI
- Understand UI layout and components
- Use browser developer tools
- Navigate between projects
- Access API documentation

## Prerequisites

- Docker Compose running (`docker compose up -d`)
- Web browser (Chrome, Firefox, Safari recommended)
- No coding knowledge required

## Steps

### Step 1: Access Web Interface

Open browser and navigate to:
```
http://localhost:8080
```

**Expected:** Project selector UI loads with "AI-Agent Framework" header

✅ **Checkpoint:** Web UI loads without errors

### Step 2: UI Layout Overview

The web interface has three main sections:

**1. Sidebar (Left)**
- Projects list
- Create new project button
- Project selector dropdown

**2. Main Content (Center)**
- Command panel
- Artifacts browser
- Project details
- Proposal viewer

**3. Header (Top)**
- Application title
- API status indicator
- Settings/config access

### Step 3: Navigate to API Documentation

Click the "API Docs" link or navigate to:
```
http://localhost:8000/docs
```

**Expected:** Interactive Swagger UI with all API endpoints

✅ **Checkpoint:** API documentation loads

### Step 4: Check API Health Status

In API docs, find `/health` endpoint:
1. Click "GET /health"
2. Click "Try it out"
3. Click "Execute"

**Expected Response:**
```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "timestamp": "2026-02-03T..."
}
```

✅ **Checkpoint:** API is healthy

### Step 5: Return to Web UI

Navigate back to `http://localhost:8080`

## UI Components Reference

| Component | Purpose | Location |
|-----------|---------|----------|
| ProjectSelector | Choose/create projects | Sidebar |
| CommandPanel | Execute commands | Main content |
| ArtifactsList | Browse generated files | Main content |
| ProposalModal | Review/apply proposals | Overlay |

## What You've Learned

✅ Access web UI at localhost:8080  
✅ Navigate UI layout  
✅ Access API documentation  
✅ Check API health status  
✅ Understand main UI components

## Next Steps

1. **[Tutorial 02: Project Creation](02-project-creation.md)** - Create projects via GUI (10 min)
2. **[TUI Quick Start](../tui-basics/01-quick-start.md)** - Command-line alternative (5 min)

## TUI Equivalent

See [TUI Quick Start](../tui-basics/01-quick-start.md) for command-line version.

## Troubleshooting

**Web UI not loading:**
- Verify Docker running: `docker ps`
- Check port 8080 not in use
- Check logs: `docker compose logs web`

**API Docs not accessible:**
- Verify API container running
- Check port 8000 not in use
- Check logs: `docker compose logs api`

## Success Checklist

- [ ] Access web UI at localhost:8080
- [ ] UI loads without errors
- [ ] Navigate to API docs
- [ ] Execute health check
- [ ] Understand UI layout

---

**Tutorial Series:** [GUI Basics](../README.md#gui-basics) | **Next:** [02 - Project Creation](02-project-creation.md)
