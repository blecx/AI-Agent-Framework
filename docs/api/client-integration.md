# Client Integration Guide

**AI-Agent-Framework - API Client Development Guide**

This guide provides comprehensive information for developers building custom clients to integrate with the AI-Agent-Framework API.

---

## Table of Contents

1. [API Overview](#api-overview)
2. [API Endpoint Reference](#api-endpoint-reference)
3. [Authentication](#authentication)
4. [Request/Response Examples](#requestresponse-examples)
5. [Error Handling](#error-handling)
6. [Client Best Practices](#client-best-practices)
7. [Example Implementations](#example-implementations)
8. [Testing Your Client](#testing-your-client)

---

## API Overview

### Base URL

```
http://localhost:8000
```

For production deployments, use your configured domain:
```
https://api.your-domain.com
```

### API Documentation

Interactive documentation is available when the API is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### Content Type

All requests and responses use JSON:

```
Content-Type: application/json
```

### API Version

Current version: `1.0.0`

The API follows semantic versioning. Breaking changes will result in a major version bump.

---

## API Endpoint Reference

### Health Check

#### `GET /health`

Check API health and configuration status.

**Response:**
```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "docs_exists": true,
  "docs_is_git": true
}
```

**Status Codes:**
- `200 OK` - API is healthy

---

### Projects

#### `POST /projects`

Create a new project.

**Request Body:**
```json
{
  "key": "PROJ001",
  "name": "Website Redesign Project"
}
```

**Response:** `201 Created`
```json
{
  "key": "PROJ001",
  "name": "Website Redesign Project",
  "methodology": "ISO21500",
  "created_at": "2026-01-10T10:30:00Z",
  "updated_at": "2026-01-10T10:30:00Z"
}
```

**Validation:**
- `key`: Must be unique, alphanumeric with underscores/hyphens only
- `name`: Required, non-empty string

**Status Codes:**
- `201 Created` - Project created successfully
- `409 Conflict` - Project with this key already exists
- `422 Unprocessable Entity` - Invalid request data

---

#### `GET /projects`

List all projects.

**Response:** `200 OK`
```json
[
  {
    "key": "PROJ001",
    "name": "Website Redesign Project",
    "methodology": "ISO21500",
    "created_at": "2026-01-10T10:30:00Z",
    "updated_at": "2026-01-10T10:30:00Z"
  },
  {
    "key": "PROJ002",
    "name": "Mobile App Development",
    "methodology": "ISO21500",
    "created_at": "2026-01-10T11:00:00Z",
    "updated_at": "2026-01-10T11:00:00Z"
  }
]
```

**Status Codes:**
- `200 OK` - Success

---

#### `GET /projects/{project_key}/state`

Get project details and current state.

**Path Parameters:**
- `project_key`: Project identifier (e.g., "PROJ001")

**Response:** `200 OK`
```json
{
  "project_info": {
    "key": "PROJ001",
    "name": "Website Redesign Project",
    "methodology": "ISO21500",
    "created_at": "2026-01-10T10:30:00Z",
    "updated_at": "2026-01-10T10:35:00Z"
  },
  "artifacts": [
    {
      "path": "artifacts/project_charter.md",
      "name": "project_charter.md",
      "type": "file",
      "size": 2048
    },
    {
      "path": "artifacts/gap_assessment.md",
      "name": "gap_assessment.md",
      "type": "file",
      "size": 1536
    }
  ],
  "last_commit": {
    "hash": "a1b2c3d4",
    "message": "[PROJ001] Add project charter",
    "author": "ISO21500 API",
    "timestamp": "2026-01-10T10:35:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Project not found

---

### Commands (Propose/Apply Workflow)

#### `POST /projects/{project_key}/commands/propose`

Propose a command for review before applying.

**Path Parameters:**
- `project_key`: Project identifier

**Request Body:**
```json
{
  "command": "assess_gaps",
  "params": null
}
```

**Available Commands:**

1. **`assess_gaps`** - Analyze missing ISO 21500 artifacts
   ```json
   {
     "command": "assess_gaps"
   }
   ```

2. **`generate_artifact`** - Create/update a project document
   ```json
   {
     "command": "generate_artifact",
     "params": {
       "artifact_name": "project_charter.md",
       "artifact_type": "project_charter"
     }
   }
   ```

3. **`generate_plan`** - Generate project schedule and Gantt chart
   ```json
   {
     "command": "generate_plan"
   }
   ```

**Response:** `200 OK`
```json
{
  "proposal_id": "prop_1704897000_abc123",
  "assistant_message": "I've analyzed the project and identified 3 missing artifacts...",
  "file_changes": [
    {
      "path": "artifacts/gap_assessment.md",
      "operation": "create",
      "diff": "--- /dev/null\n+++ b/artifacts/gap_assessment.md\n@@ -0,0 +1,10 @@\n+# Gap Assessment\n+..."
    }
  ],
  "draft_commit_message": "[PROJ001] Add gap assessment artifact"
}
```

**Status Codes:**
- `200 OK` - Proposal generated successfully
- `404 Not Found` - Project not found
- `400 Bad Request` - Invalid command or parameters

---

#### `POST /projects/{project_key}/commands/apply/{proposal_id}`

Apply a previously proposed command, committing changes to Git.

**Path Parameters:**
- `project_key`: Project identifier
- `proposal_id`: Proposal ID from propose response

**Response:** `200 OK`
```json
{
  "commit_hash": "a1b2c3d4e5f6",
  "changed_files": [
    "artifacts/gap_assessment.md",
    "events/events.ndjson"
  ],
  "message": "Changes committed successfully"
}
```

**Status Codes:**
- `200 OK` - Changes applied successfully
- `404 Not Found` - Project or proposal not found
- `410 Gone` - Proposal has expired (older than 1 hour)

---

### Artifacts

#### `GET /projects/{project_key}/artifacts`

List all artifacts for a project.

**Path Parameters:**
- `project_key`: Project identifier

**Response:** `200 OK`
```json
[
  {
    "path": "artifacts/project_charter.md",
    "name": "project_charter.md",
    "type": "file",
    "size": 2048
  },
  {
    "path": "artifacts/schedule.md",
    "name": "schedule.md",
    "type": "file",
    "size": 3072
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Project not found

---

#### `GET /projects/{project_key}/artifacts/{artifact_path:path}`

Get artifact content.

**Path Parameters:**
- `project_key`: Project identifier
- `artifact_path`: Path to artifact (e.g., "artifacts/project_charter.md")

**Response:** `200 OK`
```json
{
  "path": "artifacts/project_charter.md",
  "content": "# Project Charter\n\n## Project Overview\n...",
  "type": "file"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Project or artifact not found

---

## Authentication

### Current Status

Authentication is **optional** in the current version. The API is designed to be deployed behind a secure reverse proxy or in a trusted environment.

### Future: API Key Authentication

API key authentication can be enabled by setting the `API_KEY` environment variable.

**Header:**
```
X-API-Key: your-api-key-here
```

**Example:**
```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/projects
```

**Python Example:**
```python
import httpx

headers = {"X-API-Key": "your-api-key-here"}
response = httpx.get("http://localhost:8000/projects", headers=headers)
```

### Future: OAuth2 / Bearer Token

For more advanced authentication scenarios:

**Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Request/Response Examples

### Complete Workflow: Create Project and Generate Artifacts

#### Step 1: Create Project

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "key": "WEBSITE",
    "name": "Website Redesign Project"
  }'
```

**Response:**
```json
{
  "key": "WEBSITE",
  "name": "Website Redesign Project",
  "methodology": "ISO21500",
  "created_at": "2026-01-10T10:30:00Z",
  "updated_at": "2026-01-10T10:30:00Z"
}
```

---

#### Step 2: Propose Gap Assessment

```bash
curl -X POST http://localhost:8000/projects/WEBSITE/commands/propose \
  -H "Content-Type: application/json" \
  -d '{
    "command": "assess_gaps"
  }'
```

**Response:**
```json
{
  "proposal_id": "prop_1704897000_abc123",
  "assistant_message": "I've analyzed your project structure...",
  "file_changes": [
    {
      "path": "artifacts/gap_assessment.md",
      "operation": "create",
      "diff": "--- /dev/null\n+++ b/artifacts/gap_assessment.md\n..."
    }
  ],
  "draft_commit_message": "[WEBSITE] Add gap assessment"
}
```

---

#### Step 3: Apply Proposal

```bash
curl -X POST http://localhost:8000/projects/WEBSITE/commands/apply/prop_1704897000_abc123
```

**Response:**
```json
{
  "commit_hash": "a1b2c3d4e5f6",
  "changed_files": [
    "artifacts/gap_assessment.md",
    "events/events.ndjson"
  ],
  "message": "Changes committed successfully"
}
```

---

#### Step 4: List Artifacts

```bash
curl http://localhost:8000/projects/WEBSITE/artifacts
```

**Response:**
```json
[
  {
    "path": "artifacts/gap_assessment.md",
    "name": "gap_assessment.md",
    "type": "file",
    "size": 1536
  }
]
```

---

#### Step 5: Get Artifact Content

```bash
curl http://localhost:8000/projects/WEBSITE/artifacts/artifacts/gap_assessment.md
```

**Response:**
```json
{
  "path": "artifacts/gap_assessment.md",
  "content": "# Gap Assessment\n\n## Missing Artifacts\n...",
  "type": "file"
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | OK | Successful GET/POST request |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid command or parameters |
| `404` | Not Found | Project or resource doesn't exist |
| `409` | Conflict | Resource already exists |
| `410` | Gone | Proposal has expired |
| `422` | Unprocessable Entity | Request validation failed |
| `500` | Internal Server Error | Server-side error |

### Example Error Responses

**Project Not Found:**
```json
{
  "detail": "Project INVALID not found"
}
```

**Project Already Exists:**
```json
{
  "detail": "Project PROJ001 already exists"
}
```

**Invalid Request:**
```json
{
  "detail": [
    {
      "loc": ["body", "key"],
      "msg": "string does not match regex '^[a-zA-Z0-9_-]+$'",
      "type": "value_error.str.regex"
    }
  ]
}
```

---

## Client Best Practices

### 1. Error Handling

Always check response status codes and handle errors gracefully:

```python
import httpx

def create_project(key: str, name: str):
    try:
        response = httpx.post(
            "http://localhost:8000/projects",
            json={"key": key, "name": name},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            print(f"Project {key} already exists")
        elif e.response.status_code == 422:
            print(f"Invalid project data: {e.response.json()}")
        else:
            print(f"Error: {e}")
        return None
    except httpx.RequestError as e:
        print(f"Connection error: {e}")
        return None
```

### 2. Retry Logic

Implement exponential backoff for transient failures:

```python
import time
import httpx

def api_call_with_retry(method, url, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            response = httpx.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 and attempt < max_retries - 1:
                # Server error, retry with exponential backoff
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Connection error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

### 3. Timeout Configuration

Set appropriate timeouts for different operations:

```python
import httpx

# Short timeout for health checks
health = httpx.get("http://localhost:8000/health", timeout=5)

# Long timeout for command proposals (LLM may take time)
proposal = httpx.post(
    "http://localhost:8000/projects/PROJ001/commands/propose",
    json={"command": "generate_artifact", "params": {...}},
    timeout=120  # 2 minutes for LLM generation
)

# Medium timeout for other operations
projects = httpx.get("http://localhost:8000/projects", timeout=30)
```

### 4. Rate Limiting Considerations

**Current Status:** No rate limiting implemented

**Best Practices:**
- Avoid making parallel requests for the same project (Git conflicts)
- Add delays between bulk operations
- Implement client-side rate limiting if needed

```python
import time

def bulk_create_projects(projects):
    results = []
    for project in projects:
        result = create_project(project["key"], project["name"])
        results.append(result)
        time.sleep(0.5)  # Avoid overwhelming the API
    return results
```

### 5. Connection Pooling

Use a single client instance for multiple requests:

```python
import httpx

class ISO21500Client:
    def __init__(self, base_url="http://localhost:8000"):
        self.client = httpx.Client(base_url=base_url, timeout=30)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.client.close()
    
    def list_projects(self):
        response = self.client.get("/projects")
        response.raise_for_status()
        return response.json()
    
    def create_project(self, key, name):
        response = self.client.post("/projects", json={"key": key, "name": name})
        response.raise_for_status()
        return response.json()

# Usage
with ISO21500Client() as client:
    projects = client.list_projects()
    new_project = client.create_project("PROJ001", "My Project")
```

### 6. Async Support

For high-performance applications, use async HTTP:

```python
import httpx
import asyncio

async def create_project_async(key: str, name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/projects",
            json={"key": key, "name": name}
        )
        response.raise_for_status()
        return response.json()

# Usage
async def main():
    project = await create_project_async("PROJ001", "My Project")
    print(project)

asyncio.run(main())
```

---

## Example Implementations

### Python (httpx)

See the reference implementation in `apps/tui/` directory.

**Key files:**
- `api_client.py` - HTTP client wrapper
- `commands/projects.py` - Project management commands
- `commands/propose.py` - Propose/apply workflow

### JavaScript/TypeScript (fetch)

```typescript
class ISO21500Client {
  constructor(private baseURL: string = 'http://localhost:8000') {}

  async listProjects(): Promise<Project[]> {
    const response = await fetch(`${this.baseURL}/projects`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async createProject(key: string, name: string): Promise<Project> {
    const response = await fetch(`${this.baseURL}/projects`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({key, name})
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async proposeCommand(
    projectKey: string,
    command: string,
    params?: any
  ): Promise<Proposal> {
    const response = await fetch(
      `${this.baseURL}/projects/${projectKey}/commands/propose`,
      {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command, params})
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async applyProposal(
    projectKey: string,
    proposalId: string
  ): Promise<ApplyResult> {
    const response = await fetch(
      `${this.baseURL}/projects/${projectKey}/commands/apply/${proposalId}`,
      {method: 'POST'}
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}
```

### Go

```go
package iso21500

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type Client struct {
    BaseURL    string
    HTTPClient *http.Client
}

type Project struct {
    Key        string `json:"key"`
    Name       string `json:"name"`
    Methodology string `json:"methodology"`
    CreatedAt  string `json:"created_at"`
    UpdatedAt  string `json:"updated_at"`
}

func NewClient(baseURL string) *Client {
    return &Client{
        BaseURL:    baseURL,
        HTTPClient: &http.Client{Timeout: 30 * time.Second},
    }
}

func (c *Client) ListProjects() ([]Project, error) {
    resp, err := c.HTTPClient.Get(c.BaseURL + "/projects")
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
    }

    var projects []Project
    if err := json.NewDecoder(resp.Body).Decode(&projects); err != nil {
        return nil, err
    }

    return projects, nil
}

func (c *Client) CreateProject(key, name string) (*Project, error) {
    body := map[string]string{"key": key, "name": name}
    jsonBody, _ := json.Marshal(body)

    resp, err := c.HTTPClient.Post(
        c.BaseURL+"/projects",
        "application/json",
        bytes.NewBuffer(jsonBody),
    )
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusCreated {
        return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
    }

    var project Project
    if err := json.NewDecoder(resp.Body).Decode(&project); err != nil {
        return nil, err
    }

    return &project, nil
}
```

---

## Testing Your Client

### 1. Start the API

```bash
docker compose up api
```

### 2. Basic Connectivity Test

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "docs_exists": true,
  "docs_is_git": true
}
```

### 3. Create Test Project

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"key": "TEST001", "name": "Test Project"}'
```

### 4. List Projects

```bash
curl http://localhost:8000/projects
```

### 5. Propose Command

```bash
curl -X POST http://localhost:8000/projects/TEST001/commands/propose \
  -H "Content-Type: application/json" \
  -d '{"command": "assess_gaps"}'
```

### 6. Apply Proposal

```bash
# Use proposal_id from previous response
curl -X POST http://localhost:8000/projects/TEST001/commands/apply/prop_XXXXXX_XXXXXX
```

### 7. List Artifacts

```bash
curl http://localhost:8000/projects/TEST001/artifacts
```

---

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Deployment Guide](../deployment/README.md)
- [TUI Client Source Code](../../apps/tui/)
- [WebUI Source Code](../../apps/web/)
- [API Source Code](../../apps/api/)

---

**Last Updated:** 2026-01-10  
**Version:** 1.0.0  
**Status:** Active
