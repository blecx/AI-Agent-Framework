# Quick Start Guide

This guide shows you how to get the ISO 21500 Project Management AI Agent system up and running.

## Prerequisites

- Docker and Docker Compose installed
- (Optional) LM Studio or another OpenAI-compatible LLM running locally

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

### 2. Create Project Documents Directory

```bash
mkdir projectDocs
```

This directory will be automatically initialized as a git repository by the API on first run.

### 3. (Optional) Configure LLM

The system works with or without an LLM. Without an LLM, it will use fallback template-based generation.

To use an LLM, create or edit `configs/llm.json`:

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

For LM Studio:
1. Download and install LM Studio
2. Load a model (e.g., CodeLlama, Mistral, or any chat model)
3. Start the local server (Server tab → Start Server)
4. Use the config above (default)

For OpenAI:
```json
{
  "provider": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "your-openai-api-key",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### 4. Start the Services

```bash
docker compose up --build
```

This will:
- Build the FastAPI backend
- Build the React frontend
- Start both services
- Initialize the `/projectDocs` git repository if needed

### 5. Access the Application

- **Web UI**: http://localhost:8080
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Client CLI**: Use `docker compose run client <command>`

### 6. (Optional) Try the CLI Client

The client provides command-line access to all API operations:

```bash
# Show help and available commands
docker compose run client --help

# Create a project via CLI
docker compose run client create-project --key CLI001 --name "CLI Test Project"

# List all projects
docker compose run client list-projects

# Run a complete demo workflow
docker compose run client demo --key DEMO001 --name "Demo via CLI"
```

For detailed client usage, see [client/README.md](client/README.md).

## Using the System

You can interact with the system in two ways:

1. **Web UI** (http://localhost:8080) - Visual interface for interactive use
2. **CLI Client** - Command-line interface for automation and scripting

### Using the Web UI

### Create a Project

1. Open http://localhost:8080
2. Click "Create New Project"
3. Enter a project key (e.g., `PROJ001`) - alphanumeric, dashes, underscores only
4. Enter a project name (e.g., `Website Redesign`)
5. Click "Create Project"

### Run Commands

The system supports three main commands:

#### 1. Assess Gaps

Analyzes your project against ISO 21500 standards and identifies missing artifacts.

1. Click the "Assess Gaps" card
2. Click "Propose Changes"
3. Review the gap assessment report in the modal
4. Click "Apply & Commit" to save the report

#### 2. Generate Artifact

Creates specific project management documents.

1. Click the "Generate Artifact" card
2. Enter the artifact name (e.g., `project_charter.md`)
3. Enter the artifact type (e.g., `project_charter`)
4. Click "Propose Changes"
5. Review the generated document
6. Click "Apply & Commit" to save

#### 3. Generate Plan

Creates a project schedule with timeline and Mermaid gantt chart.

1. Click the "Generate Plan" card
2. Click "Propose Changes"
3. Review the generated schedule
4. Click "Apply & Commit" to save

### View Artifacts

1. Click the "Artifacts" tab
2. See all generated documents
3. Click any artifact to view its content

### View Project Documents

All project documents are stored in `./projectDocs/` as a separate git repository:

```bash
cd projectDocs
git log                    # View commit history
ls -la PROJ001/           # View project files
cat PROJ001/project.json  # View project metadata
```

### Using the CLI Client

The CLI client provides an alternative way to interact with the system:

```bash
# Create a project
docker compose run client create-project --key CLI001 --name "CLI Project"

# Check project state
docker compose run client get-state --key CLI001

# Propose assess_gaps command
docker compose run client propose --key CLI001 --command assess_gaps

# Note the proposal_id from output, then apply it
docker compose run client apply --key CLI001 --proposal-id <proposal-id>

# List artifacts
docker compose run client list-artifacts --key CLI001

# View artifact content
docker compose run client get-artifact --key CLI001 --path artifacts/gap_assessment.md

# Or run a complete demo workflow
docker compose run client demo --key DEMO001 --name "Automated Demo"
```

**When to use CLI vs Web UI:**

- **Use Web UI** for: Interactive project management, visual diff review, artifact browsing
- **Use CLI** for: Automation, scripting, CI/CD integration, batch operations

For more CLI examples and detailed documentation, see [client/README.md](client/README.md).

## Troubleshooting

### API Cannot Connect to LLM

If you see `[LLM unavailable: ...]` messages:

1. Ensure your LLM server is running
2. Check the `base_url` in `configs/llm.json`
3. For LM Studio, verify it's on port 1234
4. The system will still work with template-based fallbacks

### Docker Build Fails

If you encounter SSL certificate errors during build:

```bash
# Rebuild with no cache
docker compose build --no-cache

