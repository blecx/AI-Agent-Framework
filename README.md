# AI-Agent-Framework

[![Backend CI](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci.yml/badge.svg)](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci.yml)
[![Backend Quality Gates](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci-backend.yml)
[![PoC CI](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci-poc.yml/badge.svg)](https://github.com/blecx/AI-Agent-Framework/actions/workflows/ci-poc.yml)
[![codecov](https://codecov.io/gh/blecx/AI-Agent-Framework/branch/main/graph/badge.svg)](https://codecov.io/gh/blecx/AI-Agent-Framework)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An ISO 21500 Project Management AI Agent System with FastAPI backend and React/Vite frontend, deployed as Docker containers.

---

## 🤖 Multi-Agent Coding Framework (PoC → MVP Roadmap)

This repository also contains a **multi-agent local coding framework** that automates code changes via a hub-and-agent Docker stack.

### Roadmap

| Phase | Label | Status | Description |
|---|---|---|---|
| **S1** | **PoC** | ✅ *current* | Hub (FastAPI+Postgres), generalist agent, python-runner, LLM-gateway stub, CLI (`agentctl`) |
| S2 | MVP | 🔜 planned | Specialised agents (architect, tester, reviewer), real LLM policies, approval UI, multi-repo |
| S3 | Hardening | 🔜 planned | Retry/back-off, RBAC, audit log, observability |
| 9C | VS Code Extension | 🔜 deferred | Full IDE integration, run panel, diff viewer |

**→ See [`poc/README.md`](poc/README.md) for setup, quickstart, and full documentation.**

---

## Overview

This system provides intelligent project management following ISO 21500 standards. It features:

- **FastAPI Backend**: Handles project management logic, LLM interactions, and git-based document storage
- **React/Vite Frontend**: Modern UI for project creation, command execution, and artifact management
- **Docker Deployment**: Two-container setup for easy deployment
- **Git-based Storage**: All project documents stored in a separate git repository with full version history

## 📚 Documentation

**New to the project?** Start here:

- 🚀 **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 10 minutes
- 🧰 **[Install & LLM Setup Guide](docs/howto/install-and-llm-setup.md)** - Docker images, local setup, and provider configuration examples
- 🧩 **[Context7 MCP Setup (VS Code + Docker)](docs/howto/context7-vscode-docker.md)** - Persistent docs-grounding setup with boot-time startup
- 🛡️ **[Bash Gateway MCP Setup (VS Code + Docker)](docs/howto/mcp-bash-gateway.md)** - Policy-allowlisted script execution via local MCP server
- 🧱 **[Repo Fundamentals MCP Setup](docs/howto/mcp-repo-fundamentals.md)** - Git/Search/Filesystem MCP servers
- ⚙️ **[DevOps MCP Setup](docs/howto/mcp-devops.md)** - Docker/Compose + Test Runner MCP servers
- 📚 **[Offline Docs MCP Setup](docs/howto/mcp-offline-docs.md)** - Local SQLite docs index for fully offline docs grounding
- 🧑‍💻 **[GitHub Ops MCP Setup](docs/howto/mcp-github-ops.md)** - PR/Issue/Checks workflows via `gh` in a dedicated MCP container
- 📏 **[MCP Tool Arbitration Hard Rules](docs/howto/mcp-routing-rules.md)** - Strict tool-selection precedence for ambiguous tasks

Boot-time setup helper (all MCP services):

```bash
./scripts/install-all-mcp-systemd.sh
```

- 📚 **[Tutorials](docs/tutorials/README.md)** - NEW! Step-by-step learning paths for all skill levels
- 🤖 **[Resolve-Issue Chat](ISSUEAGENT-CHAT-SETUP.md)** - Run resolve-issue and Ralph agents from VS Code chat
- 🤝 **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- 📖 **[Documentation Hub](docs/README.md)** - Complete documentation index

**Architecture & Design:**

- 🏗️ **[Architecture Overview](docs/architecture/overview.md)** - High-level system design
- 🧩 **[Module Documentation](docs/architecture/modules.md)** - Detailed module boundaries and responsibilities
- 📊 **[Data Models](docs/architecture/data-models.md)** - Pydantic models and schemas
- 🔄 **[Interaction Flows](docs/architecture/flows.md)** - Sequence diagrams and data flows
- 🔧 **[Extensibility Guide](docs/architecture/extensibility.md)** - How to extend the system

**Developer Resources:**

- 💻 **[Development Guide](docs/development.md)** - Local development setup and workflow
- 🧪 **[Testing Guide](tests/README.md)** - Running tests and coverage
- 🔗 **[E2E Testing](E2E_TESTING.md)** - Cross-repo E2E testing with client
- 🎯 **[API Integration Guide](docs/api/client-integration-guide.md)** - Building custom clients
- 🏛️ **[Architecture Decision Records](docs/adr/)** - Key architectural decisions
- 🔄 **[PR Merge Workflow](docs/prmerge-command.md)** - Automated PR merge and issue closing
- 🐛 **[PR Troubleshooting](docs/prmerge-best-practices.md#troubleshooting-common-issues)** - Common CI and merge issues

## Architecture

### Three-Container Setup

The system uses a modern three-container architecture for maximum flexibility and separation of concerns:

1. **API Container (`api`)**: FastAPI backend service
   - Handles project management logic and LLM interactions
   - Manages git-based document storage
   - Exposes REST API endpoints
   - Port: 8000

2. **Web Container (`web`)**: React/Vite frontend service
   - Modern UI for project creation and management
   - Visual diff viewer for proposal review
   - Artifact browser and preview
   - Port: 8080

3. **Client Container (`client`)**: Python CLI client (optional)
   - Demonstrates API usage without the web UI
   - Enables automation and scripting
   - CI/CD integration capability
   - Command-line interface for all API operations

### Why Three Containers?

This architecture provides:

- **API-First Design**: The client validates that all functionality is available via REST API
- **Composability**: Each component can be used independently
- **Flexibility**: Choose the interface that fits your workflow (Web UI, TUI, or CLI)
- **Automation**: Client enables scripting and CI/CD integration
- **Optional Components**: The client is not required for core functionality

### Container Communication

```
┌─────────────┐
│   Web UI    │──┐
│  (port 8080)│  │  Rich visual interface
└─────────────┘  │
                 │    ┌──────────────┐
                 ├───►│  API Server  │◄────────┐
                 │    │  (port 8000) │         │
┌─────────────┐  │    └──────────────┘         │
│   Client    │──┘            │                │
│  (TUI/CLI)  │  Interactive  ▼                │
└─────────────┘  & Automation │                │
                       ┌──────────────┐         │
                       │ projectDocs/ │─────────┘
                       │ (Git Repo)   │
                       └──────────────┘
```

All containers communicate via Docker network. The web UI and client (with TUI/CLI modes) both consume the same REST API.

### Backend (FastAPI)

- LLM abstraction with OpenAI-compatible HTTP adapter
- Git repository manager for project documents
- Command orchestration with propose/apply workflow
- Audit logging with NDJSON format
- Template-driven artifact generation
- **AI Agent Cognitive Skills**: Extensible skill system with Memory, Planning, and Learning capabilities

### Cognitive Skills System

The framework includes a powerful extensible skills system that provides cognitive capabilities to AI agents:

- **Memory Skill**: Short-term and long-term memory management for agents
- **Planning Skill**: Multi-step plan generation from goals and constraints
- **Learning Skill**: Experience capture and learning from outcomes
- **Extensible Architecture**: Easy to add custom skills via plugin system

**Documentation:** [docs/skills/README.md](docs/skills/README.md) | **API:** [docs/api/skills-api.md](docs/api/skills-api.md)

### Frontend (React/Vite)

- Project creation and selection
- Command panel with three core commands:
  - `assess_gaps`: Analyze missing ISO 21500 artifacts
  - `generate_artifact`: Create/update project documents
  - `generate_plan`: Generate project schedule with Mermaid gantt chart
- Proposal review modal with unified diff viewer
- Artifacts list and preview
- Real-time status updates

### Compliance Features

- No secrets committed to code repository
- Optional prompt/content logging (disabled by default)
- Only hashes stored in audit logs by default
- Separate project documents repository

## User Interfaces & Clients

The AI-Agent Framework provides multiple interfaces to suit different workflows and use cases:

### 🎓 Learning Resources

**New users?** Start with our comprehensive tutorials:

- **[TUI Quick Start](docs/tutorials/tui-basics/01-quick-start.md)** - Get started with command-line interface (5 min)
- **[Web Interface Basics](docs/tutorials/gui-basics/01-web-interface.md)** - Learn the web GUI (5 min)
- **[Complete Learning Paths](docs/tutorials/README.md)** - Structured paths from beginner to advanced (60-220 minutes)

All tutorials use a Todo Application example to teach real-world ISO 21500 project management.

### 🖥️ TUI (Text User Interface)

**Location:** `apps/tui/`

A command-line interface for automation, testing, and scripting workflows.

**Best for:**

- CI/CD pipelines and automation
- Quick testing and validation
- Command-line scripting
- Server environments without GUI

**Documentation:** [apps/tui/README.md](apps/tui/README.md)

### 🎮 Advanced Client (CLI + Interactive TUI)

**Location:** `client/`

A Python-based client with both traditional CLI and an interactive terminal UI (using Textual).

**Best for:**

- Interactive terminal-based project management
- SSH/remote sessions
- Visual navigation in terminal
- API testing and validation
- Automation with rich feedback

**Documentation:** [client/README.md](client/README.md)

### 🌐 WebUI (Web User Interface)

**Repository:** [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)

A modern graphical web interface for interactive project management (separate repository).

**Best for:**

- Interactive project management with visual feedback
- Team collaboration
- Non-technical users
- Visual diff review and proposal comparison
- Cross-platform access from any browser

**Documentation:** See the [WebUI repository](https://github.com/blecx/AI-Agent-Framework-Client) for setup and usage instructions.

### Choosing the Right Client

| Client     | Use Case                | Automation   | Visual Interface        | Setup Complexity |
| ---------- | ----------------------- | ------------ | ----------------------- | ---------------- |
| **TUI**    | CLI automation, scripts | ✅ Excellent | 📟 Command-line         | 🟢 Simple        |
| **Client** | Terminal workflows      | ✅ Good      | 🖥️ Interactive terminal | 🟢 Simple        |
| **WebUI**  | Interactive management  | ⚠️ Limited   | 🌐 Full graphical UI    | 🟡 Moderate      |

All clients communicate with the same REST API, ensuring feature parity and flexibility.

## Quick Start

**📖 See [QUICKSTART.md](QUICKSTART.md) for a detailed step-by-step guide.**

### Optional: OpenAI Images for workflow mockups

Some workflow steps can generate UI mockup artifacts via OpenAI Images.

- Set `OPENAI_API_KEY` in your shell before running mockup-enabled steps.
- Workflow entry point: `agents.tools.generate_mockup_artifacts(...)`.
- Output folder: `.tmp/mockups/issue-<n>/` (images + `index.html`).
- If the key is missing, mockup generation exits gracefully with an actionable message.

### VS Code Auto-Approve Setup (Optional but Recommended)

If you're using VS Code with GitHub Copilot, apply the safe profile (default):

```bash
./scripts/setup-low-approval.sh safe
```

Opt in to low-friction mode only when working in a high-trust environment:

```bash
./scripts/setup-low-approval.sh low-friction
```

Roll back to safe mode at any time:

```bash
./scripts/setup-low-approval.sh safe
```

To regenerate workspace settings (backend + client) and verify no drift:

```bash
./scripts/setup-autoapprove.sh --workspace-only
./scripts/setup-autoapprove.sh --check --workspace-only
```

This configures auto-approve for:

- **Subagents**: `resolve-issue`, `close-issue`, `pr-merge`, `Plan`
- **Terminal commands**: Git, npm, Python, Docker, and 60+ common commands
- **All workspaces**: Backend, client, and global VS Code settings

After running, reload VS Code (`Ctrl+Shift+P` → `Developer: Reload Window`) to apply changes.

**Risk note**: Low-friction mode increases convenience but broadens approval scope; prefer `safe` as the default profile.

## Installation & Setup

To avoid duplicated setup instructions across docs, this repository uses:

- **Quick path:** [QUICKSTART.md](QUICKSTART.md)
- **Canonical install + LLM guide:** [docs/howto/install-and-llm-setup.md](docs/howto/install-and-llm-setup.md)

### Local quick reference

```bash
git submodule update --init --recursive
./setup.sh
source .venv/bin/activate
mkdir -p projectDocs
cp configs/llm.default.json configs/llm.json  # optional
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

In another terminal (optional web dev UI):

```bash
cd ../AI-Agent-Framework-Client/client
npm install
npm run dev
```

### Docker quick reference

```bash
git submodule update --init --recursive
docker compose up --build
```

Endpoints:

- Web UI: <http://localhost:8080>
- API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>
- Client CLI/TUI: `docker compose run client <command>`

## Client Usage

The optional client provides both interactive (TUI) and command-line (CLI) access to all API operations.

### 🖥️ Terminal User Interface (TUI) - NEW!

Launch an interactive visual interface in your terminal:

```bash
# Launch TUI (default when running client container)
docker compose run client

# Or explicitly
docker compose run client tui
```

**TUI Features:**

- 📁 **Visual Project Management**: Browse and create projects with menus
- ⚙️ **Interactive Commands**: Run commands with real-time feedback
- 📊 **Artifact Browser**: View generated artifacts
- ⌨️ **Keyboard Navigation**: Full keyboard and mouse support
- 🎨 **Dark/Light Mode**: Toggle with `d` key

### 📟 Command Line Interface (CLI)

Traditional CLI for automation and scripting:

### Quick Start

```bash
# Show available commands
docker compose run client --help

# Create a project
docker compose run client create-project --key PROJ001 --name "My Project"

# List all projects
docker compose run client list-projects

# Run a complete demo workflow
docker compose run client demo --key DEMO001 --name "Demo Project"
```

### Common Commands

```bash
# Check API health
docker compose run client health

# Get project state
docker compose run client get-state --key PROJ001

# Propose command (preview changes)
docker compose run client propose --key PROJ001 --command assess_gaps

# Apply proposal (commit changes)
docker compose run client apply --key PROJ001 --proposal-id <id>

# List artifacts
docker compose run client list-artifacts --key PROJ001

# Get artifact content
docker compose run client get-artifact --key PROJ001 --path artifacts/gap_assessment.md
```

For detailed client documentation, see [client/README.md](client/README.md).

## Usage

### Creating a Project

1. Open http://localhost:8080
2. Click "Create New Project"
3. Enter a project key (e.g., `PROJ001`) and name
4. Click "Create Project"

### Running Commands

1. Select your project
2. Choose a command from the Commands tab:
   - **Assess Gaps**: Identifies missing ISO 21500 artifacts
   - **Generate Artifact**: Creates specific project documents
   - **Generate Plan**: Generates project schedule with timeline
3. Click "Propose Changes" to see what will be created
4. Review the proposed changes and diffs
5. Click "Apply & Commit" to save changes to git

### Viewing Artifacts

1. Switch to the "Artifacts" tab
2. Click on any artifact to view its content
3. All changes are tracked in git with full history

## Project Structure

```
AI-Agent-Framework/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Application entry point
│   │   ├── models.py          # Pydantic models
│   │   ├── services/          # Core services
│   │   │   ├── git_manager.py # Git operations
│   │   │   ├── llm_service.py # LLM integration
│   │   │   └── command_service.py # Command handling
│   │   └── routers/           # API routes
├── ../AI-Agent-Framework-Client/
│   └── client/                # Canonical React/Vite web UI
│       └── src/
├── docker/
│   ├── api/                   # API Dockerfile
│   └── web/                   # Web Dockerfile + nginx config
├── templates/
│   ├── prompts/iso21500/      # Jinja2 prompt templates
│   └── output/iso21500/       # Markdown output templates
├── configs/
│   └── llm.default.json       # Default LLM configuration
├── projectDocs/               # Git repo for project documents (auto-created)
└── docker-compose.yml         # Docker orchestration
```

## LLM Configuration

LLM configuration examples are maintained in one place:

- [docs/howto/install-and-llm-setup.md#llm-connection-configuration](docs/howto/install-and-llm-setup.md#llm-connection-configuration)

Supported examples include:

- GitHub Models (Copilot/GitHub)
- OpenAI
- Local LLMs (LM Studio, Ollama via OpenAI-compatible endpoint)

## Project Documents Storage

All project documents are stored in the `projectDocs/` directory, which is:

- A separate git repository (auto-initialized if missing)
- Mounted into the API container at `/projectDocs`
- Never committed to the code repository
- Fully version-controlled with commit history

### Directory Structure

```
projectDocs/
├── .git/                      # Git repository
├── PROJECT001/
│   ├── project.json          # Project metadata
│   ├── artifacts/            # Generated documents
│   │   ├── project_charter.md
│   │   ├── schedule.md
│   │   └── ...
│   ├── reports/              # Gap assessments, etc.
│   └── events/
│       └── events.ndjson     # Audit log
└── PROJECT002/
    └── ...
```

## API Endpoints

### Projects

- `POST /projects` - Create new project
- `GET /projects` - List all projects
- `GET /projects/{key}/state` - Get project state

### Commands

- `POST /projects/{key}/commands/propose` - Propose changes
- `POST /projects/{key}/commands/apply` - Apply changes

### Artifacts

- `GET /projects/{key}/artifacts` - List artifacts
- `GET /projects/{key}/artifacts/{path}` - Get artifact content

## Development

### Local Development Setup

For detailed local development setup, see the [Local Development Setup](#local-development-setup) section above.

**Quick Reference:**

1. **Create virtual environment:**

   ```bash
   ./setup.sh  # Linux/macOS
   # or
   setup.bat   # Windows
   ```

2. **Activate virtual environment:**

   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate.bat  # Windows
   ```

3. **Run the API:**

   ```bash
   cd apps/api
   PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   ```

4. **Run the Web UI (optional):**
   ```bash
   cd ../AI-Agent-Framework-Client/client
   npm install
   npm run dev
   ```

### Adding New Dependencies

1. Add the dependency to `requirements.txt` with a pinned version
2. If it's a runtime dependency (needed by the API), also add it to `apps/api/requirements.txt`
3. Reinstall dependencies:
   ```bash
   source .venv/bin/activate  # Activate if not already active
   pip install -r requirements.txt
   ```
4. For Docker deployment, rebuild the images:
   ```bash
   docker compose build --no-cache
   ```

**Note:** Testing and development dependencies (pytest, black, flake8) should only be in the root `requirements.txt`, not in `apps/api/requirements.txt`.

### Adding New Commands

1. Add command logic to `apps/api/services/command_service.py`
2. Create prompt template in `templates/prompts/iso21500/`
3. Create output template in `templates/output/iso21500/`
4. Update frontend `CommandPanel.jsx` with new command
   (canonical UI repo path: `../AI-Agent-Framework-Client/client/src`)

### Testing

Comprehensive test suite with unit, integration, and E2E tests. **See [Testing Guide](tests/README.md) for full documentation.**

#### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests only
pytest tests/integration

# E2E tests
TERM=xterm-256color pytest tests/e2e

# With coverage
pytest --cov=apps/api --cov-report=html tests/
# View coverage: open htmlcov/index.html

# With coverage threshold check (80%)
pytest --cov=apps/api --cov-report=term-missing --cov-fail-under=80 tests/
```

#### Test Structure

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - `test_command_service.py` - Command propose/apply logic
  - `test_git_manager.py` - Git operations
  - `test_llm_service.py` - LLM client
  - `test_governance_service.py` - Governance operations
  - `test_raid_service.py` - RAID register
  - `test_workflow_service.py` - Workflow state machine
  - `test_audit_service.py` - Audit logging

- **Integration Tests** (`tests/integration/`): Test API endpoints
  - `test_core_api.py` - Health, projects, commands, artifacts
  - `test_governance_api.py` - Governance endpoints
  - `test_raid_api.py` - RAID endpoints
  - `test_workflow_api.py` - Workflow endpoints

- **E2E Tests** (`tests/e2e/`): Test complete workflows
  - `test_governance_raid_workflow.py` - Full governance + RAID workflows
  - `backend_e2e_runner.py` - E2E test harness for cross-repo testing

#### Coverage Requirements

- Overall: 80%+ (enforced in CI)
- Services: 90%+
- Routers: 85%+

Current coverage: ![Coverage](https://codecov.io/gh/blecx/AI-Agent-Framework/branch/main/graph/badge.svg)

#### E2E Testing with Client

For cross-repository E2E testing with the client, see **[E2E Testing Guide](E2E_TESTING.md)**.

Quick start:

```bash
# Terminal 1: Start backend
python tests/e2e/backend_e2e_runner.py --mode server

# Terminal 2: Run client E2E tests (in client repo)
export BACKEND_URL=http://localhost:8000
npm run test:e2e
```

#### Writing Tests

**Unit tests** should:

- Mock all external dependencies
- Test one component at a time
- Use fixtures for common setup
- Be fast and deterministic

**Integration tests** should:

- Use FastAPI TestClient
- Create isolated test environment per test
- Test realistic API workflows
- Verify both success and error responses

**All tests** must:

- Be independent (no shared state)
- Use unique temp directories
- Clean up after themselves
- Work in any order
- Be parallel-safe

### Development Workflow Scripts

The project includes automation scripts for common development workflows:

#### PR Merge Workflow (`scripts/prmerge`)

Comprehensive command for handling the entire PR merge workflow from validation to issue closure:

```bash
# Basic usage - merge PR and close issue
./scripts/prmerge <issue_number>

# With completion time tracking
./scripts/prmerge <issue_number> <actual_hours>

# Example
./scripts/prmerge 24 7.5
```

**Features:**

- ✅ Automatic PR detection by issue number
- ✅ CI validation (fails fast if CI failing)
- ✅ Branch protection handling (3 resolution strategies)
- ✅ Comprehensive issue closing messages
- ✅ Learning system integration (completion time tracking)
- ✅ Next issue suggestion

**What it does:**

1. Validates PR exists and CI passes
2. Guides manual review if needed
3. Handles branch protection issues
4. Merges PR with squash commit
5. Gets merge commit SHA
6. Generates comprehensive issue closing message
7. Closes issue with detailed documentation
8. Records completion for learning system
9. Suggests next issue to work on

**📖 See [PR Merge Command Documentation](docs/prmerge-command.md) for complete guide.**

#### Issue Selection (`scripts/next-issue.py`)

Intelligent issue selector with **two-phase workflow**:

**Phase 1: Reconciliation** - Syncs local tracking with GitHub (source of truth)
**Phase 2: Selection** - Finds next available issue based on dependencies and priority

```bash
# Normal usage (includes reconciliation)
./scripts/next-issue.py

# With detailed GitHub API debugging
./scripts/next-issue.py --verbose

# Custom timeout (default: 180s)
./scripts/next-issue.py --timeout 120

# Skip reconciliation (faster, but not recommended)
./scripts/next-issue.py --skip-reconcile

# Preview without updating knowledge base
./scripts/next-issue.py --dry-run
```

**Features:**

- GitHub as source of truth (not local files)
- Automatic PR/issue reconciliation
- Sequential order from tracking file (issues 24-58)
- Built-in timeout handling (no external `timeout` needed)
- API response caching for performance
- Progress indicators for long operations

**📖 See [Next Issue Command Documentation](docs/NEXT-ISSUE-COMMAND.md) for complete guide.**

#### Completion Tracking (`scripts/record-completion.py`)

Records completion data for learning system to improve future estimates:

```bash
# Record completion
./scripts/record-completion.py <issue_number> <actual_hours> "<notes>"

# Example
./scripts/record-completion.py 24 7.5 "Tests took longer than expected"
```

**📖 See [Development Guide](docs/development.md) for more workflow automation.**

#### Goal Archiving (`scripts/archive-goals.sh`)

Archive all `## Goal...` sections from `.tmp/*.md` into timestamped artifacts under `.tmp/archive/`.

```bash
# Archive goals and keep source files in .tmp
bash scripts/archive-goals.sh

# Archive and move matched source files into the timestamped snapshot folder
bash scripts/archive-goals.sh --move
```

Outputs per run:

- `goals-<timestamp>.md` (consolidated goal archive)
- `goals-<timestamp>.json` (manifest)
- `snapshots/<timestamp>/` (source snapshots)

`scripts/work-issue.py` runs goal archiving automatically before and after execution.
Disable with `--no-goal-archive` (per-run) or `WORK_ISSUE_GOAL_ARCHIVE=0` (environment).

### Adding New Templates

**Prompt Template** (`templates/prompts/iso21500/my_command.j2`):

```jinja2
You are creating {{ artifact_name }} for project {{ project_key }}.
...
```

**Output Template** (`templates/output/iso21500/my_artifact.md`):

```markdown
# {{ title }}

{{ generated_content }}
```

## Security & Compliance

- API keys and secrets never committed to git
- Prompt/content logging disabled by default
- Audit logs store only hashes unless explicitly enabled
- Project documents in separate git repository
- No sensitive data in code repository

## ISO 21500 Artifacts

The system supports generating standard ISO 21500 project management artifacts:

1. Project Charter
2. Stakeholder Register
3. Scope Statement
4. Work Breakdown Structure (WBS)
5. Project Schedule
6. Budget Plan
7. Quality Plan
8. Risk Register
9. Communication Plan
10. Procurement Plan

## ISO 21500/21502 Governance & RAID Register

The system includes a comprehensive governance backbone aligned with ISO 21500/21502 standards:

### Governance Features

- **Governance Metadata**: Track project objectives, scope, stakeholders, decision rights, stage gates, and approvals
- **Decision Log**: Record and track key project decisions with rationale and impact analysis
- **Traceability**: Bidirectional linking between decisions and RAID items
- **Audit Trail**: Complete history of all governance activities

### RAID Register

Comprehensive management of:

- **Risks**: Potential events that may negatively impact the project
- **Assumptions**: Factors believed to be true for planning purposes
- **Issues**: Current problems requiring resolution
- **Dependencies**: Reliance on external factors, teams, or deliverables

Features include:

- CRUD operations with full lifecycle tracking
- Filtering by type, status, owner, and priority
- Impact and likelihood assessment for risks
- Mitigation planning and next actions
- Links to governance decisions and change requests
- Audit trail with created/updated timestamps

### API Endpoints

**Governance:**

- `GET/POST/PUT /projects/{key}/governance/metadata` - Governance metadata management
- `GET/POST /projects/{key}/governance/decisions` - Decision log management
- `GET /projects/{key}/governance/decisions/{id}` - Single decision retrieval
- `POST /projects/{key}/governance/decisions/{id}/link-raid/{raid_id}` - Link decision to RAID

**RAID Register:**

- `GET /projects/{key}/raid` - List/filter RAID items
- `GET /projects/{key}/raid/{id}` - Get RAID item
- `POST /projects/{key}/raid` - Create RAID item
- `PUT /projects/{key}/raid/{id}` - Update RAID item
- `DELETE /projects/{key}/raid/{id}` - Delete RAID item
- `POST /projects/{key}/raid/{id}/link-decision/{decision_id}` - Link RAID to decision
- `GET /projects/{key}/raid/by-decision/{decision_id}` - Get RAID items by decision

### Documentation

For detailed information, see:

- [Governance Documentation](docs/governance.md) - Complete governance backbone guide
- [RAID Register Documentation](docs/raid_register.md) - Comprehensive RAID register reference

## Troubleshooting

### API Container Issues

```bash
# Check API logs
docker compose logs api

# Verify /projectDocs is accessible
docker compose exec api ls -la /projectDocs
```

### LLM Connection Issues

```bash
# Test LLM endpoint
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local-model","messages":[{"role":"user","content":"test"}]}'
```

### Frontend Not Loading

```bash
# Check web container logs
docker compose logs web

# Verify nginx config
docker compose exec web cat /etc/nginx/conf.d/default.conf
```

## License

This project is part of the AI-Agent-Framework repository.

## Contributing

We follow a **Plan → Issues → PRs** workflow for all contributions. Please review our development guidelines before starting:

**📋 Essential Reading:**

- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Complete development guide and workflow
- **[.github/prompts/](.github/prompts/)** - Templates for planning, issues, and PRs
- **[docs/development.md](docs/development.md)** - Detailed development documentation

**Quick Contribution Steps:**

1. **Plan**: Start with a clear spec (goal, scope, acceptance criteria)
2. **Create Issue**: Use [issue template](.github/prompts/drafting-issue.md) with validation steps
3. **Implement**: One issue per PR, keep changes small (< 200 lines preferred)
4. **Validate**: Run linting, builds, and tests per [validation steps](.github/copilot-instructions.md#validation-steps-backend---ai-agent-framework)
5. **Submit PR**: Use [PR template](.github/prompts/drafting-pr.md) with copy-pasteable validation commands
6. **Review & Merge**: Squash merge preferred

### PR Process & Validation (Required)

CI enforces that your PR description follows the required checklist/sections and includes evidence that validation was actually run.

Minimum local validation for backend changes:

```bash
./setup.sh
source .venv/bin/activate

# Format + lint (recommended)
./scripts/format_and_lint_backend.sh

# Or individually (CI equivalent)
python -m black apps/api --check
python -m flake8 apps/api

# Tests
python -m pytest -q
```

**Key Guidelines:**

- **Never commit** `projectDocs/` or `configs/llm.json` (auto-ignored)
- Always set `PROJECT_DOCS_PATH=../../projectDocs` when running API locally
- Add runtime dependencies to **both** `requirements.txt` files (root and `apps/api/`)
- Test with both local venv (`./setup.sh`) and Docker before submitting
- **Automated tests:** Add tests (unit/integration/E2E) when requested by issues or features - see `tests/README.md`
- For cross-repo changes (backend + frontend), see [coordination guide](.github/prompts/cross-repo-coordination.md)

---

**Target Branch:** `main`  
**Version:** 1.0.0 MVP
