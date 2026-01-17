# Client Integration Guide

**Date:** 2026-01-14  
**Status:** Active  
**Last Updated:** 2026-01-14

## Overview

This guide is for developers who want to build custom clients that integrate with the AI-Agent-Framework API. Whether you're building a mobile app, desktop application, or automated workflow, this guide provides everything you need to consume the API effectively.

## CI Setup for AI-Agent-Framework-Client (API Integration Tests)

If your client repository (e.g. `AI-Agent-Framework-Client`) runs REST/API contract tests, CI needs a running API.

### Recommended approach (GitHub Actions)

Use the reusable workflow in this repo to:

1. Checkout the client repo (caller)
2. Checkout `blecx/AI-Agent-Framework` into `server/`
3. Start the API via `docker compose`
4. Wait for `/health`
5. Run the client test command with `API_BASE_URL=http://localhost:8000`

Example workflow in the client repo:

```yaml
name: Client CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  api-integration:
    uses: blecx/AI-Agent-Framework/.github/workflows/reusable-client-api-integration.yml@main
    with:
      # React/TypeScript/Vite client (Node toolchain)
      client_runtime: node
      node_version: '20'
      client_workdir: .
      client_install_command: npm ci
      client_lint_command: npm run lint
      client_build_command: npm run build
      # Use whatever your repo provides (e.g. npm run test:api)
      client_test_command: npm test
```

Notes:

- The API is started from `docker-compose.yml` in the server repo and exposed on `http://localhost:8000`.
- If your client tests use versioned endpoints, set `API_BASE_URL` to `http://localhost:8000/api/v1` in your test setup.

## API Overview

**Base URL:** `http://localhost:8000` (development)  
**Versioned Base URL:** `http://localhost:8000/api/v1` (recommended)  
**Production:** `https://api.your-domain.com/api/v1`  
**Protocol:** REST over HTTP/HTTPS  
**Content Type:** `application/json`  
**API Documentation:** `http://localhost:8000/docs` (FastAPI auto-generated Swagger UI)

### Core Principles

1. **API-First Design:** All functionality available via REST endpoints
2. **Propose/Apply Workflow:** Two-step process for command execution
3. **Stateless:** Each request is independent
4. **Standard HTTP:** Uses conventional HTTP methods and status codes
5. **JSON Everywhere:** All requests and responses use JSON
6. **Versioned API:** All endpoints available under `/api/v1/` prefix for stability

## API Versioning

**Current Version:** `v1`

### Versioned Endpoints (Recommended)

All endpoints are available under the `/api/v1/` prefix for API stability and future compatibility:

```bash
# Recommended: Use versioned endpoints
curl http://localhost:8000/api/v1/projects
curl http://localhost:8000/api/v1/health
```

### Backward Compatibility (Deprecated)

Legacy unversioned endpoints are still supported but **deprecated**:

```bash
# Deprecated: Will be removed in future versions
curl http://localhost:8000/projects
curl http://localhost:8000/health
```

**Migration Path:**

- New clients should use `/api/v1/` prefix from the start
- Existing clients should migrate to versioned endpoints
- Unversioned endpoints will be removed in a future major version (v2.0.0)

### Version Detection

Check API version via the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

Response includes `api_version` field:

```json
{
  "status": "healthy",
  "api_version": "v1",
  ...
}
```

## Authentication

### Current (MVP)

**No authentication required** for local development.

```bash
curl http://localhost:8000/projects
```

### Future (Production)

**API Key Authentication** via header:

```bash
curl -H "X-API-Key: your-api-key" \
     https://api.your-domain.com/projects
```

**Environment Variable:**

```bash
export API_KEY=your-api-key
```

## Client Workflow Contract Checklist

This section maps common client workflows to their required API endpoints, ensuring clients have a clear contract for integration.

### Core Client Workflows

#### 1. Application Initialization

**Goal:** Verify API is available and ready

