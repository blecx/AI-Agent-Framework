# Cross-Repository Validation Guide

**Date:** 2026-01-14  
**Backend Commit:** e196bf8  
**API Version:** v1  
**Status:** Phase 1/3 Complete

## Overview

This guide provides instructions for validating the AI-Agent-Framework backend API contract with the AI-Agent-Framework-Client repository.

## Backend Setup

### Prerequisites
- Python 3.10+ (3.12 tested)
- Git
- Docker 28+ (optional)

### Local Development Setup

1. **Clone and setup backend:**
   ```bash
   git clone https://github.com/blecx/AI-Agent-Framework.git
   cd AI-Agent-Framework
   git checkout copilot/align-api-contract-phase-1  # Or main after merge
   ./setup.sh
   source .venv/bin/activate
   ```

2. **Configure environment:**
   ```bash
   mkdir -p projectDocs
   export PROJECT_DOCS_PATH=$(pwd)/projectDocs
   ```

3. **Start API server:**
   ```bash
   cd apps/api
   PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   ```

   API will be available at:
   - **Versioned API:** http://localhost:8000/api/v1/
   - **Legacy API:** http://localhost:8000/ (deprecated, backward compatible)
   - **OpenAPI Docs:** http://localhost:8000/docs

### Docker Setup

```bash
mkdir -p projectDocs
docker compose up --build
```

- **Web UI:** http://localhost:8080
- **API (versioned):** http://localhost:8000/api/v1/
- **API (legacy):** http://localhost:8000/

## Client Setup

### Prerequisites for Client Testing

1. **Environment Variables:**
   ```bash
   # Point to backend API
   export API_BASE_URL=http://localhost:8000/api/v1
   
   # Optional: API timeout
   export API_TIMEOUT=30
   ```

2. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "docs_path": "/path/to/projectDocs",
     "docs_exists": true,
     "docs_is_git": true,
     "api_version": "v1"
   }
   ```

## Validation Scenarios

### Scenario 1: Basic Health & Project Management

**Goal:** Verify basic API connectivity and project CRUD

```bash
# 1. Check API health
curl http://localhost:8000/api/v1/health

# 2. List projects (should be empty)
curl http://localhost:8000/api/v1/projects

# 3. Create a project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "key": "VALIDATE001",
    "name": "Validation Test Project"
  }'

# 4. Verify project appears in list
curl http://localhost:8000/api/v1/projects

# 5. Get project state
curl http://localhost:8000/api/v1/projects/VALIDATE001/state
```

**Expected:** All requests return 200/201 with valid JSON

---

### Scenario 2: Workflow State Management

**Goal:** Verify ISO 21500 workflow state transitions

```bash
# 1. Get initial workflow state
curl http://localhost:8000/api/v1/projects/VALIDATE001/workflow/state
# Expected: current_state = "initiating"

# 2. Get allowed transitions
curl http://localhost:8000/api/v1/projects/VALIDATE001/workflow/allowed-transitions
# Expected: allowed_transitions includes "planning"

# 3. Transition to planning phase
curl -X PATCH http://localhost:8000/api/v1/projects/VALIDATE001/workflow/state \
  -H "Content-Type: application/json" \
  -d '{
    "to_state": "planning",
    "actor": "test_user",
    "reason": "Validation test"
  }'

# 4. Verify state changed
curl http://localhost:8000/api/v1/projects/VALIDATE001/workflow/state
# Expected: current_state = "planning"
```

**Expected:** Valid state transitions accepted, invalid transitions rejected with 400

---

### Scenario 3: RAID Register Management

**Goal:** Verify RAID CRUD operations and filtering

```bash
# 1. List RAID items (should be empty)
curl http://localhost:8000/api/v1/projects/VALIDATE001/raid

# 2. Create a risk
curl -X POST http://localhost:8000/api/v1/projects/VALIDATE001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "risk",
    "title": "Test Risk",
    "description": "Risk for validation testing",
    "owner": "test_user@example.com",
    "priority": "high",
    "status": "open"
  }'

