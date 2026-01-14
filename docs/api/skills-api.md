# Skills API Documentation

Complete API reference for AI Agent cognitive skills endpoints.

## Base URL

- **Versioned (recommended)**: `/api/v1/agents`
- **Legacy (deprecated)**: `/agents`

All examples use the versioned endpoints.

## Authentication

Currently no authentication is required. Future versions will support API keys and OAuth.

## Endpoints

### List Available Skills

Get metadata for all registered skills.

**Endpoint**: `GET /api/v1/agents/skills`

**Response**: `200 OK`

```json
[
  {
    "name": "memory",
    "version": "1.0.0",
    "description": "Manage agent short-term and long-term memory",
    "input_schema": { ... },
    "output_schema": { ... }
  },
  {
    "name": "planning",
    "version": "1.0.0",
    "description": "Generate multi-step plans from goals and constraints",
    "input_schema": { ... },
    "output_schema": { ... }
  },
  {
    "name": "learning",
    "version": "1.0.0",
    "description": "Record and learn from agent experiences",
    "input_schema": { ... },
    "output_schema": { ... }
  }
]
```

**Example**:

```bash
curl -X GET http://localhost:8000/api/v1/agents/skills
```

---

### Get Agent Memory

Retrieve current memory state for an agent.

**Endpoint**: `GET /api/v1/agents/{agent_id}/skills/memory`

**Parameters**:
- `agent_id` (path): Unique agent identifier

**Response**: `200 OK`

```json
{
  "agent_id": "agent_001",
  "short_term": {
    "current_task": "processing documents",
    "iteration": 5,
    "active_connections": ["db1", "cache"]
  },
  "long_term": {
    "learned_patterns": ["pattern_a", "pattern_b"],
    "user_preferences": {
      "language": "en",
      "format": "json"
    }
  },
  "metadata": {
    "created_at": "2026-01-14T10:00:00Z",
    "updated_at": "2026-01-14T15:30:00Z"
  }
}
```

**Example**:

```bash
curl -X GET http://localhost:8000/api/v1/agents/agent_001/skills/memory
```

---

### Update Agent Memory

Update (merge) agent memory state.

**Endpoint**: `POST /api/v1/agents/{agent_id}/skills/memory`

**Parameters**:
- `agent_id` (path): Unique agent identifier

**Request Body**:

```json
{
  "short_term": {
    "current_task": "new task",
    "status": "active"
  },
  "long_term": {
    "learned_fact": "important information"
  }
}
```

Both fields are optional. Provided values are merged with existing memory (not replaced).

**Response**: `200 OK`

Returns the updated memory state (same format as GET).

**Example**:

```bash
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/memory \
  -H "Content-Type: application/json" \
  -d '{
    "short_term": {"current_task": "analyzing data"},
    "long_term": {"data_source": "database_x"}
  }'
```

---

### Create a Plan

Generate a multi-step plan for achieving a goal.

**Endpoint**: `POST /api/v1/agents/{agent_id}/skills/plan`

**Parameters**:
- `agent_id` (path): Unique agent identifier

**Request Body**:

```json
{
  "goal": "Deploy application to production",
  "constraints": [
    "Must complete within 2 weeks",
    "Budget limited to $5000",
    "Zero downtime required"
  ],
  "context": {
    "environment": "production",
    "team_size": 3,
    "existing_infrastructure": "AWS"
  }
}
```

- `goal` (required): Clear description of what to achieve
- `constraints` (optional): List of constraints to consider
- `context` (optional): Additional context for planning

**Response**: `200 OK`

```json
{
  "agent_id": "agent_001",
  "goal": "Deploy application to production",
  "steps": [
    {
      "step_number": 1,
      "title": "Analyze Requirements",
      "description": "Analyze and clarify requirements for: Deploy application to production",
      "estimated_duration": "30m",
      "dependencies": [],
      "status": "pending"
    },
    {
      "step_number": 2,
      "title": "Design Approach",
      "description": "Design solution approach considering constraints",
      "estimated_duration": "1h",
      "dependencies": [1],
      "status": "pending"
    },
    {
      "step_number": 3,
      "title": "Implement Solution",
      "description": "Implement solution for: Deploy application to production",
      "estimated_duration": "2h",
      "dependencies": [2],
      "status": "pending"
    },
    {
      "step_number": 4,
      "title": "Test and Validate",
      "description": "Test implementation and validate against requirements",
      "estimated_duration": "1h",
      "dependencies": [3],
      "status": "pending"
    },
    {
      "step_number": 5,
      "title": "Verify Constraints",
      "description": "Verify all constraints are met: Must complete within 2 weeks, Budget limited to $5000, Zero downtime required",
      "estimated_duration": "30m",
      "dependencies": [4],
      "status": "pending"
    }
  ],
  "estimated_total_duration": "5h",
  "created_at": "2026-01-14T15:00:00Z"
}
```