| Workflow Step         | Endpoint         | Method | Required |
| --------------------- | ---------------- | ------ | -------- |
| Check API health      | `/api/v1/health` | GET    | ✅       |
| Verify git repository | `/api/v1/health` | GET    | ✅       |

**Expected Flow:**

```
1. GET /api/v1/health
   → Verify status = "healthy" and docs_is_git = true
```

---

#### 2. Project Management

**Goal:** Create and manage projects

| Workflow Step       | Endpoint                                | Method | Required |
| ------------------- | --------------------------------------- | ------ | -------- |
| List all projects   | `/api/v1/projects`                      | GET    | ✅       |
| Create new project  | `/api/v1/projects`                      | POST   | ✅       |
| Get project state   | `/api/v1/projects/{key}/state`          | GET    | ✅       |
| Get workflow state  | `/api/v1/projects/{key}/workflow/state` | GET    | ✅       |
| Transition workflow | `/api/v1/projects/{key}/workflow/state` | PATCH  | ✅       |

**Expected Flow:**

```
1. GET /api/v1/projects
   → Display project list
2. POST /api/v1/projects with {key, name}
   → Create new project
3. GET /api/v1/projects/{key}/state
   → Get project details and artifacts
4. GET /api/v1/projects/{key}/workflow/state
   → Display current workflow phase
```

---

#### 3. RAID Register Management

**Goal:** Manage risks, assumptions, issues, and dependencies

| Workflow Step        | Endpoint                                                  | Method | Required |
| -------------------- | --------------------------------------------------------- | ------ | -------- |
| List RAID items      | `/api/v1/projects/{key}/raid`                             | GET    | ✅       |
| Filter RAID items    | `/api/v1/projects/{key}/raid?type={type}&status={status}` | GET    | ✅       |
| Get RAID item detail | `/api/v1/projects/{key}/raid/{id}`                        | GET    | ✅       |
| Create RAID item     | `/api/v1/projects/{key}/raid`                             | POST   | ✅       |
| Update RAID item     | `/api/v1/projects/{key}/raid/{id}`                        | PUT    | ✅       |
| Delete RAID item     | `/api/v1/projects/{key}/raid/{id}`                        | DELETE | ✅       |

**Expected Flow:**

```
1. GET /api/v1/projects/{key}/raid
   → Display RAID register
2. POST /api/v1/projects/{key}/raid with {type, title, description, owner}
   → Create new RAID item
3. GET /api/v1/projects/{key}/raid/{id}
   → Show item details
4. PUT /api/v1/projects/{key}/raid/{id} with updates
   → Update RAID item
```

---

#### 4. Command Execution (Propose/Apply)

**Goal:** Execute AI-assisted commands with preview

| Workflow Step   | Endpoint                                  | Method | Required |
| --------------- | ----------------------------------------- | ------ | -------- |
| Propose command | `/api/v1/projects/{key}/commands/propose` | POST   | ✅       |
| Apply proposal  | `/api/v1/projects/{key}/commands/apply`   | POST   | ✅       |

**Expected Flow:**

```
1. POST /api/v1/projects/{key}/commands/propose
   with {command, params}
   → Get proposal with file_changes preview
2. User reviews file_changes
3. POST /api/v1/projects/{key}/commands/apply
   with {proposal_id}
   → Commit changes to git
```

---

#### 5. Artifact Management

**Goal:** View and manage project artifacts

| Workflow Step        | Endpoint                                  | Method | Required |
| -------------------- | ----------------------------------------- | ------ | -------- |
| List artifacts       | `/api/v1/projects/{key}/artifacts`        | GET    | ✅       |
| Get artifact content | `/api/v1/projects/{key}/artifacts/{path}` | GET    | ✅       |

**Expected Flow:**

```
1. GET /api/v1/projects/{key}/artifacts
   → Display artifact list
2. GET /api/v1/projects/{key}/artifacts/{path}
   → Display artifact content
```

---

#### 6. Governance & Compliance

**Goal:** Manage governance metadata and audit trail