# 3. Create an issue
curl -X POST http://localhost:8000/api/v1/projects/VALIDATE001/raid \
  -H "Content-Type: application/json" \
  -d '{
    "type": "issue",
    "title": "Test Issue",
    "description": "Issue for validation testing",
    "owner": "test_user@example.com",
    "priority": "medium",
    "status": "open"
  }'

# 4. List all RAID items
curl http://localhost:8000/api/v1/projects/VALIDATE001/raid

# 5. Filter by type
curl "http://localhost:8000/api/v1/projects/VALIDATE001/raid?type=risk"

# 6. Filter by priority
curl "http://localhost:8000/api/v1/projects/VALIDATE001/raid?priority=high"

# 7. Get specific RAID item (use ID from creation response)
curl http://localhost:8000/api/v1/projects/VALIDATE001/raid/{raid_id}
```

**Expected:** All CRUD operations work, filtering returns correct results

---

### Scenario 4: Command Propose/Apply Workflow

**Goal:** Verify AI-assisted command execution with preview

```bash
# 1. Propose a command
curl -X POST http://localhost:8000/api/v1/projects/VALIDATE001/commands/propose \
  -H "Content-Type: application/json" \
  -d '{
    "command": "assess_gaps",
    "params": {}
  }'
# Note: May return 500 if LLM unavailable - this is expected behavior
# with fallback to templates

# 2. If proposal succeeds, apply it
curl -X POST http://localhost:8000/api/v1/projects/VALIDATE001/commands/apply \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "<proposal_id_from_step_1>"
  }'

# 3. List artifacts to see changes
curl http://localhost:8000/api/v1/projects/VALIDATE001/artifacts
```

**Expected:** Proposal returns file_changes preview, apply commits to git

---

### Scenario 5: Audit Trail & Governance

**Goal:** Verify audit events and governance metadata

```bash
# 1. Get audit events
curl http://localhost:8000/api/v1/projects/VALIDATE001/audit-events

# 2. Filter audit events by type
curl "http://localhost:8000/api/v1/projects/VALIDATE001/audit-events?event_type=workflow_state_changed"

# 3. Get governance metadata
curl http://localhost:8000/api/v1/projects/VALIDATE001/governance/metadata
```

**Expected:** Audit events include all actions performed, governance endpoint returns metadata

---

### Scenario 6: Backward Compatibility

**Goal:** Verify legacy unversioned endpoints still work

```bash
# All these should work identically to versioned endpoints:
curl http://localhost:8000/health
curl http://localhost:8000/projects
curl http://localhost:8000/projects/VALIDATE001/state
```

**Expected:** All unversioned endpoints return same data as versioned counterparts

## Client Integration Testing

### Python Client Example

```python
import requests

class APIClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def create_project(self, key, name):
        response = requests.post(
            f"{self.base_url}/projects",
            json={"key": key, "name": name}
        )
        response.raise_for_status()
        return response.json()

# Test
client = APIClient()
health = client.health_check()
print(f"API Version: {health['api_version']}")
assert health['api_version'] == 'v1'
assert health['status'] == 'healthy'

project = client.create_project("CLIENT001", "Client Test")
assert project['key'] == "CLIENT001"
print("✅ Client integration test passed!")
```

### JavaScript/TypeScript Client Example

```javascript
class APIClient {
  constructor(baseUrl = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }
  
  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }
  
  async createProject(key, name) {
    const response = await fetch(`${this.baseUrl}/projects`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({key, name})
    });
    if (!response.ok) throw new Error('Failed to create project');
    return response.json();
  }
}

// Test
const client = new APIClient();
const health = await client.healthCheck();
console.log(`API Version: ${health.api_version}`);
assert(health.api_version === 'v1');
assert(health.status === 'healthy');

const project = await client.createProject('CLIENT001', 'Client Test');
assert(project.key === 'CLIENT001');
console.log('✅ Client integration test passed!');
```

## Automated Test Suite

### Run Backend Integration Tests

```bash
cd AI-Agent-Framework
source .venv/bin/activate

# Run all integration tests
python3 -m pytest tests/integration/ -v

