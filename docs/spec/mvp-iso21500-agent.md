# MVP Specification: ISO 21500 Project Management AI Agent v1

**Version:** 1.0.0  
**Date:** 2026-01-09  
**Status:** Implemented

## Executive Summary

The ISO 21500 Project Management AI Agent is a containerized web application that helps project managers create, manage, and maintain project documentation following ISO 21500 standards. The system uses AI to generate project artifacts, assess compliance gaps, and maintain project schedules while ensuring full audit traceability and compliance with security standards.

## System Architecture

### Overview

The system consists of two containerized services:

1. **FastAPI Backend** - Handles business logic, LLM integration, git operations, and API endpoints
2. **React/Vite Frontend** - Provides modern web UI for project management operations

Both containers communicate over Docker networking and share access to a mounted `/projectDocs` directory that contains all project documentation as a separate git repository.

### Component Details

#### Backend (FastAPI)

**Technology Stack:**
- Python 3.12
- FastAPI framework
- GitPython for version control operations
- Jinja2 for template rendering
- Pydantic for data validation

**Core Services:**

1. **Git Manager Service** (`services/git_manager.py`)
   - Initializes and manages project document repositories
   - Auto-initializes git if `/projectDocs` is not a repository
   - Creates commits for all document changes
   - Provides project state and artifact listing
   - Generates unified diffs for change proposals

2. **LLM Service** (`services/llm_service.py`)
   - HTTP adapter for OpenAI-compatible APIs
   - Configurable via `/config/llm.json`
   - Default configuration for LM Studio on `http://host.docker.internal:1234/v1`
   - Graceful fallback to template-based generation when LLM unavailable
   - Supports streaming responses

3. **Command Service** (`services/command_service.py`)
   - Orchestrates propose/apply workflow
   - Renders prompt templates with Jinja2
   - Calls LLM service for content generation
   - Generates file changes and diffs
   - Applies changes with git commits
   - Logs audit events

**API Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/health` | GET | System health status |
| `/projects` | GET | List all projects |
| `/projects` | POST | Create new project |
| `/projects/{key}/state` | GET | Get project state |
| `/projects/{key}/commands/propose` | POST | Propose document changes |
| `/projects/{key}/commands/apply` | POST | Apply and commit changes |
| `/projects/{key}/artifacts` | GET | List artifacts |
| `/projects/{key}/artifacts/{path}` | GET | Get artifact content |

#### Frontend (React/Vite)

**Technology Stack:**
- React 18
- Vite build tool
- Modern JavaScript (ES6+)
- CSS modules for styling
- Nginx for production serving

**Core Components:**

1. **ProjectSelector** - Project creation and selection UI
2. **ProjectView** - Main project interface with tabs
3. **CommandPanel** - Three command cards for user actions
4. **ProposalModal** - Diff viewer and approval interface
5. **ArtifactsList** - Document browser and previewer

**User Workflows:**

1. **Project Creation**: User creates project → Backend creates folder structure → Git initialized
2. **Command Execution**: User selects command → Fills parameters → Clicks "Propose Changes"
3. **Review Proposal**: Backend generates content → Shows diff → User reviews changes
4. **Apply Changes**: User clicks "Apply & Commit" → Backend writes files → Git commits → User sees success

#### Docker Configuration

**Container 1: API** (`docker/api/Dockerfile`)
- Based on `python:3.12-slim`
- Installs git, Python dependencies
- Mounts `/projectDocs` volume
- Optionally mounts `/config/llm.json`
- Exposes port 8000

**Container 2: Web** (`docker/web/Dockerfile`)
- Multi-stage build: Node.js build → Nginx serve
- Builds React app with Vite
- Nginx configuration with API proxy
- Exposes port 80 (mapped to 8080 on host)

**Docker Compose** (`docker-compose.yml`)
- Orchestrates both containers
- Shared network for inter-container communication
- Volume mounts for persistent storage
- Health checks and restart policies

## Core Features

### 1. Separate Project Documents Git Repository

**Location:** `/projectDocs` (mounted volume)

**Features:**
- Auto-initialized as git repository on first run
- Completely separate from code repository
- Never committed to code repo (enforced via `.gitignore`)
- Full version history for all project documents
- Each project stored in its own subdirectory

**Directory Structure:**
```
projectDocs/
├── .git/                          # Git repository
├── PROJECT001/
│   ├── project.json              # Project metadata
│   ├── artifacts/                # Generated documents
│   │   ├── project_charter.md
│   │   ├── schedule.md
│   │   └── ...
│   ├── reports/                  # Gap assessments
│   │   └── gap_assessment.md
│   └── events/
│       └── events.ndjson         # Audit log
└── PROJECT002/
    └── ...