| Workflow Step           | Endpoint                                                | Method | Required |
| ----------------------- | ------------------------------------------------------- | ------ | -------- |
| Get governance metadata | `/api/v1/projects/{key}/governance`                     | GET    | ✅       |
| Update governance       | `/api/v1/projects/{key}/governance`                     | PUT    | ✅       |
| Get audit events        | `/api/v1/projects/{key}/audit-events`                   | GET    | ✅       |
| Filter audit events     | `/api/v1/projects/{key}/audit-events?event_type={type}` | GET    | ✅       |

**Expected Flow:**

```
1. GET /api/v1/projects/{key}/governance
   → Display governance structure
2. GET /api/v1/projects/{key}/audit-events
   → Display audit trail
3. GET /api/v1/projects/{key}/audit-events?since={timestamp}
   → Show recent events
```

---

### Complete End-to-End Workflow

**Scenario:** Create project → Add RAID item → Transition workflow → View audit

```bash
# 1. Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"key": "PROJ001", "name": "My Project"}'

# 2. Verify initial workflow state
curl http://localhost:8000/api/v1/projects/PROJ001/workflow/state
# Expected: current_state = "initiating"

# 3. Create a RAID risk
curl -X POST http://localhost:8000/api/v1/projects/PROJ001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "risk",
    "title": "Budget overrun risk",
    "description": "Risk of exceeding budget",
    "owner": "pm@example.com",
    "priority": "high"
  }'

# 4. Transition to planning phase
curl -X PATCH http://localhost:8000/api/v1/projects/PROJ001/workflow/state \
  -H "Content-Type: application/json" \
  -d '{
    "to_state": "planning",
    "actor": "pm@example.com",
    "reason": "Initial planning"
  }'

# 5. View audit trail
curl http://localhost:8000/api/v1/projects/PROJ001/audit-events
# Expected: project_created, raid_item_created, workflow_state_changed events
```

---

### Contract Validation Checklist

Use this checklist to verify your client implementation:

- [ ] **Health Check**: Can verify API is running and healthy
- [ ] **Project Creation**: Can create projects with valid key format
- [ ] **Project Listing**: Can retrieve and display all projects
- [ ] **Project State**: Can get comprehensive project state
- [ ] **Workflow State**: Can view and transition workflow phases
- [ ] **RAID CRUD**: Can create, read, update, delete RAID items
- [ ] **RAID Filtering**: Can filter RAID by type, status, owner, priority
- [ ] **Command Propose**: Can propose commands and preview changes
- [ ] **Command Apply**: Can apply proposals and commit changes
- [ ] **Artifact Listing**: Can list project artifacts
- [ ] **Artifact Content**: Can retrieve artifact content
- [ ] **Governance Read**: Can view governance metadata
- [ ] **Audit Events**: Can retrieve and filter audit events
- [ ] **Error Handling**: Properly handles 400, 404, 409, 500 errors
- [ ] **API Versioning**: Uses `/api/v1/` prefix for all requests

---

## API Endpoints

### Health & Status

#### GET / - Basic Health Check

**Description:** Check if API is running

**Request:**

```bash
curl http://localhost:8000/
```

**Response:**

```json
{
  "status": "healthy",
  "service": "ISO 21500 Project Management AI Agent",
  "version": "1.0.0"
}
```

**Status Codes:**

- `200 OK` - Service is healthy

---

#### GET /api/v1/health - Detailed Health Check (Versioned)

**Description:** Get detailed health information (versioned endpoint - recommended)

**Request:**

```bash
curl http://localhost:8000/api/v1/health
```

**Response:**

```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "docs_exists": true,
  "docs_is_git": true,
  "api_version": "v1"
}
```

**Status Codes:**

- `200 OK` - Service is healthy

**Note:** Legacy unversioned `/health` endpoint is still available but deprecated.

---

### Project Management

#### GET /api/v1/projects - List Projects

**Description:** Get a list of all projects

**Request:**

```bash
curl http://localhost:8000/api/v1/projects
```

**Response:**