# Or use the API Dockerfile's trusted host flags (already included)
```

### Ports Already in Use

If ports 8000 or 8080 are already in use:

```bash
# Stop the services
docker compose down

# Edit docker-compose.yml to use different ports
# Then restart
docker compose up --build
```

### Cannot Access from Host

If using LM Studio and the API can't reach it:

- Ensure LM Studio is running on the host machine
- The URL `http://host.docker.internal:1234` should work on Docker Desktop
- On Linux, you may need to use `http://172.17.0.1:1234` or your host IP

## Advanced Usage

## Local Development (without Docker)

If you prefer to develop without Docker, you can run the application directly on your local machine using a Python virtual environment.

### Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **Git**
- **Node.js 18+** (for web UI)
- (Optional) LM Studio or OpenAI-compatible LLM endpoint

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

2. **Run the intelligent setup script:**

The setup script automatically detects available Python versions, lets you choose one, and sets up your environment.

**Linux/macOS:**
```bash
./setup.sh
```

**Windows (PowerShell - Recommended):**
```powershell
.\setup.ps1
```

**Windows (Command Prompt):**
```cmd
setup.bat
```

**Script features:**
- 🔍 Auto-detects all Python 3.x versions on your system
- 📋 Shows compatible versions (3.10+) with their installation paths
- ✅ Prompts you to select a version or auto-selects if only one found
- 🔒 Validates minimum version requirements (Python 3.10+)
- 📦 Creates `.venv/` with your selected Python version
- ⬆️ Upgrades pip and installs all dependencies
- 💡 Provides helpful download links if no compatible version found

This will:
- Create a virtual environment in `.venv/`
- Install all Python dependencies
- Display next steps

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

5. **Configure LLM (optional):**
```bash
cp configs/llm.default.json configs/llm.json
# Edit configs/llm.json with your LLM settings
```

For local LLM (LM Studio):
- Ensure LM Studio is running on `http://localhost:1234`
- Update `configs/llm.json`:
  ```json
  {
    "provider": "lmstudio",
    "base_url": "http://localhost:1234/v1",
    "api_key": "lm-studio",
    "model": "local-model"
  }
  ```

6. **Run the API server:**
```bash
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

The API will be available at:
- http://localhost:8000
- API Docs: http://localhost:8000/docs

7. **(Optional) Run the Web UI:**
```bash
# In a new terminal
cd apps/web
npm install
npm run dev
```

The web UI will be available at http://localhost:5173

### When to Use Local Development vs Docker

**Use Local Development (.venv) when:**
- You're actively developing and debugging code
- You need faster iteration cycles
- You want to use your IDE's debugger
- You need to inspect or modify dependencies
- You're running on a development machine

**Use Docker when:**
- You want a consistent environment across team members
- You're deploying to production
- You need to test the full system integration
- You want isolated environments
- You're distributing the application to others

### Switching Between Local and Docker

You can easily switch between local and Docker development:

**To Docker:**
```bash
deactivate  # Exit virtual environment if active
docker compose up --build
```

**To Local:**
```bash
docker compose down
source .venv/bin/activate  # or .venv\Scripts\activate.bat on Windows
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

---

## Docker Deployment (Production)

For production deployment or if you prefer Docker, continue using the Docker setup described in the earlier sections of this guide.

### Customizing Templates

Edit templates in:
- `templates/prompts/iso21500/` - Jinja2 prompts for LLM
- `templates/output/iso21500/` - Markdown output templates

### Audit Logging

Audit events are stored in:
```
projectDocs/[PROJECT_KEY]/events/events.ndjson
```

By default, only hashes are logged (no sensitive content). To enable full logging, modify the `log_content` parameter in `apps/api/routers/commands.py`.

## Security Notes

- Never commit the `projectDocs/` directory to your code repository
- Store API keys securely (use environment variables or mounted config files)
- The default configuration logs only hashes, not actual prompts or content
- Review the `.gitignore` file to ensure sensitive files are excluded

## Next Steps

- Review the full [README.md](README.md) for detailed architecture information
- Explore the API documentation at http://localhost:8000/docs
- Customize templates for your specific needs
- Integrate with CI/CD pipelines for automated project management

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed documentation
- Review API logs: `docker compose logs api`
- Review web logs: `docker compose logs web`
- Check the GitHub repository for updates