# Run specific test suites
python3 -m pytest tests/integration/test_versioned_api.py -v
python3 -m pytest tests/integration/test_core_api.py -v  # Backward compat
python3 -m pytest tests/integration/test_workflow_api.py -v
python3 -m pytest tests/integration/test_raid_api.py -v
```

Expected results:
- ✅ `test_versioned_api.py`: 25/25 passing
- ✅ `test_core_api.py`: 27/27 passing (backward compatibility)
- ✅ `test_workflow_api.py`: All passing
- ✅ `test_raid_api.py`: All passing

## Contract Validation Checklist

Use this checklist when validating client against backend:

### API Basics
- [ ] Health endpoint returns 200 with `api_version: "v1"`
- [ ] OpenAPI docs accessible at `/docs`
- [ ] CORS configured correctly for client origin

### Project Management
- [ ] Can create projects with valid key/name
- [ ] Can list all projects
- [ ] Can get project state with artifacts
- [ ] Project creation returns 409 for duplicates

### Workflow Management
- [ ] Can get workflow state (returns `initiating` for new projects)
- [ ] Can get allowed transitions for current state
- [ ] Can transition to valid states (e.g., initiating → planning)
- [ ] Invalid transitions rejected with 400 error

### RAID Register
- [ ] Can list RAID items (empty initially)
- [ ] Can create RAID items (risk, assumption, issue, dependency)
- [ ] Can get specific RAID item by ID
- [ ] Can update RAID items
- [ ] Can delete RAID items
- [ ] Filtering works (type, status, owner, priority)

### Command Execution
- [ ] Can propose commands (returns proposal with file_changes)
- [ ] Can apply proposals (commits to git)
- [ ] Proposals include: proposal_id, assistant_message, file_changes, draft_commit_message
- [ ] Apply returns: commit_hash, changed_files, message

### Artifacts
- [ ] Can list project artifacts
- [ ] Can get artifact content
- [ ] Artifact list includes versions metadata

### Governance & Audit
- [ ] Can get governance metadata
- [ ] Can get audit events
- [ ] Can filter audit events by type, actor, date range
- [ ] Audit events include all significant actions

### Error Handling
- [ ] 404 for nonexistent projects
- [ ] 400 for invalid request data
- [ ] 409 for duplicate resources
- [ ] Consistent error format: `{"detail": "message"}`

### Backward Compatibility
- [ ] Unversioned endpoints (`/projects`, `/health`) still work
- [ ] Both versioned and unversioned return same data (except api_version)

## Known Issues & Workarounds

### LLM Service Unavailable
**Issue:** Command propose may fail with 500 if LLM service not configured  
**Workaround:** Backend falls back to templates automatically, error is expected  
**Client Action:** Handle 500 gracefully, inform user to configure LLM if needed

### Proposals in Memory
**Issue:** Proposals cached in memory, lost on API restart  
**Workaround:** Apply proposals promptly after proposing  
**Client Action:** Show warning if API restarts between propose/apply

## Support & Coordination

### Backend Repository
- **Repo:** https://github.com/blecx/AI-Agent-Framework
- **Branch:** `copilot/align-api-contract-phase-1`
- **Commit:** e196bf8
- **Issues:** Report at https://github.com/blecx/AI-Agent-Framework/issues

### Client Repository  
- **Repo:** https://github.com/blecx/AI-Agent-Framework-Client
- **Integration:** Update `apiClient.ts` to use `/api/v1/` endpoints

### Cross-Repo Coordination
When making changes that affect both repos:
1. Open issue in backend repo describing API changes
2. Create matching issue in client repo referencing backend issue
3. Implement backend changes first (if backward compatible)
4. Test backend changes with validation scenarios above
5. Implement client changes referencing backend commit
6. Test end-to-end with both repos together

## Version History

| Date       | Version | Commit  | Changes |
|------------|---------|---------|---------|
| 2026-01-14 | v1      | e196bf8 | Initial API versioning, all endpoints under /api/v1/, backward compatibility maintained |

---

**Last Updated:** 2026-01-14  
**Maintained By:** Backend Team  
**For Questions:** See GitHub issues