```json
[
  {
    "key": "PROJECT001",
    "name": "My Project",
    "methodology": "ISO21500",
    "created_at": "2026-01-10T00:00:00Z",
    "updated_at": "2026-01-10T12:30:00Z"
  },
  {
    "key": "PROJECT002",
    "name": "Another Project",
    "methodology": "ISO21500",
    "created_at": "2026-01-09T00:00:00Z",
    "updated_at": "2026-01-10T10:15:00Z"
  }
]
```

**Status Codes:**

- `200 OK` - Projects retrieved successfully
- `500 Internal Server Error` - Server error

---

#### POST /api/v1/projects - Create Project

**Description:** Create a new project

**Request:**

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "key": "PROJECT001",
    "name": "My Project"
  }'
```

**Request Body:**

```json
{
  "key": "PROJECT001", // Required: Alphanumeric, underscore, hyphen only
  "name": "My Project" // Required: Human-readable name
}
```

**Response:**

```json
{
  "key": "PROJECT001",
  "name": "My Project",
  "methodology": "ISO21500",
  "created_at": "2026-01-10T00:00:00Z",
  "updated_at": "2026-01-10T00:00:00Z"
}
```

**Status Codes:**

- `201 Created` - Project created successfully
- `400 Bad Request` - Invalid request body
- `409 Conflict` - Project already exists
- `500 Internal Server Error` - Server error

**Validation:**

- `key` must match pattern: `^[a-zA-Z0-9_-]+$`
- `key` must be unique
- `name` is required

---

#### GET /api/v1/projects/{key}/state - Get Project State

**Description:** Get complete project state including artifacts and last commit

**Request:**

```bash
curl http://localhost:8000/api/v1/projects/PROJECT001/state
```

**Response:**

```json
{
  "project_info": {
    "key": "PROJECT001",
    "name": "My Project",
    "methodology": "ISO21500",
    "created_at": "2026-01-10T00:00:00Z",
    "updated_at": "2026-01-10T12:30:00Z"
  },
  "artifacts": [
    {
      "path": "artifacts/project_charter.md",
      "name": "project_charter.md",
      "type": "markdown",
      "versions": [
        {
          "version": "current",
          "date": "2026-01-10T12:30:00Z"
        }
      ]
    }
  ],
  "last_commit": {
    "hash": "a1b2c3d4",
    "message": "[PROJECT001] Add project charter",
    "author": "AI Agent",
    "timestamp": "2026-01-10T12:30:00Z"
  }
}
```

**Status Codes:**

- `200 OK` - State retrieved successfully
- `404 Not Found` - Project not found
- `500 Internal Server Error` - Server error

---

### Command Execution (Propose/Apply Pattern)

#### POST /api/v1/projects/{key}/commands/propose - Propose Command

**Description:** Generate a proposal for command execution with preview of changes

**Request:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/PROJECT001/commands/propose \
  -H "Content-Type: application/json" \
  -d '{
    "command": "generate_artifact",
    "params": {
      "artifact_type": "project_charter"
    }
  }'
```

**Request Body:**

```json
{
  "command": "assess_gaps", // Required: Command name
  "params": {
    // Optional: Command parameters
    "artifact_type": "project_charter"
  }
}
```

**Available Commands:**

- `assess_gaps` - Analyze missing ISO 21500 artifacts
- `generate_artifact` - Create or update project document
- `generate_plan` - Generate project schedule with Mermaid gantt chart

**Response:**

```json
{
  "proposal_id": "prop_abc123",
  "assistant_message": "I will create a project charter based on ISO 21500 standards...",
  "file_changes": [
    {
      "path": "artifacts/project_charter.md",
      "operation": "create",
      "diff": "--- /dev/null\n+++ b/artifacts/project_charter.md\n@@ -0,0 +1,50 @@\n+# Project Charter\n+\n+## Project Name\n+My Project\n..."
    }
  ],
  "draft_commit_message": "[PROJECT001] Add project charter"
}
```

**Response Fields:**

