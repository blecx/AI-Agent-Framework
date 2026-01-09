# AI-Agent-Framework

An ISO 21500 Project Management AI Agent System with FastAPI backend and React/Vite frontend, deployed as Docker containers.

## Overview

This system provides intelligent project management following ISO 21500 standards. It features:

- **FastAPI Backend**: Handles project management logic, LLM interactions, and git-based document storage
- **React/Vite Frontend**: Modern UI for project creation, command execution, and artifact management
- **Docker Deployment**: Two-container setup for easy deployment
- **Git-based Storage**: All project documents stored in a separate git repository with full version history

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

| Client | Use Case | Automation | Visual Interface | Setup Complexity |
|--------|----------|------------|------------------|------------------|
| **TUI** | CLI automation, scripts | ✅ Excellent | 📟 Command-line | 🟢 Simple |
| **Client** | Terminal workflows | ✅ Good | 🖥️ Interactive terminal | 🟢 Simple |
| **WebUI** | Interactive management | ⚠️ Limited | 🌐 Full graphical UI | 🟡 Moderate |

All clients communicate with the same REST API, ensuring feature parity and flexibility.

## Quick Start

**📖 See [QUICKSTART.md](QUICKSTART.md) for a detailed step-by-step guide.**

## Local Development Setup

For local development without Docker, follow these steps:

### Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **Git**
- (Optional) LM Studio or OpenAI-compatible LLM endpoint

### Step-by-Step Setup

1. **Clone the repository:**
```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

2. **Run the intelligent setup script:**

The setup script will automatically detect all available Python versions on your system, prompt you to select one, validate that it meets the minimum requirements, and create a virtual environment.

**Linux/macOS:**
```bash
./setup.sh
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Windows (Command Prompt):**
```cmd
setup.bat
```

**What the script does:**
- 🔍 Detects all available Python 3.x versions on your system
- 📋 Shows you a list of compatible versions (3.10+) with their paths
- ✅ Prompts you to select a version (or auto-selects if only one is found)
- 🔒 Validates the selected version meets minimum requirements
- 📦 Creates a Python virtual environment in `.venv/` using your selected version
- ⬆️ Upgrades pip to the latest version
- 📥 Installs all required dependencies from `requirements.txt`
- ✨ Displays next steps for running the application

If no compatible Python version is found, the script will display download links and helpful error messages.

3. **Activate the virtual environment:**

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

4. **Create project documents directory:**
```bash
mkdir projectDocs
```

5. **Configure LLM settings (optional):**
```bash
cp configs/llm.default.json configs/llm.json
# Edit configs/llm.json with your LLM endpoint details
```

6. **Run the API server:**
```bash
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

7. **Access the application:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Note:** For the web UI, you'll need to run it separately (see Web UI section below) or use Docker.

### Manual Setup (Alternative)

If you prefer not to use the setup script, you can set up manually:

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate and install dependencies:**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate.bat on Windows
   
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Running the Web UI (Optional)

If you want to run the React frontend locally:

```bash
cd apps/web
npm install
npm run dev
```

The web UI will be available at http://localhost:5173 (or the port shown in the terminal).

### Docker Deployment Setup

For production or simplified deployment using Docker:

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

This will start all three services:
- API server (backend)
- Web UI (frontend)
- Client (CLI tool - optional)

5. Access the application:
- Web UI: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Client: `docker compose run client <command>` (see Client Usage below)

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
   cd apps/web
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
