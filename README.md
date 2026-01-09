# AI-Agent-Framework

An ISO 21500 Project Management AI Agent System with FastAPI backend and React/Vite frontend, deployed as Docker containers.

## Overview

This system provides intelligent project management following ISO 21500 standards. It features:

- **FastAPI Backend**: Handles project management logic, LLM interactions, and git-based document storage
- **React/Vite Frontend**: Modern UI for project creation, command execution, and artifact management
- **Docker Deployment**: Two-container setup for easy deployment
- **Git-based Storage**: All project documents stored in a separate git repository with full version history

## Architecture

### Backend (FastAPI)
- LLM abstraction with OpenAI-compatible HTTP adapter
- Git repository manager for project documents
- Command orchestration with propose/apply workflow
- Audit logging with NDJSON format
- Template-driven artifact generation

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

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) LM Studio or OpenAI-compatible LLM endpoint

### Setup

1. Clone this repository:
```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

2. Create project documents directory:
```bash
mkdir projectDocs
```

3. (Optional) Configure LLM settings:
```bash
# Copy and edit the LLM config
cp configs/llm.default.json configs/llm.json
# Edit configs/llm.json with your LLM endpoint details
```

The default configuration uses LM Studio on `http://host.docker.internal:1234/v1`.

4. Start the services:
```bash
docker compose up --build
```

5. Access the application:
- Web UI: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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
│   └── web/                   # React/Vite frontend
│       └── src/
│           ├── components/    # React components
│           └── services/      # API client
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

The system uses a JSON configuration file for LLM settings. Create `configs/llm.json` to override defaults:

```json
{
  "provider": "lmstudio",
  "base_url": "http://host.docker.internal:1234/v1",
  "api_key": "lm-studio",
  "model": "local-model",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 120
}
```

### Supported LLM Providers

Any OpenAI-compatible endpoint works:
- LM Studio (default)
- OpenAI API
- Azure OpenAI
- Ollama with OpenAI compatibility
- LocalAI
- Text Generation WebUI (with OpenAI extension)

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

### Running Locally (without Docker)

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

### Adding New Commands

1. Add command logic to `apps/api/services/command_service.py`
2. Create prompt template in `templates/prompts/iso21500/`
3. Create output template in `templates/output/iso21500/`
4. Update frontend `CommandPanel.jsx` with new command

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

1. Create a feature branch
2. Make your changes
3. Test with `docker compose up --build`
4. Submit a pull request

---

**Target Branch:** `main`  
**Version:** 1.0.0 MVP