- `proposal_id` - Unique identifier for this proposal (required for apply)
- `assistant_message` - Human-readable explanation of changes
- `file_changes` - Array of file modifications with unified diffs
- `draft_commit_message` - Suggested git commit message

**File Change Operations:**

- `create` - New file
- `modify` - Update existing file
- `delete` - Remove file

**Status Codes:**

- `200 OK` - Proposal generated successfully
- `400 Bad Request` - Invalid command or parameters
- `404 Not Found` - Project not found
- `500 Internal Server Error` - Server error

---

#### POST /api/v1/projects/{key}/commands/apply - Apply Proposal

**Description:** Apply a previously generated proposal and commit changes to git

**Request:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/PROJECT001/commands/apply \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "prop_abc123"
  }'
```

**Request Body:**

```json
{
  "proposal_id": "prop_abc123" // Required: ID from propose response
}
```

**Response:**

```json
{
  "commit_hash": "a1b2c3d4e5f6",
  "changed_files": ["artifacts/project_charter.md"],
  "message": "Changes applied and committed successfully"
}
```

**Status Codes:**

- `200 OK` - Proposal applied successfully
- `400 Bad Request` - Invalid proposal ID
- `404 Not Found` - Project or proposal not found
- `500 Internal Server Error` - Server error

**Important Notes:**

- Proposals are cached in memory (lost on API restart)
- Apply within reasonable time after propose
- Each proposal can only be applied once
- Audit log entry created automatically

---

### Artifact Management

#### GET /api/v1/projects/{key}/artifacts - List Artifacts

**Description:** Get list of all artifacts in project's artifacts folder

**Request:**

```bash
curl http://localhost:8000/api/v1/projects/PROJECT001/artifacts
```

**Response:**

```json
[
  {
    "path": "artifacts/project_charter.md",
    "name": "project_charter.md",
    "type": "markdown",
    "versions": [
      {
        "version": "current",
        "date": "2026-01-10T12:30:00Z"
      }
    ]
  },
  {
    "path": "artifacts/stakeholder_register.md",
    "name": "stakeholder_register.md",
    "type": "markdown",
    "versions": [
      {
        "version": "current",
        "date": "2026-01-10T13:45:00Z"
      }
    ]
  }
]
```

**Status Codes:**

- `200 OK` - Artifacts retrieved successfully
- `404 Not Found` - Project not found
- `500 Internal Server Error` - Server error

---

#### GET /api/v1/projects/{key}/artifacts/{path} - Get Artifact Content

**Description:** Retrieve content of a specific artifact

**Request:**

```bash
curl http://localhost:8000/api/v1/projects/PROJECT001/artifacts/project_charter.md
```

**Response:**

```markdown
# Project Charter

## Project Name

My Project

## Project Purpose

...
```

**Content Types:**

- `text/markdown` - For .md files
- `text/plain` - For other files

**Status Codes:**

- `200 OK` - Artifact content retrieved
- `404 Not Found` - Project or artifact not found
- `500 Internal Server Error` - Server error

---

## Error Handling

### Error Response Format

All errors return a consistent JSON structure:

```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning               | Action                        |
| ---- | --------------------- | ----------------------------- |
| 200  | OK                    | Request successful            |
| 201  | Created               | Resource created successfully |
| 400  | Bad Request           | Fix request parameters        |
| 404  | Not Found             | Resource doesn't exist        |
| 409  | Conflict              | Resource already exists       |
| 500  | Internal Server Error | Retry or contact support      |

### Error Handling Best Practices

**1. Always Check Status Code:**

```python
response = requests.post(url, json=data)
if response.status_code == 200:
    data = response.json()
else:
    error = response.json()
    print(f"Error: {error['detail']}")
```

**2. Implement Retry Logic for 5xx Errors:**

```python
import time

def api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code < 500:
            return response
        time.sleep(2 ** attempt)  # Exponential backoff
    raise Exception("Max retries exceeded")
```

**3. Validate Input Before Sending:**