```

**Rationale:** See [ADR-0001](../adr/0001-docs-repo-mounted-git.md)

### 2. LLM HTTP Adapter with JSON Configuration

**Configuration File:** `configs/llm.json` (or `configs/llm.default.json` for defaults)

**Configuration Schema:**
```json
{
  "provider": "lmstudio",           // Provider identifier
  "base_url": "http://...",         // API endpoint URL
  "api_key": "lm-studio",           // API key or token
  "model": "local-model",           // Model name
  "temperature": 0.7,               // Sampling temperature
  "max_tokens": 4096,               // Max response tokens
  "timeout": 120                    // Request timeout (seconds)
}
```

**Supported Providers:**
- LM Studio (default)
- OpenAI API
- Azure OpenAI
- Ollama (with OpenAI compatibility)
- LocalAI
- Any OpenAI-compatible endpoint

**Features:**
- Environment variable overrides supported
- Graceful fallback when LLM unavailable
- HTTP client with retry logic
- Streaming support for long responses

**Rationale:** See [ADR-0002](../adr/0002-llm-http-adapter-json-config.md)

### 3. Propose/Apply Workflow (Review-Before-Commit)

**Workflow Steps:**

1. **Propose Phase:**
   - User selects command and provides parameters
   - System renders prompt template
   - LLM generates content (or fallback to templates)
   - System creates file change proposals
   - System generates unified diffs
   - Returns `proposal_id` for tracking

2. **Review Phase:**
   - Frontend displays proposed changes
   - Shows unified diff with additions/deletions
   - User reviews all changes before applying
   - User can cancel or proceed

3. **Apply Phase:**
   - User approves changes
   - System writes files to `/projectDocs`
   - System creates git commit with descriptive message
   - System logs audit event
   - Returns commit hash for verification

**Benefits:**
- No accidental overwrites
- User always reviews before committing
- Full audit trail
- Rollback via git history
- Compliance with change management policies

**Rationale:** See [ADR-0003](../adr/0003-propose-apply-before-commit.md)

### 4. Template System

**Prompt Templates** (`templates/prompts/iso21500/`)
- Jinja2 templates for LLM prompts
- Parameterized with project context
- Supports conditional logic and loops
- Three templates for three commands:
  - `assess_gaps.j2` - Gap analysis prompt
  - `generate_artifact.j2` - Artifact generation prompt
  - `generate_plan.j2` - Schedule generation prompt

**Output Templates** (`templates/output/iso21500/`)
- Markdown templates for fallback content
- Used when LLM unavailable
- Structured format for consistency
- Three templates matching commands:
  - `gap_report.md` - Gap assessment template
  - `project_charter.md` - Charter template
  - `project_plan.md` - Schedule with Mermaid gantt

### 5. Audit Logging

**Log Format:** NDJSON (Newline Delimited JSON)

**Log Location:** `projectDocs/{PROJECT_KEY}/events/events.ndjson`

**Event Schema:**
```json
{
  "timestamp": "2026-01-09T12:00:00Z",
  "event_type": "command_proposed|command_applied",
  "command": "assess_gaps",
  "proposal_id": "uuid",
  "user": "system",
  "prompt_hash": "sha256:...",
  "content_hash": "sha256:...",
  "commit_hash": "abc123...",
  "files_changed": ["path1", "path2"]
}
```

**Compliance Features:**
- **By default**: Only hashes stored (no sensitive content)
- **Optional**: Full content logging via `log_content=true` parameter
- **Immutable**: Append-only log file
- **Traceable**: Links proposals to commits
- **Auditable**: Full history of all operations

### 6. ISO 21500 Commands

**Command 1: Assess Gaps**
- **Purpose:** Analyze project against ISO 21500 standards
- **Output:** Gap assessment report identifying missing artifacts
- **Location:** `reports/gap_assessment.md`

**Command 2: Generate Artifact**
- **Purpose:** Create specific project management documents
- **Parameters:** `artifact_name`, `artifact_type`
- **Output:** Generated artifact (e.g., `project_charter.md`)
- **Location:** `artifacts/{artifact_name}`
- **Supported Types:**
  - Project Charter
  - Stakeholder Register
  - Scope Statement
  - WBS (Work Breakdown Structure)
  - Project Schedule
  - Budget Plan
  - Quality Plan
  - Risk Register
  - Communication Plan
  - Procurement Plan

**Command 3: Generate Plan**
- **Purpose:** Create project schedule with timeline
- **Output:** Schedule document with Mermaid gantt chart
- **Location:** `artifacts/schedule.md`

## Compliance & Security

### EU AI Act Considerations

**Transparency:**
- System purpose clearly documented
- AI-generated content marked as such
- Human review required before committing (propose/apply)
- Full audit trail of AI usage

**Risk Mitigation:**
- No autonomous decision-making (human-in-the-loop)
- Limited to document generation (low-risk use case)
- No personal data processing by default
- Configurable to exclude sensitive data

### ISO 27001 Alignment

**Access Control:**
- No authentication in MVP (container-level security assumed)
- Future: Role-based access control

**Information Security:**
- Secrets management via mounted config files
- No API keys in code
- `.gitignore` prevents accidental secret commits
- Project documents in separate repository

**Audit and Logging:**
- All operations logged with timestamps
- Hashes stored by default (privacy by design)
- Optional full content logging for specific use cases
- Immutable audit trail

**Data Classification:**
- Project documents: Confidential (customer-managed)
- Audit logs: Internal (hashes only by default)
- Templates: Public
- Source code: Public

### Security Best Practices

1. **Secrets Management:**
   - API keys via mounted files or environment variables
   - Never commit secrets to git
   - Regular rotation of credentials

2. **Prompt Logging:**
   - Disabled by default
   - Enable only when required for debugging
   - Review logs for sensitive data before sharing

3. **Content Redaction:**
   - User responsible for reviewing content before applying
   - No automatic PII detection in MVP
   - Future: Configurable redaction patterns

4. **Retention:**
   - Project documents retained per customer policy
   - Audit logs retained for compliance period
   - Git history provides point-in-time recovery

## Technical Specifications

### System Requirements

**Minimum:**
- Docker 20.10+
- Docker Compose 2.0+
- 2 GB RAM
- 1 GB disk space

**Recommended:**
- Docker 24.0+
- Docker Compose 2.20+
- 4 GB RAM
- 10 GB disk space
- LM Studio or OpenAI API access

### Performance Characteristics

**Expected Response Times:**
- Project creation: < 1 second
- Command proposal (with LLM): 5-30 seconds (depends on LLM)
- Command proposal (fallback): < 1 second
- Command apply: < 2 seconds
- Artifact listing: < 1 second

**Scalability:**
- Designed for single-user or small team use
- Concurrent project support: Unlimited (file-based)
- Concurrent command execution: Sequential per project (git locking)

### API Specifications

**OpenAPI/Swagger Documentation:**
- Available at `http://localhost:8000/docs`
- Interactive API explorer
- Request/response schemas
- Authentication: None (MVP)

