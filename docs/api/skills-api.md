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

**Endpoint**: `GET /api/v1/agents/{agent_id}/skills`

**Parameters**:
- `agent_id` (path): Unique agent identifier (currently maintained for API consistency; skills list is global)

**Response**: `200 OK`

```json
{
  "skills": [
    {
      "name": "memory",
      "version": "1.0.0",
      "description": "Manage agent short-term and long-term memory",
      "enabled": true
    },
    {
      "name": "planning",
      "version": "1.0.0",
      "description": "Generate multi-step plans from goals and constraints",
      "enabled": true
    },
    {
      "name": "learning",
      "version": "1.0.0",
      "description": "Record and learn from agent experiences",
      "enabled": true
    }
  ],
  "total": 3
}
```

**Example**:

```bash
curl -X GET http://localhost:8000/api/v1/agents/agent_001/skills
```

---

### Get Agent Memory

Retrieve current memory state for an agent.

**Endpoint**: `GET /api/v1/agents/{agent_id}/skills/memory?memory_type={type}`

**Parameters**:
- `agent_id` (path): Unique agent identifier
- `memory_type` (query): Memory type to retrieve - "short_term" or "long_term"

**Response**: `200 OK`

```json
{
  "success": true,
  "message": "Memory retrieved successfully",
  "timestamp": "2026-01-14T15:30:00Z",
  "data": {
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
}
```

**Example**:

```bash
curl -X GET "http://localhost:8000/api/v1/agents/agent_001/skills/memory?memory_type=short_term"
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
  "memory_type": "short_term",
  "data": {
    "current_task": "new task",
    "status": "active"
  }
}
```

The `memory_type` field must be either "short_term" or "long_term". Provided values are merged with existing memory (not replaced).

**Response**: `200 OK`

Returns the updated memory state (same format as GET).

**Example**:

```bash
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/memory \
  -H "Content-Type: application/json" \
  -d '{
    "memory_type": "short_term",
    "data": {"current_task": "analyzing data"}
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
  "success": true,
  "message": "Plan generated successfully",
  "timestamp": "2026-01-14T15:00:00Z",
  "data": {
    "agent_id": "agent_001",
    "goal": "Deploy application to production",
    "steps": [
      {
        "step": 1,
        "action": "Analyze Requirements",
        "description": "Analyze and clarify requirements for: Deploy application to production",
        "dependencies": [],
        "status": "pending"
      },
      {
        "step": 2,
        "action": "Design Approach",
        "description": "Design solution approach considering constraints",
        "dependencies": [1],
        "status": "pending"
      },
      {
        "step": 3,
        "action": "Implement Solution",
        "description": "Implement solution for: Deploy application to production",
        "dependencies": [2],
        "status": "pending"
      },
      {
        "step": 4,
        "action": "Test and Validate",
        "description": "Test implementation and validate against requirements",
        "dependencies": [3],
        "status": "pending"
      },
      {
        "step": 5,
        "action": "Verify Constraints",
        "description": "Verify all constraints are met: Must complete within 2 weeks, Budget limited to $5000, Zero downtime required",
        "dependencies": [4],
        "status": "pending"
      }
    ],
    "created_at": "2026-01-14T15:00:00Z"
  },
  "metadata": {
    "constraints": [
      "Must complete within 2 weeks",
      "Budget limited to $5000",
      "Zero downtime required"
    ]
  }
}
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
  "context": "Deploying application to production",
  "action": "Used Kubernetes rolling deployment strategy with 3 replicas",
  "outcome": "Deployment succeeded in 180 seconds with zero downtime",
  "feedback": "Rolling strategy worked well. Consider increasing health check intervals.",
  "tags": ["deployment", "kubernetes", "production"]
}
```

- `context` (required): Context or situation of the experience
- `action` (required): Action that was taken
- `outcome` (required): What happened as a result
- `feedback` (optional): Reflection or evaluation
- `tags` (optional): Tags for categorization

**Response**: `200 OK`

```json
{
  "success": true,
  "message": "Experience recorded successfully",
  "timestamp": "2026-01-14T15:30:00Z",
  "data": {
    "agent_id": "agent_001",
    "experience_id": "550e8400-e29b-41d4-a716-446655440000",
    "recorded_at": "2026-01-14T15:30:00Z"
  }
}
```

**Example**:

```bash
curl -X POST http://localhost:8000/api/v1/agents/agent_001/skills/learn \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Code review for PR #42",
    "action": "Reviewed 12 files for potential issues",
    "outcome": "Found 3 issues in 25 minutes",
    "feedback": "Found critical issues efficiently",
    "tags": ["code_review", "quality_check"]
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
    "memory_type": "short_term",
    "data": {"current_step": 1, "plan_id": "plan_123"}
  }'

# Agent 2 retrieves agent 1's memory for collaboration
curl -X GET "http://localhost:8000/api/v1/agents/agent_001/skills/memory?memory_type=short_term"

# Agent 2 records experience
curl -X POST http://localhost:8000/api/v1/agents/agent_002/skills/learn \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Collaborating with agent_001 on customer data processing",
    "action": "Retrieved agent_001 memory and coordinated task execution",
    "outcome": "Successfully coordinated work with agent_001",
    "tags": ["collaboration", "multi-agent"]
  }'
```

### Long-Running Task with Memory

```bash
# Store intermediate state
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/agents/worker_001/skills/memory \
    -H "Content-Type: application/json" \
    -d "{
      \"memory_type\": \"short_term\",
      \"data\": {
        \"iteration\": $i,
        \"checkpoint\": \"step_$i\"
      }
    }"
  
  # ... do work ...
  
  sleep 1
done

# Retrieve final state
curl -X GET "http://localhost:8000/api/v1/agents/worker_001/skills/memory?memory_type=short_term"
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