```python
import re

def validate_project_key(key):
    if not re.match(r'^[a-zA-Z0-9_-]+$', key):
        raise ValueError("Invalid project key format")
```

**4. Handle Network Failures:**

```python
import requests
from requests.exceptions import ConnectionError, Timeout

try:
    response = requests.get(url, timeout=30)
except (ConnectionError, Timeout) as e:
    print(f"Network error: {e}")
    # Fallback or retry logic
```

## Example Requests & Responses

### Complete Workflow Example (Using Versioned API)

**Step 1: Create Project**

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"key": "DEMO001", "name": "Demo Project"}'
```

Response:

```json
{
  "key": "DEMO001",
  "name": "Demo Project",
  "methodology": "ISO21500",
  "created_at": "2026-01-10T14:00:00Z",
  "updated_at": "2026-01-10T14:00:00Z"
}
```

---

**Step 2: Assess Gaps**

```bash
curl -X POST http://localhost:8000/api/v1/projects/DEMO001/commands/propose \
  -H "Content-Type: application/json" \
  -d '{"command": "assess_gaps"}'
```

Response:

```json
{
  "proposal_id": "prop_xyz789",
  "assistant_message": "I have analyzed the project and identified missing ISO 21500 artifacts...",
  "file_changes": [
    {
      "path": "reports/gap_assessment.md",
      "operation": "create",
      "diff": "--- /dev/null\n+++ b/reports/gap_assessment.md\n..."
    }
  ],
  "draft_commit_message": "[DEMO001] Add gap assessment report"
}
```

---

**Step 3: Apply Changes**

```bash
curl -X POST http://localhost:8000/api/v1/projects/DEMO001/commands/apply \
  -H "Content-Type: application/json" \
  -d '{"proposal_id": "prop_xyz789"}'
```

Response:

```json
{
  "commit_hash": "abc123def456",
  "changed_files": ["reports/gap_assessment.md"],
  "message": "Changes applied and committed successfully"
}
```

---

**Step 4: Generate Artifact**

```bash
curl -X POST http://localhost:8000/api/v1/projects/DEMO001/commands/propose \
  -H "Content-Type: application/json" \
  -d '{
    "command": "generate_artifact",
    "params": {"artifact_type": "project_charter"}
  }'
```

Response:

```json
{
  "proposal_id": "prop_charter123",
  "assistant_message": "I will create a project charter...",
  "file_changes": [
    {
      "path": "artifacts/project_charter.md",
      "operation": "create",
      "diff": "..."
    }
  ],
  "draft_commit_message": "[DEMO001] Add project charter"
}
```

---

**Step 5: Apply Artifact**

```bash
curl -X POST http://localhost:8000/api/v1/projects/DEMO001/commands/apply \
  -H "Content-Type: application/json" \
  -d '{"proposal_id": "prop_charter123"}'
```

---

**Step 6: List Artifacts**

```bash
curl http://localhost:8000/api/v1/projects/DEMO001/artifacts
```

Response:

```json
[
  {
    "path": "artifacts/project_charter.md",
    "name": "project_charter.md",
    "type": "markdown",
    "versions": [{ "version": "current", "date": "2026-01-10T14:05:00Z" }]
  }
]
```

---

**Step 7: Get Artifact Content**

```bash
curl http://localhost:8000/projects/DEMO001/artifacts/project_charter.md
```

Response: (Markdown content of the charter)

## Client Implementation Examples

### Python Client (Versioned API)

```python
import requests
from typing import Dict, List, Optional

class AIAgentClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_version: str = "v1"):
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.session = requests.Session()

    def _get_api_url(self, path: str) -> str:
        """Construct versioned API URL."""
        return f"{self.base_url}/api/{self.api_version}{path}"

    def create_project(self, key: str, name: str) -> Dict:
        """Create a new project."""
        response = self.session.post(
            self._get_api_url("/projects"),
            json={"key": key, "name": name}
        )
        response.raise_for_status()
        return response.json()

    def list_projects(self) -> List[Dict]:
        """List all projects."""
        response = self.session.get(self._get_api_url("/projects"))
        response.raise_for_status()
        return response.json()

    def propose_command(self, project_key: str, command: str,
                       params: Optional[Dict] = None) -> Dict:
        """Propose a command execution."""
        response = self.session.post(
            self._get_api_url(f"/projects/{project_key}/commands/propose"),
            json={"command": command, "params": params or {}}
        )
        response.raise_for_status()
        return response.json()

    def apply_proposal(self, project_key: str, proposal_id: str) -> Dict:
        """Apply a proposal."""
        response = self.session.post(
            self._get_api_url(f"/projects/{project_key}/commands/apply"),
            json={"proposal_id": proposal_id}
        )
        response.raise_for_status()
        return response.json()

    def list_artifacts(self, project_key: str) -> List[Dict]:
        """List project artifacts."""
        response = self.session.get(
            self._get_api_url(f"/projects/{project_key}/artifacts")
        )
        response.raise_for_status()
        return response.json()

# Usage
client = AIAgentClient()

# Create project
project = client.create_project("DEMO001", "Demo Project")
print(f"Created: {project['key']}")

# Propose command
proposal = client.propose_command("DEMO001", "assess_gaps")
print(f"Proposal ID: {proposal['proposal_id']}")

# Apply changes
result = client.apply_proposal("DEMO001", proposal['proposal_id'])
print(f"Committed: {result['commit_hash']}")