**Example**:

```bash
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/plan \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Implement user authentication",
    "constraints": ["Must use OAuth 2.0", "2 days timeline"]
  }'
```

---

### Record Learning Experience

Record an experience for the agent to learn from.

**Endpoint**: `POST /api/v1/agents/{agent_id}/skills/learn`

**Parameters**:
- `agent_id` (path): Unique agent identifier

**Request Body**:

```json
{
  "experience": {
    "input": {
      "action": "deploy",
      "method": "kubernetes",
      "parameters": {
        "replicas": 3,
        "strategy": "rolling"
      }
    },
    "outcome": {
      "success": true,
      "duration_seconds": 180,
      "metrics": {
        "downtime": 0,
        "error_rate": 0.001
      }
    },
    "feedback": "Deployment was smooth. Rolling strategy worked well with no downtime.",
    "context": {
      "environment": "production",
      "timestamp": "2026-01-14T15:00:00Z",
      "team": "ops"
    }
  }
}
```

- `input` (required): What led to this experience (action, parameters, context)
- `outcome` (required): What happened (results, metrics, success/failure)
- `feedback` (optional): Human or AI evaluation of the outcome
- `context` (optional): Additional contextual information

**Response**: `200 OK`

```json
{
  "agent_id": "agent_001",
  "experience_id": "550e8400-e29b-41d4-a716-446655440000",
  "recorded_at": "2026-01-14T15:30:00Z",
  "message": "Experience recorded successfully"
}
```

**Example**:

```bash
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/learn \
  -H "Content-Type: application/json" \
  -d '{
    "experience": {
      "input": {"task": "code_review", "files": 12},
      "outcome": {"issues_found": 3, "time_minutes": 25},
      "feedback": "Found critical issues efficiently"
    }
  }'
```

---

## Error Responses

### 400 Bad Request

Invalid input or validation failure.

```json
{
  "detail": "goal is required"
}
```

### 404 Not Found

Agent or resource not found.

```json
{
  "detail": "Agent agent_999 not found"
}
```

### 422 Unprocessable Entity

Request body validation failed (Pydantic validation).

```json
{
  "detail": [
    {
      "loc": ["body", "goal"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

Skill execution error or server error.

```json
{
  "detail": "Failed to execute skill: internal error"
}
```

---

## Usage Examples

### Multi-Agent Workflow

```bash
# Agent 1 creates a plan
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/plan \
  -H "Content-Type: application/json" \
  -d '{"goal": "Process customer data"}'

# Agent 1 stores working memory
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/memory \
  -H "Content-Type: application/json" \
  -d '{
    "short_term": {"current_step": 1, "plan_id": "plan_123"}
  }'

# Agent 2 retrieves agent 1's memory for collaboration
curl -X GET http://localhost:8000/api/v1/agents/agent_001/skills/memory

# Agent 2 records experience
curl -X POST http://localhost:8000/api/v1/agents/agent_002/skills/learn \
  -H "Content-Type: application/json" \
  -d '{
    "experience": {
      "input": {"collaborated_with": "agent_001"},
      "outcome": {"success": true}
    }
  }'
```

### Long-Running Task with Memory

```bash
# Store intermediate state
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/agents/worker_001/skills/memory \
    -H "Content-Type: application/json" \
    -d "{
      \"short_term\": {
        \"iteration\": $i,
        \"checkpoint\": \"step_$i\"
      }
    }"
  
  # ... do work ...
  
  sleep 1
done

# Retrieve final state
curl -X GET http://localhost:8000/api/v1/agents/worker_001/skills/memory
```

---

## Interactive API Documentation

The framework provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Try endpoints directly in the browser
- Download OpenAPI specification

---

## Rate Limiting

Currently no rate limiting is enforced. Production deployments should implement rate limiting at the reverse proxy or API gateway level.

---

## Versioning

API versioning follows semantic versioning:

- **v1**: Current stable version
- Breaking changes will result in a new version (v2, v3, etc.)
- Legacy unversioned endpoints will be deprecated in a future major version

Always use versioned endpoints (`/api/v1/...`) in production code.

---

## SDKs and Client Libraries

Currently, you can use any HTTP client. Future releases may include:

- Python SDK
- JavaScript/TypeScript SDK
- Go SDK

For now, use standard HTTP clients like `requests` (Python), `fetch` (JavaScript), or `curl`.