**Request Format:**
- JSON request bodies
- RESTful conventions
- Standard HTTP status codes

**Response Format:**
- JSON responses
- Consistent error structure
- Detailed error messages

### Deployment Options

**Docker Compose (Default):**
```bash
docker compose up --build
```

**Local Development:**
- Backend: `uvicorn main:app --reload`
- Frontend: `npm run dev`

**Production Considerations:**
- Add reverse proxy (Nginx, Traefik)
- Enable HTTPS/TLS
- Add authentication layer
- Configure backup for `/projectDocs`
- Monitor logs and health endpoints

## Future Enhancements (Post-MVP)

### High Priority
1. User authentication and authorization
2. Multi-user collaboration features
3. Real-time updates with WebSockets
4. Advanced diff viewer (side-by-side)
5. Markdown rendering in artifact preview

### Medium Priority
6. Search and filter for artifacts
7. Export to PDF/Word formats
8. Custom template creation UI
9. Integration with external project management tools
10. Metrics and reporting dashboard

### Low Priority
11. Mobile-responsive UI improvements
12. Offline mode support
13. Plugin system for extensibility
14. Multi-language support
15. Advanced AI features (summarization, recommendations)

## Testing Strategy

### MVP Testing (Completed)
- [x] Manual testing of all API endpoints
- [x] Manual testing of all UI workflows
- [x] Git operations verification
- [x] LLM integration testing (with and without LLM)
- [x] Docker build and deployment testing

### Future Testing
- [ ] Unit tests for all services
- [ ] Integration tests for API endpoints
- [ ] E2E tests for UI workflows
- [ ] Performance testing
- [ ] Security testing
- [ ] Compliance validation

## Documentation

### Available Documentation
- [README.md](../../README.md) - Comprehensive overview and usage guide
- [QUICKSTART.md](../../QUICKSTART.md) - Step-by-step setup guide
- [SUMMARY.md](../../SUMMARY.md) - Implementation status and testing results
- [ADR-0001](../adr/0001-docs-repo-mounted-git.md) - Separate docs repository decision
- [ADR-0002](../adr/0002-llm-http-adapter-json-config.md) - LLM adapter configuration
- [ADR-0003](../adr/0003-propose-apply-before-commit.md) - Propose/apply workflow
- [Chat Context Guide](../howto/chat-context-in-repo.md) - Context storage best practices

## Success Criteria

### Functional Requirements
- [x] Create projects with git initialization
- [x] Execute three core commands (assess_gaps, generate_artifact, generate_plan)
- [x] Propose/review/apply workflow functional
- [x] Unified diff generation and display
- [x] Git commit with proper messages
- [x] Audit logging with NDJSON format
- [x] LLM integration with fallback

### Non-Functional Requirements
- [x] Docker deployment working
- [x] No secrets in code repository
- [x] Separate project documents repository
- [x] Comprehensive documentation
- [x] Compliance-ready logging (hashes by default)
- [x] User-friendly web interface

### Quality Attributes
- [x] **Reliability:** System works with and without LLM
- [x] **Maintainability:** Clear code structure and documentation
- [x] **Usability:** Intuitive UI with clear workflows
- [x] **Security:** No secrets in code, configurable logging
- [x] **Compliance:** Audit trail, human review, transparency

## Conclusion

The MVP v1 of the ISO 21500 Project Management AI Agent is complete and meets all specified requirements. The system provides a solid foundation for AI-assisted project management with strong compliance features and extensibility for future enhancements.

**Project Repository:** https://github.com/blecx/AI-Agent-Framework

**Version:** 1.0.0 MVP  
**Release Date:** 2026-01-09  
**Status:** Production Ready
