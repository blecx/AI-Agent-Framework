# Master Plan for AI-Agent-Framework Solution (Merged)

**Date Created:** January 11, 2026  
**Source:** Consolidated from ISO 21500 project planning discussions and repository metadata  
**Repository:** blecx/AI-Agent-Framework

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [ISO 21500 Artifact Workflow](#iso-21500-artifact-workflow)
3. [System Architecture](#system-architecture)
4. [Repository Structure](#repository-structure)
5. [Implementation Phases](#implementation-phases)
6. [Development Workflow](#development-workflow)
7. [Quality Assurance](#quality-assurance)
8. [Appendix A: Repository Metadata](#appendix-a-repository-metadata)

---

## Executive Summary

This document consolidates the master plan for the AI-Agent-Framework, an ISO 21500/21502-inspired project management system that uses AI agents to generate, validate, and audit project artifacts.

**Core Vision:**
- Provide a predictable, testable "artifact workflow spine" for project management
- Enable AI-assisted artifact generation with human oversight and control
- Implement a propose/review/apply pattern for all changes with full traceability
- Support both WebUI and TUI/CLI interfaces for maximum flexibility

**Key Components:**
- **Backend:** FastAPI (Python 3.10+) with Git-based document storage
- **Frontend:** React/Vite with modern component architecture
- **Deployment:** Docker Compose (2 containers: API + Web/nginx)
- **AI Integration:** OpenAI-compatible LLM adapter with graceful fallback to templates
- **Storage:** Separate Git repository for project documents (projectDocs/)

---

## ISO 21500 Artifact Workflow

This repository implements an **ISO 21500 / ISO 21502** inspired workflow that drives project work through explicit artifacts.

### Guiding Principles

1. **Artifact-first:** Work is driven by the creation and evolution of explicit project artifacts
2. **Thin-slice delivery:** Every step delivers a minimal, end-to-end usable slice
3. **Blueprint-driven:** Blueprints declare what artifacts exist, required fields, and relationships
4. **AI-assisted, human-controlled:** AI drafts; humans approve and merge
5. **Testable workflow:** Every workflow capability must be covered by functional tests and E2E flows

### ISO Workflow Spine

The system supports six core workflow stages:

#### 1. Projects
- Create/select a project
- Configure metadata (name, sponsor, manager, dates, constraints)
- Initialize project workspace and Git repository

#### 2. Artifacts
- Generate and manage project artifacts (charter, PMP, RAID, schedule baseline)
- Track versions and status (draft / reviewed / approved)
- Maintain artifact relationships and dependencies

#### 3. Templates
- Provide structured templates for artifacts (fields, schema, required sections)
- Enable validation for completeness
- Support Jinja2 templating for dynamic content

#### 4. Blueprints
- Define collections of templates and rules representing a process or methodology
- Drive UI navigation and required artifact sets
- Enforce organizational standards and compliance

#### 5. Proposals
- All changes to artifacts occur via proposals (AI-generated or human-authored)
- Proposals include diffs and rationale
- Accepted proposals update artifacts with full audit trail

#### 6. Audit
- Automated checks across artifacts (consistency, required fields, cross-references)
- Audit results are actionable (errors/warnings) and can open issues
- Compliance reporting for governance and oversight

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
├─────────────────────────────────────────────────────────────┤
│  React/Vite WebUI (Port 8080)  │  TUI/CLI (Optional)        │
└─────────────────┬───────────────┴────────────────────────────┘
                  │
                  │ HTTP/REST API
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Routers   │  │   Services   │  │   Models         │   │
│  │  - Projects │  │  - Git Mgr   │  │  - Pydantic      │   │
│  │  - Commands │  │  - LLM Svc   │  │  - Schemas       │   │
│  │  - Artifacts│  │  - Cmd Svc   │  │  - Validation    │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ File I/O & Git Operations
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              projectDocs/ (Separate Git Repo)                │
├─────────────────────────────────────────────────────────────┤
│  └── [PROJECT_KEY]/                                          │
│      ├── artifacts/                                          │
│      ├── metadata.json                                       │
│      └── audit.log                                           │
└─────────────────────────────────────────────────────────────┘
```

### Backend Components (FastAPI)

**Core Services:**
- **Git Manager** (`services/git_manager.py`, 193 lines)
  - Manages project document repository initialization and operations
  - Handles commits, history, and version tracking
  - Provides diff generation for proposals

- **LLM Service** (`services/llm_service.py`, 94 lines)
  - OpenAI-compatible HTTP adapter
  - Configurable via JSON (default: LM Studio on localhost:1234)
  - Graceful fallback to templates when LLM unavailable

- **Command Service** (`services/command_service.py`, 291 lines)
  - Orchestrates the propose/apply workflow
  - Handles artifact generation, gap assessment, and planning
  - Integrates templates, LLM, and Git operations

**API Routers:**
- `routers/projects.py` (78 lines) - Project CRUD operations
- `routers/commands.py` (71 lines) - Command execution endpoints
- `routers/artifacts.py` (48 lines) - Artifact retrieval and management

**Models:**
- `models.py` (69 lines) - Pydantic models for request/response validation

### Frontend Components (React/Vite)

**Key Components:**
- **ProjectSelector** - Create/select projects with metadata configuration
- **ProjectView** - Main workspace with artifact navigation
- **CommandPanel** - Execute three core commands (assess_gaps, generate_artifact, generate_plan)
- **ProposalModal** - Review AI-generated proposals with diff view
- **ArtifactsList** - Browse and manage project artifacts

**Build Configuration:**
- Uses `rolldown-vite@7.2.5` for fast builds (~120ms)
- Vite config proxies `/api` to backend
- ESLint for code quality (one acceptable warning in ProjectView.jsx)

### LLM Integration

**Default Configuration (LM Studio):**
```json
{
  "endpoint": "http://localhost:1234/v1/chat/completions",
  "model": "local-model",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

**Fallback Behavior:**
- If LLM endpoint unavailable, system uses pre-built templates
- No error thrown to user; seamless degradation
- Templates provide baseline functionality without AI enhancement

### Storage Architecture

**Project Documents (projectDocs/):**
- **CRITICAL:** Separate Git repository, NEVER committed to code repo
- Auto-initialized by API on first startup
- Each project stored in `[PROJECT_KEY]/` subdirectory
- Full Git history for audit trail and version control

**Configuration:**
- `configs/llm.json` - User-specific LLM configuration (gitignored)
- `configs/llm.default.json` - Default template for new installations
- `templates/prompts/iso21500/*.j2` - Jinja2 prompt templates
- `templates/output/iso21500/*.md` - Markdown output templates

---

## Repository Structure

```
AI-Agent-Framework/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── main.py                   # Application entry point (76 lines)
│   │   ├── models.py                 # Pydantic models (69 lines)
│   │   ├── requirements.txt          # Runtime dependencies only
│   │   ├── routers/
│   │   │   ├── projects.py           # Project endpoints (78 lines)
│   │   │   ├── commands.py           # Command endpoints (71 lines)
│   │   │   └── artifacts.py          # Artifact endpoints (48 lines)
│   │   └── services/
│   │       ├── command_service.py    # Command orchestration (291 lines)
│   │       ├── git_manager.py        # Git operations (193 lines)
│   │       └── llm_service.py        # LLM integration (94 lines)
│   └── web/                          # React/Vite frontend
│       ├── package.json              # Uses rolldown-vite@7.2.5
│       ├── vite.config.js            # Proxies /api to backend
│       └── src/
│           └── components/
│               ├── ProjectSelector.jsx
│               ├── ProjectView.jsx
│               ├── CommandPanel.jsx
│               ├── ProposalModal.jsx
│               └── ArtifactsList.jsx
├── configs/
│   ├── llm.default.json              # Default LLM configuration
│   └── llm.json                      # User config (gitignored)
├── docker/
│   ├── Dockerfile.api                # Backend container
│   ├── Dockerfile.web                # Frontend container
│   └── nginx.conf                    # Nginx configuration
├── docs/
│   ├── README.md                     # Documentation index
│   ├── development.md                # Detailed dev guide
│   ├── project-plan.md               # Copy of PLAN.md
│   ├── architecture/                 # Architecture docs
│   ├── api/                          # API documentation
│   ├── chat/                         # Chat transcripts
│   └── howto/                        # How-to guides
├── templates/
│   ├── prompts/iso21500/             # Jinja2 prompt templates
│   └── output/iso21500/              # Markdown output templates
├── projectDocs/                      # Separate Git repo (gitignored)
├── requirements.txt                  # Dev + test dependencies
├── setup.sh / setup.ps1 / setup.bat  # Setup scripts
├── docker-compose.yml                # Container orchestration
├── PLAN.md                           # Canonical project plan
├── README.md                         # Project overview
├── QUICKSTART.md                     # Fast setup guide
└── SUMMARY.md                        # Project summary
```

**Size Statistics:**
- ~190MB total repository size
- 8000+ files including dependencies
- Core backend: ~1000 lines of Python
- Core frontend: Modern React components

---

## Implementation Phases

### Step 1 (Thin Slice): PMP + RAID

**Goal:** Deliver a minimal, end-to-end usable slice producing two core artifacts.

**Artifacts:**
- **PMP (Project Management Plan)** - Minimum viable structure:
  - Purpose/overview
  - Scope statement
  - Deliverables list
  - Milestones (coarse)
  - Roles & responsibilities
  - Communications plan (minimal)
  - Change control approach (proposal-based)

- **RAID (Risks, Assumptions, Issues, Dependencies)** - Minimum viable tracking:
  - Type (Risk/Assumption/Issue/Dependency)
  - Description
  - Owner
  - Status
  - Impact (low/med/high)
  - Due date / review date

**Required Capabilities:**
1. Create/select a project
2. Generate PMP and RAID artifacts from templates/blueprints
3. Edit artifacts in WebUI (and optionally via TUI)
4. Propose AI-assisted changes (proposal) and apply accepted proposals
5. Run audit that validates required fields and cross-artifact references

**WebUI Requirements:**
- Project selector / project creation page
- Artifact navigation (PMP, RAID)
- Artifact editor (structured fields + markdown where appropriate)
- Proposal creation (AI-assisted suggestion + human edit)
- Proposal review/apply flow
- Audit page showing results + links back to fix

### Step 2: Enhanced Artifact Set

**Additional Artifacts:**
- Project Charter
- Stakeholder Register
- Communication Plan
- Quality Management Plan

**Enhanced Features:**
- Artifact relationships and dependencies
- Cross-artifact validation rules
- Enhanced proposal diff view with side-by-side comparison

### Step 3: Advanced Capabilities

**Features:**
- Schedule baseline with Gantt view
- Resource management and allocation
- Budget tracking and forecasting
- Integration with external PM tools (Jira, MS Project)
- Multi-project portfolio view

---

## Development Workflow

### Plan → Issues → PRs

**ALWAYS follow this standard workflow:**

1. **Start with a Plan/Spec**
   - Define clear goal, scope, acceptance criteria, and constraints
   - Consider impact on related repo: `blecx/AI-Agent-Framework-Client`
   - Document any cross-repo dependencies or API changes

2. **Break Work into Small Issues**
   - Each issue should be sized for a single PR
   - Issues must include acceptance criteria and validation steps
   - Link related issues across repositories when coordinating changes

3. **Implement One Issue Per PR**
   - Keep diffs small and reviewable (prefer < 200 lines changed)
   - Include validation steps in PR description
   - Reference the issue number in PR title and description
   - Use descriptive commit messages following conventional commits

4. **Validation Requirements**
   - Run linting and builds before submitting PR
   - Test locally with both Docker and venv setups
   - Verify no unintended files are committed

5. **Merge Strategy**
   - Prefer squash merges to keep history clean
   - Ensure PR title is clear (becomes squash commit message)
   - Delete branch after merge

### Traceability

Maintain clear links: Plan → Issue → PR → Commits
- Use issue references in PRs: "Fixes #123" or "Closes #123"
- Include context in PR descriptions
- Link to related issues in other repos when coordinating changes

### Build & Setup

**Local Development (5-10 min):**
```bash
./setup.sh  # Auto-detects Python, creates .venv, installs deps (60-90s)
source .venv/bin/activate  # REQUIRED for all Python commands
mkdir -p projectDocs  # MUST exist before API starts
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
# API runs at http://localhost:8000
```

**Frontend (optional, 2-3 min):**
```bash
cd apps/web && npm install  # ~4s
npm run dev  # http://localhost:5173
npm run build  # ~120ms
```

**Docker (2-3 min build):**
```bash
mkdir -p projectDocs  # MUST exist
docker compose up --build  # Web: :8080, API: :8000
```

**Prerequisites:**
- Python 3.10+ (3.12 tested)
- Node 20+
- Git
- Docker 28+ (optional)

### Pre-Commit Validation Checklist

1. **Setup Python Environment**
   ```bash
   ./setup.sh  # Creates .venv if not exists
   source .venv/bin/activate
   mkdir -p projectDocs
   ```

2. **Run Linters** (optional but recommended)
   ```bash
   python -m black apps/api/
   python -m flake8 apps/api/
   ```

3. **Test API Locally**
   ```bash
   cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","docs_path":"..."}
   ```

4. **Test Frontend** (if changed)
   ```bash
   cd apps/web
   npm install
   npm run lint  # 1 warning in ProjectView.jsx is acceptable
   npm run build  # Should complete in ~120ms
   ```

5. **Test Docker Build** (if Dockerfile changed)
   ```bash
   docker compose build
   docker compose up
   # Verify web at :8080 and API at :8000
   ```

6. **Verify Git Status**
   ```bash
   git status
   # Ensure projectDocs/ and configs/llm.json are NOT staged
   ```

---

## Quality Assurance

### Testing Strategy

**No automated tests currently exist:**
- No pytest files in repository
- No CI/CD workflows
- No `.github/workflows/` directory
- Manual testing via API docs (`/docs`) or web UI

**Future Testing Requirements (Step 1):**
- All functionality must include **functional tests** in dedicated `tests/` directories
- Test structure:
  - `tests/unit/` - Unit tests for services and utilities
  - `tests/integration/` - API endpoint integration tests
  - `tests/functional/` - End-to-end workflow tests
  - `webui/tests/` - Frontend component tests

**E2E Requirements:**
- TUI-driven E2E tests simulating complete workflows
- Must run non-interactively (scripted) in CI
- Workflow: create/select project → generate PMP/RAID → edit → propose → apply → audit

**Quality Gates:**
- CI must fail if:
  - Tests fail
  - Required functional tests for new features are missing
  - `tests/README.md` is missing or out of date

### Linting

**Python (optional):**
```bash
python -m black apps/api/
python -m flake8 apps/api/
```

**JavaScript:**
```bash
cd apps/web && npm run lint
# Note: 1 warning in ProjectView.jsx (useEffect deps) is acceptable
```

### Manual Validation

**API Health Check:**
```bash
curl http://localhost:8000/health
```

**Create Project:**
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"key": "TEST", "name": "Test Project"}'
```

**Check Git Log:**
```bash
cd projectDocs && git log --oneline
```

---

## Appendix A: Repository Metadata

### Project Information

- **Repository:** blecx/AI-Agent-Framework
- **Primary Branch:** main
- **Related Repository:** blecx/AI-Agent-Framework-Client
- **License:** Not specified
- **Last Updated:** January 11, 2026

### Key Technologies

**Backend:**
- FastAPI 0.109.1
- Uvicorn 0.27.0
- Pydantic 2.5.3
- GitPython 3.1.41
- Jinja2 3.1.3
- OpenAI 1.10.0

**Frontend:**
- React 19.2.0
- Vite (rolldown-vite@7.2.5 override)
- ESLint 9.39.1

**Development:**
- pytest 7.4.4
- black 24.1.1
- flake8 7.0.0

### Dependencies Management

**Python Dependencies:**
- **Root `requirements.txt`:** Dev + test dependencies
- **`apps/api/requirements.txt`:** Runtime dependencies only
- When adding runtime deps: Add to BOTH files
- When adding dev/test deps: Add to root only

**JavaScript Dependencies:**
- Managed via `npm` in `apps/web/`
- Always commit both `package.json` and `package-lock.json`

### Critical Security Notes

**NEVER commit:**
- `projectDocs/` directory (separate Git repository)
- `configs/llm.json` (user-specific LLM configuration)
- API keys or credentials
- Environment files with secrets

**Security Features:**
- Audit logs store hashes only by default (compliance)
- CORS enabled (configure for production)
- Environment variables for sensitive configuration

### Common Issues & Solutions

**Setup Issues:**
- Multiple Python versions: Choose any 3.10+
- Missing python3-venv: `sudo apt install python3.12-venv`
- PowerShell restricted: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Runtime Issues:**
- PROJECT_DOCS_PATH not set: Always use `PROJECT_DOCS_PATH=../../projectDocs` when running uvicorn
- Git fails: Configure `git config --global user.email/name`
- LLM unavailable: Auto-fallback to templates (no error)
- Ports in use: Stop services or edit docker-compose.yml

**Docker Issues:**
- "npm error Exit handler never called" during build is HARMLESS, ignore
- SSL errors: Dockerfile has `--trusted-host` flags, try `docker compose build --no-cache`
- Missing projectDocs: Create directory before `docker compose up`

### Git Conventions

**Project Documents:**
- `projectDocs/` is a separate Git repository
- Auto-initialized by API on first run
- Each command creates a commit: `[PROJECT_KEY] Description`
- Let API manage projectDocs/, don't modify manually

**Code Commits:**
- Use conventional commit messages
- Reference issue numbers in commits and PRs
- Keep commits atomic and focused
- Squash merge PRs to keep history clean

### Cross-Repository Coordination

**Working with AI-Agent-Framework-Client:**

When making API changes:
1. Document breaking changes in PR description
2. Version API endpoints if breaking compatibility
3. Create matching client issue before merging backend changes
4. Link issues across repos: "Requires blecx/AI-Agent-Framework-Client#123"
5. Test integration by running both services together

**Common coordination scenarios:**
- New API endpoint → Client needs to consume it
- Changed response format → Client needs to update interfaces
- New project command → Client needs UI components
- Changed authentication → Client needs to update requests

### Quick Command Reference

```bash
# Setup from scratch
./setup.sh && source .venv/bin/activate && mkdir -p projectDocs

# Run API (local dev)
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Run frontend dev server
cd apps/web && npm install && npm run dev

# Build frontend for production
cd apps/web && npm run build

# Docker deployment
mkdir -p projectDocs && docker compose up --build

# Lint code
python -m black apps/api/ && python -m flake8 apps/api/  # Python
cd apps/web && npm run lint  # JavaScript

# Check API health
curl http://localhost:8000/health

# View project docs git log
cd projectDocs && git log --oneline
```

---

## Conclusion

This master plan consolidates the vision, architecture, and implementation strategy for the AI-Agent-Framework. The system aims to provide a robust, AI-enhanced project management platform following ISO 21500 standards with full traceability, audit capabilities, and a human-in-the-loop approval workflow.

**Key Success Factors:**
1. Maintain artifact-first approach with explicit artifacts driving all work
2. Implement thin-slice delivery for rapid value delivery
3. Ensure testability at all levels (unit, integration, E2E)
4. Keep the propose/review/apply workflow for all changes
5. Maintain clear separation between code repo and project documents
6. Follow cross-repo coordination practices for client integration

**Next Steps:**
1. Complete Step 1 implementation (PMP + RAID artifacts)
2. Establish testing infrastructure (unit, integration, E2E)
3. Document API contracts for client coordination
4. Set up CI/CD pipeline with quality gates
5. Plan Step 2 artifact enhancements

---

**Document Version:** 1.0  
**Last Updated:** January 11, 2026  
**Maintained By:** blecx/AI-Agent-Framework Team
