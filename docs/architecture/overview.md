# Architecture Overview

**AI-Agent-Framework - ISO 21500 Project Management System**

This document provides a comprehensive overview of the system architecture, components, communication flows, and deployment strategies.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [System Components](#system-components)
3. [Architecture Diagrams](#architecture-diagrams)
4. [Communication Flows](#communication-flows)
5. [Data Storage](#data-storage)
6. [Deployment Modes](#deployment-modes)
7. [Technology Stack](#technology-stack)
8. [Design Principles](#design-principles)
9. [Related Documentation](#related-documentation)

---

## System Overview

The AI-Agent-Framework is a full-stack project management system that implements ISO 21500 standards with AI assistance. The system follows a modern, containerized architecture with clear separation of concerns between the API, user interfaces, and data storage.

**Key Features:**
- ISO 21500-compliant project management
- AI-powered artifact generation with LLM integration
- Propose/apply workflow for reviewing changes before committing
- Git-based document versioning
- Multiple client interfaces (Web UI and CLI)
- Docker-based deployment

---

## System Components

The system consists of three main application components and one data storage component:

### 1. API (`apps/api/`)

**Location:** `blecx/AI-Agent-Framework/apps/api/`

**Technology:** FastAPI (Python 3.10+)

**Purpose:** Core business logic and REST API provider

**Responsibilities:**
- Project management operations (create, list, query)
- Command orchestration (propose/apply workflow)
- LLM integration via HTTP adapter
- Git operations on project documents
- Artifact generation and retrieval
- Audit logging
- Template rendering (Jinja2)

**Key Files:**
- `main.py` - FastAPI application setup
- `models.py` - Pydantic data models
- `routers/` - API endpoint definitions
  - `projects.py` - Project CRUD operations
  - `commands.py` - Command propose/apply endpoints
  - `artifacts.py` - Artifact access endpoints
- `services/` - Business logic
  - `command_service.py` - Command execution logic
  - `git_manager.py` - Git operations wrapper
  - `llm_service.py` - LLM HTTP adapter

**Port:** 8000

**API Documentation:** Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

### 2. TUI (`apps/tui/`)

**Location:** `blecx/AI-Agent-Framework/apps/tui/`

**Technology:** Python + Click framework

**Purpose:** Command-line interface for automation and testing

**Responsibilities:**
- Provide CLI access to all API endpoints
- Enable automation and scripting workflows
- Support CI/CD integration
- Validate API completeness
- Serve as reference implementation for API consumers

**Key Files:**
- `main.py` - CLI entry point and command groups
- `api_client.py` - HTTP client for API communication
- `config.py` - Configuration management
- `commands/` - Command implementations
  - `projects.py` - Project management commands
  - `propose.py` - Propose/apply workflow commands
  - `artifacts.py` - Artifact access commands

**Usage:**
```bash
# Local
python main.py projects list

# Docker
docker compose run tui projects list
```

### 3. WebUI (`apps/web/`)

**Location:** `blecx/AI-Agent-Framework/apps/web/`

**Technology:** React 19 + Vite

**Purpose:** Interactive web interface for project management

**Responsibilities:**
- Visual project creation and selection
- Interactive command panel
- Proposal review with diff viewer
- Artifact browsing and preview
- Real-time status updates

**Key Files:**
- `src/components/`
  - `ProjectSelector.jsx` - Project creation and selection
  - `ProjectView.jsx` - Main project view
  - `CommandPanel.jsx` - Command execution interface
  - `ProposalModal.jsx` - Proposal review and diff viewer
  - `ArtifactsList.jsx` - Artifact browser
- `vite.config.js` - Build configuration with API proxy

**Port:** 8080 (served via nginx in production)

**Development:** Uses Vite dev server with hot reload

### 4. Project Documents Repository

**Location:** `projectDocs/` (separate Git repository)

**Purpose:** Version-controlled storage for all project documents

**Structure:**
```
projectDocs/
├── .git/                    # Git repository
├── PROJECT_KEY_1/
│   ├── project.json        # Project metadata
│   ├── artifacts/          # Generated documents
│   │   ├── project_charter.md
│   │   ├── schedule.md
│   │   └── gap_assessment.md
│   └── events/
│       └── events.ndjson   # Audit log (NDJSON format)
├── PROJECT_KEY_2/
│   └── ...
└── README.md               # Repository documentation
```

**Key Features:**
- **Separate from code repository**: Never committed to `blecx/AI-Agent-Framework`
- **Git-based versioning**: Every change is a commit with full history
- **Auto-initialized**: API creates repository if it doesn't exist
- **Volume-mounted**: Accessible from host in Docker deployments
- **Privacy by design**: Audit logs store hashes by default

---

## Architecture Diagrams

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│          blecx/AI-Agent-Framework Repository            │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │                  apps/api/                       │   │
│  │              FastAPI Backend                     │   │
│  │                                                  │   │
│  │  • REST API endpoints                           │   │
│  │  • Business logic                               │   │
│  │  • LLM integration                              │   │
│  │  • Git operations                               │   │
│  │                                                  │   │
│  │  Port: 8000                                      │   │
│  └────────────────┬───────────────┬─────────────────┘   │
│                   │               │                      │
│         ┌─────────┴──────┐   ┌───┴──────────────┐      │
│         │                │   │                   │      │
│  ┌──────▼──────┐  ┌─────▼────▼──┐               │      │
│  │  apps/tui/  │  │  apps/web/  │               │      │
│  │  CLI Client │  │   Web UI    │               │      │
│  │  (Python)   │  │(React+Vite) │               │      │
│  │             │  │             │               │      │
│  │  Commands   │  │ Interactive │               │      │
│  │  Automation │  │  Interface  │               │      │
│  │  Scripting  │  │             │               │      │
│  │             │  │ Port: 8080  │               │      │
│  └─────────────┘  └─────────────┘               │      │
│                                                   │      │
│                                   Git Operations │      │
│                                                   ▼      │
│                                        ┌──────────────┐ │
│                                        │ /projectDocs │ │
│                                        │  Git Repo    │ │
│                                        │              │ │
│                                        │  • Projects  │ │
│                                        │  • Artifacts │ │
│                                        │  • History   │ │
│                                        └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                                   
                                   │
                                   │ HTTP (OpenAI-compatible)
                                   ▼
                          ┌──────────────────┐
                          │   LLM Service    │
                          │  (LM Studio /    │
                          │   OpenAI API)    │
                          └──────────────────┘
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                              │
│  ┌───────────────────────────────────────────────────┐     │
│  │         iso21500-network (Bridge)                 │     │
│  │                                                     │     │
│  │  ┌────────────────┐  ┌────────────────┐          │     │
│  │  │  api:8000      │  │  web:80        │          │     │
│  │  │  (FastAPI)     │◄─┤  (nginx+React) │          │     │
│  │  │                │  │                 │          │     │
│  │  └───────┬────────┘  └────────────────┘          │     │
│  │          │                                         │     │
│  │          │           ┌────────────────┐          │     │
│  │          └──────────►│  tui           │          │     │
│  │                      │  (Python CLI)  │          │     │
│  │                      └────────────────┘          │     │
│  │                                                     │     │
│  └───────────────────────────────────────────────────┘     │
│                                                              │
│  Volume Mounts:                                             │
│  • ./projectDocs:/projectDocs (API)                        │
│  • ./configs/llm.default.json:/config/llm.json (API)      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
           │                                  │
           │ Port Mapping                     │ Port Mapping
           ▼                                  ▼
      Host:8000                           Host:8080
```

### Sequence Diagram: Propose/Apply Flow

```
User (TUI/Web)    API Server     LLM Service    Git Manager    projectDocs/
      │               │               │              │              │
      │─── POST ────► │               │              │              │
      │  /propose     │               │              │              │
      │               │               │              │              │
      │               │─── Generate ──►              │              │
      │               │  (Optional)   │              │              │
      │               │◄── Response ──┤              │              │
      │               │               │              │              │
      │               │──── Read current state ─────►│              │
      │               │◄─── Project files ───────────┤              │
      │               │               │              │              │
      │◄── Proposal ──┤               │              │              │
      │   (preview)   │               │              │              │
      │               │               │              │              │
   [User Reviews]     │               │              │              │
      │               │               │              │              │
      │─── POST ────► │               │              │              │
      │  /apply       │               │              │              │
      │               │               │              │              │
      │               │──── Write files ────────────►│              │
      │               │               │              │─── commit ──►│
      │               │               │              │◄─── hash ────┤
      │               │◄─── Success ─────────────────┤              │
      │               │               │              │              │
      │◄── Success ───┤               │              │              │
      │               │               │              │              │
```

---

## Communication Flows

### TUI → API

**Protocol:** HTTP/REST over Docker network or localhost

**Communication:**
- TUI makes HTTP requests to API endpoints
- Uses environment variable `API_BASE_URL` for configuration
- Supports both Docker network (`http://api:8000`) and localhost
- Standard REST patterns (GET, POST)
- JSON request/response format

**Authentication:** Optional API key via `X-API-Key` header (future)

### WebUI → API

**Protocol:** HTTP/REST with proxy in development

**Communication:**
- React app makes fetch requests to API
- Development: Vite proxy forwards `/api` to `http://localhost:8000`
- Production: nginx reverse proxy handles routing
- CORS enabled in API for cross-origin requests

**Development Flow:**
```
Browser → Vite Dev Server (5173) → Proxy → API (8000)
```

**Production Flow:**
```
Browser → nginx (80) → API (8000)
         ↓
      Static files (React build)
```

### API → Project Documents

**Protocol:** Git operations via GitPython library

**Operations:**
- `git init` - Initialize repository on first use
- `git add` - Stage files for commit
- `git commit` - Commit changes with descriptive messages
- `git log` - Retrieve commit history
- File I/O - Read/write project files and artifacts

**Commit Messages:** Format: `[PROJECT_KEY] Description`

**Example:**
```
[PROJ001] Create project
[PROJ001] Add gap assessment artifact
[PROJ001] Update project charter
```

### API → LLM Service

**Protocol:** HTTP POST (OpenAI-compatible API)

**Configuration:** JSON config file (`configs/llm.default.json`)

**Request Flow:**
1. API constructs prompt from Jinja2 template
2. Sends POST request to LLM endpoint
3. Receives generated content
4. Falls back to static templates if LLM unavailable

**Graceful Degradation:**
- If LLM service is unreachable, uses template-based generation
- No error thrown to user
- System continues to function with template outputs

---

## Data Storage

### Project Documents Storage

**Location:** `projectDocs/` directory (Git repository)

**Structure:**
- Each project gets its own directory named by project key
- `project.json` stores project metadata
- `artifacts/` directory contains generated documents
- `events/events.ndjson` contains audit log

**Version Control:**
- Every change creates a Git commit
- Full history preserved
- Can revert to any previous state
- Commit messages describe changes

**Privacy Features:**
- Audit logs store SHA-256 hashes by default
- Optional full content logging (disabled by default)
- No secrets in project documents
- Separate from code repository

### Configuration Storage

**LLM Configuration:** `configs/llm.default.json`
- LLM endpoint URL
- Model name
- API key (if required)
- Request parameters (temperature, max_tokens, etc.)

**Templates:**
- Prompts: `templates/prompts/iso21500/*.j2`
- Output templates: `templates/output/iso21500/*.md`

---

## Deployment Modes

### 1. Docker Compose (Recommended)

**Best for:** Production, team environments, consistent setup

**Setup:**
```bash
mkdir -p projectDocs
docker compose up --build
```

**Access:**
- Web UI: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Advantages:**
- Consistent environment across machines
- All dependencies included
- Easy to scale
- Isolated from host system

### 2. Local Development

**Best for:** Development, debugging, rapid iteration

**Setup:**
```bash
# Backend
cd apps/api
source .venv/bin/activate
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Frontend (separate terminal)
cd apps/web
npm run dev

# TUI (separate terminal)
cd apps/tui
source .venv/bin/activate
python main.py --help
```

**Advantages:**
- Fast hot reload
- Direct access to source code
- Easy debugging
- Native IDE integration

### 3. Hybrid Mode

**Best for:** Frontend development with stable backend

**Setup:**
```bash
# API in Docker
docker compose up api

# Frontend locally
cd apps/web
npm run dev

# TUI locally
cd apps/tui
export API_BASE_URL=http://localhost:8000
python main.py projects list
```

**Advantages:**
- Fast frontend iteration
- Stable backend environment
- Best of both worlds

### 4. Kubernetes (Future)

**Best for:** Large-scale deployments, high availability

**Components:**
- API deployment with autoscaling
- Web deployment with ingress
- Persistent volume for projectDocs
- ConfigMaps for configuration
- Secrets for sensitive data

---

## Technology Stack

### Backend (API)

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| FastAPI | 0.109.1 | Web framework |
| Uvicorn | 0.27.0 | ASGI server |
| Pydantic | 2.5.3 | Data validation |
| GitPython | 3.1.41 | Git operations |
| Jinja2 | 3.1.3 | Template engine |
| OpenAI | 1.10.0 | LLM client library |

### Frontend (WebUI)

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI framework |
| Vite | 7.2.5 | Build tool |
| ESLint | 9.39.1 | Code linting |

### CLI (TUI)

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| Click | 8.1.7 | CLI framework |
| httpx | 0.27.0 | HTTP client |
| Rich | 13.7.0 | Terminal formatting |

### Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 28+ | Containerization |
| Docker Compose | 3.8 | Multi-container orchestration |
| nginx | Latest | Web server (production) |
| Git | 2.x | Version control |

---

## Design Principles

### 1. API-First Design

All functionality is exposed via REST API. Both TUI and WebUI are pure API consumers with no shared business logic.

**Benefits:**
- Clear separation of concerns
- Easy to add new clients
- Testable API layer
- Supports third-party integrations

### 2. Separation of Concerns

- **API**: Business logic and data access
- **TUI**: Command-line interface
- **WebUI**: Visual interface
- **Project Documents**: Data storage

Each component has a single, well-defined responsibility.

### 3. Git-Based Storage

Project documents are stored in a separate Git repository, providing:
- Version history
- Change tracking
- Rollback capability
- Audit trail
- No database required

### 4. Propose/Apply Workflow

Two-step process ensures users review changes before committing:
1. **Propose**: Generate and preview changes
2. **Apply**: Commit approved changes to Git

**Benefits:**
- User control and transparency
- Prevents unwanted changes
- Supports review process
- Compliance with governance requirements

### 5. Template-Based Generation

Jinja2 templates for prompts and outputs:
- Consistent formatting
- Easy to customize
- Fallback when LLM unavailable
- Version-controlled templates

### 6. Privacy by Design

- Audit logs store hashes by default, not full content
- Optional full content logging (disabled by default)
- No secrets in configuration files
- Separate project documents from code

### 7. Graceful Degradation

- LLM unavailable? Use templates
- Git operations fail? Return clear error
- Missing configuration? Use defaults
- System remains functional under various failure modes

---

## Related Documentation

### Architecture Decisions

- [ADR-0001: Separate Project Documents Git Repository](../adr/0001-docs-repo-mounted-git.md)
- [ADR-0002: LLM HTTP Adapter with JSON Configuration](../adr/0002-llm-http-adapter-json-config.md)
- [ADR-0003: Propose/Apply Workflow](../adr/0003-propose-apply-before-commit.md)
- [ADR-0004: Separate Client Application](../adr/0004-separate-client-application.md)

### Deployment Guides

- [Deployment Guide](../deployment/README.md)
- [Quick Start Guide](../../QUICKSTART.md)
- [Development Guide](../development.md)

### API Documentation

- [Client Integration Guide](../api/client-integration.md)
- [Interactive API Docs](http://localhost:8000/docs) (when running)

### Specifications

- [MVP Specification](../spec/mvp-iso21500-agent.md)

---

**Last Updated:** 2026-01-10  
**Version:** 1.0.0  
**Status:** Active