# List artifacts
artifacts = client.list_artifacts("DEMO001")
print(f"Artifacts: {len(artifacts)}")
```

### JavaScript Client (Versioned API)

```javascript
class AIAgentClient {
  constructor(baseUrl = 'http://localhost:8000', apiVersion = 'v1') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiVersion = apiVersion;
  }

  _getApiUrl(path) {
    return `${this.baseUrl}/api/${this.apiVersion}${path}`;
  }

  async createProject(key, name) {
    const response = await fetch(this._getApiUrl('/projects'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, name }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async listProjects() {
    const response = await fetch(this._getApiUrl('/projects'));
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async proposeCommand(projectKey, command, params = {}) {
    const response = await fetch(
      this._getApiUrl(`/projects/${projectKey}/commands/propose`),
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, params }),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async applyProposal(projectKey, proposalId) {
    const response = await fetch(
      this._getApiUrl(`/projects/${projectKey}/commands/apply`),
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proposal_id: proposalId }),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async listArtifacts(projectKey) {
    const response = await fetch(
      this._getApiUrl(`/projects/${projectKey}/artifacts`),
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }
}

// Usage
const client = new AIAgentClient();

(async () => {
  // Create project
  const project = await client.createProject('DEMO001', 'Demo Project');
  console.log(`Created: ${project.key}`);

  // Propose command
  const proposal = await client.proposeCommand('DEMO001', 'assess_gaps');
  console.log(`Proposal ID: ${proposal.proposal_id}`);

  // Apply changes
  const result = await client.applyProposal('DEMO001', proposal.proposal_id);
  console.log(`Committed: ${result.commit_hash}`);

  // List artifacts
  const artifacts = await client.listArtifacts('DEMO001');
  console.log(`Artifacts: ${artifacts.length}`);
})();
```

### Go Client

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

type AIAgentClient struct {
    BaseURL string
    Client  *http.Client
}

func NewClient(baseURL string) *AIAgentClient {
    return &AIAgentClient{
        BaseURL: baseURL,
        Client:  &http.Client{},
    }
}

func (c *AIAgentClient) CreateProject(key, name string) (map[string]interface{}, error) {
    data := map[string]string{"key": key, "name": name}
    jsonData, _ := json.Marshal(data)

    resp, err := c.Client.Post(
        c.BaseURL+"/projects",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    return result, nil
}

func main() {
    client := NewClient("http://localhost:8000")

    project, err := client.CreateProject("DEMO001", "Demo Project")
    if err != nil {
        panic(err)
    }

    fmt.Printf("Created: %s\n", project["key"])
}
```

## Best Practices

### 1. Use Propose/Apply Workflow

Always use the two-step propose/apply pattern:

**✅ Correct:**

```python
# Step 1: Propose
proposal = client.propose_command("PROJECT001", "generate_artifact")

# Step 2: Review (your code here)
print(f"Changes: {len(proposal['file_changes'])} files")

# Step 3: Apply
result = client.apply_proposal("PROJECT001", proposal['proposal_id'])
```

**❌ Incorrect:**

```python
# Skipping propose step (not possible with this API)
```

### 2. Handle Async Operations

Commands may take time to generate proposals:

```python
import time

def propose_with_timeout(client, project_key, command, timeout=30):
    start = time.time()
    try:
        proposal = client.propose_command(project_key, command)
        return proposal
    except Timeout:
        if time.time() - start > timeout:
            raise Exception("Proposal generation timeout")
        raise
```

### 3. Implement Retry Logic

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session
```

### 4. Validate Input

```python
import re

def validate_project_key(key: str) -> bool:
    """Validate project key matches API requirements."""
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, key))

# Use before API call
if not validate_project_key(user_input):
    raise ValueError("Invalid project key format")
```

### 5. Cache Project State

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedClient(AIAgentClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._cache_ttl = timedelta(minutes=5)

    def get_project_state(self, project_key: str) -> Dict:
        """Get project state with caching."""
        cache_key = f"state:{project_key}"
        if cache_key in self._cache:
            cached_at, data = self._cache[cache_key]
            if datetime.now() - cached_at < self._cache_ttl:
                return data

        # Fetch fresh data
        response = self.session.get(
            f"{self.base_url}/projects/{project_key}/state"
        )
        response.raise_for_status()
        data = response.json()

        # Update cache
        self._cache[cache_key] = (datetime.now(), data)
        return data
```

### 6. Handle Large Responses

For artifacts with large content:

```python
def get_artifact_stream(client, project_key, artifact_path):
    """Stream large artifacts instead of loading into memory."""
    url = f"{client.base_url}/projects/{project_key}/artifacts/{artifact_path}"
    response = client.session.get(url, stream=True)
    response.raise_for_status()

    with open(f"downloaded_{artifact_path}", 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

## Rate Limiting (Future)

When rate limiting is implemented:

**Headers:**

- `X-RateLimit-Limit` - Max requests per window
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Window reset time (Unix timestamp)

**Response when rate limited:**

```json
{
  "detail": "Rate limit exceeded. Retry after 60 seconds."
}
```

**Status Code:** `429 Too Many Requests`

## Troubleshooting

### Connection Refused

**Problem:** Cannot connect to API

**Solutions:**

1. Check API is running: `curl http://localhost:8000/health`
2. Verify port in docker-compose.yml
3. Check firewall rules
4. Verify base URL in client configuration

### CORS Errors (Browser)

**Problem:** Browser shows CORS error

**Solution:** API already configured for CORS. Check:

1. API is running
2. Web UI is served from correct origin
3. Browser developer console for specific error

### Proposal Not Found

**Problem:** Apply fails with "proposal not found"

**Solutions:**

1. Proposals are cached in memory (lost on restart)
2. Apply immediately after propose
3. Check proposal_id is correct

### Timeout Errors

**Problem:** Request times out

**Solutions:**

1. Increase client timeout (default: 30s)
2. Check LLM service is responding
3. Use templates-only mode if LLM unavailable

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Deployment Guide](../deployment/multi-component-guide.md)
- [ADR-0004: Client Separation Strategy](../adr/0004-separate-client-application.md)
- [API Auto-Generated Docs](http://localhost:8000/docs) (when running)

## Support

**Issues:** Open an issue on GitHub  
**API Documentation:** http://localhost:8000/docs  
**Source Code:** https://github.com/blecx/AI-Agent-Framework

---

**Classification:** Public (API documentation)  
**Retention:** Indefinite  
**Last Reviewed:** 2026-01-10
