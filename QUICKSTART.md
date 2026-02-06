# Quick Start Guide

This guide shows you how to get the ISO 21500 Project Management AI Agent system up and running.

> **💡 Multi-Repository Project:** This project includes a separate client repository at [AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client). For full-stack development, see the [Development Guide](docs/development.md#cross-repository-coordination) for cross-repo workflow.

## Prerequisites

- Docker and Docker Compose installed
- (Optional) LM Studio or another OpenAI-compatible LLM running locally

### System Requirements

**For Web UI (Browser-based):**
- Desktop browser: Chrome, Firefox, Edge, or Safari (latest versions)
- Minimum screen resolution: 1280x720
- Mouse and keyboard recommended

**Mobile/Tablet Support:**
- ⚠️ Tablets (iPad, Android 10"+): Limited support, landscape mode only, read-only recommended
- ❌ Smartphones: Not supported (screen too small for UI)
- See [Mobile Compatibility Guide](docs/clients/README.md#mobile-browser-compatibility) for details

**For TUI/CLI:**
- Terminal with color support
- SSH access (for remote use)
- Works on any device with terminal access (including mobile via SSH)

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

### 2. Project Documents Directory

By default the compose configuration uses a Docker named volume for project documents so no manual step is required.

If you prefer to keep project documents on your host filesystem, create the directory before starting services:

```bash
# Optional: create host directory for persistent docs (only needed if you want host-managed files)
mkdir -p projectDocs
```

The API will initialize the repository inside the docs directory on first run.

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

- **Web UI**: <http://localhost:8080>
- **API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **Client CLI**: Use `docker compose run client <command>`

### 6. (Optional) Try the Client

The client provides both interactive (TUI) and command-line (CLI) access:

#### 🖥️ Terminal User Interface (NEW!)

Launch an interactive visual interface:

```bash
# Launch TUI (default)
docker compose run client

# Or explicitly
docker compose run client tui
```

Navigate with keyboard/mouse, manage projects, run commands, and view artifacts in real-time!

#### 📟 Command Line Interface

Traditional CLI for automation:

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

## Choosing the Right Client

The AI-Agent Framework offers multiple interfaces to match your workflow:

### Available Clients

1. **TUI (Text User Interface)** - `apps/tui/` - Command-line client for automation
2. **Advanced Client** - `client/` - CLI + interactive terminal UI (with Textual)
3. **WebUI** - Separate repository - Modern web-based graphical interface

### Decision Guide

**Use TUI (`apps/tui/`) when:**

- ✅ Running in CI/CD pipelines
- ✅ Writing automation scripts
- ✅ Need simple, fast command-line operations
- ✅ Working in minimal environments

**Use Advanced Client (`client/`) when:**

- ✅ Working in terminal/SSH sessions but want visual navigation
- ✅ Need interactive feedback in terminal
- ✅ Debugging or testing the API
- ✅ Want both CLI scripting and interactive TUI modes

**Use WebUI (separate repo) when:**

- ✅ Need rich visual interface
- ✅ Managing projects interactively
- ✅ Working with non-technical team members
- ✅ Want visual diff review and artifact preview

## Getting Started with TUI

The TUI client is a simple command-line tool included in this repository.

**Docker:**

```bash
# Show help
docker compose run tui --help

# Create project
docker compose run tui projects create --key PROJ001 --name "My Project"

# List projects
docker compose run tui projects list

# Propose command
docker compose run tui commands propose --project PROJ001 --command assess_gaps
```

**Local:**

```bash
cd apps/tui
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py health
```

**Full documentation:** [apps/tui/README.md](apps/tui/README.md)

## Getting Started with Advanced Client

The advanced client provides both CLI and interactive TUI modes.

**Docker (Interactive TUI):**

```bash
# Launch interactive TUI (default)
docker compose run client

# Or explicitly
docker compose run client tui
```

**Docker (CLI mode):**

```bash
# Run CLI commands
docker compose run client --help
docker compose run client create-project --key TEST001 --name "Test"
docker compose run client demo --key DEMO001 --name "Demo Project"
```

**Local:**

```bash
cd client
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.client tui  # Interactive mode
python -m src.client health  # CLI mode
```

**Full documentation:** [client/README.md](client/README.md)

## Next Steps

Now that you have the system running, here's where to go next:

### Learn Through Tutorials

Our comprehensive tutorial suite will teach you everything from basics to advanced workflows:

**🌱 Beginner Path (60 minutes):**

- [TUI Quick Start](docs/tutorials/tui-basics/01-quick-start.md) - Docker setup and basic commands (5 min)
- [First Project](docs/tutorials/tui-basics/02-first-project.md) - Create your first project (10 min)
- [Web Interface Basics](docs/tutorials/gui-basics/01-web-interface.md) - Navigate the web UI (5 min)
- [Complete Beginner Path](docs/tutorials/README.md#-beginner-path-60-minutes) - Full guided tour

**🚀 Intermediate Path (110 minutes):**

- Learn workflow management and ISO 21500 lifecycle
- [View Intermediate Path](docs/tutorials/README.md#-intermediate-path-110-minutes)

**🎯 Advanced Path (220 minutes):**

- Master hybrid workflows and automation
- [View Advanced Path](docs/tutorials/README.md#-advanced-path-220-minutes)

**📚 All Tutorials:** [docs/tutorials/README.md](docs/tutorials/README.md)

### Explore the System

After tutorials, dive deeper into capabilities:

## Getting Started with WebUI

The WebUI is a **separate repository** with a modern React-based interface.

**Repository:** [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)

**Quick Start:**

1. Clone the WebUI repository:

   ```bash
   git clone https://github.com/blecx/AI-Agent-Framework-Client.git
   ```

2. Follow the setup instructions in the WebUI repository's README

3. Ensure the AI-Agent-Framework API is running (this repository)

4. Configure the WebUI to connect to your API endpoint

**Note:** The Docker setup in this repository already includes a web frontend at `apps/web/`. The separate WebUI repository provides an alternative, enhanced interface with additional features.

**When to use each web interface:**

- **`apps/web/`** (included): Quick setup, basic features, integrated deployment
- **Separate WebUI repo**: Enhanced features, independent updates, customizable

For detailed WebUI setup and features, visit: [https://github.com/blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)

## Using the System

You can interact with the system through multiple interfaces. Below are examples using the included web UI and clients.

### Using the Web UI (Included)

#### Create a Project

1. Open <http://localhost:8080>
2. Click "Create New Project"
3. Enter a project key (e.g., `PROJ001`) - alphanumeric, dashes, underscores only
4. Enter a project name (e.g., `Website Redesign`)
5. Click "Create Project"

#### Run Commands

The system supports three main commands:

##### 1. Assess Gaps

Analyzes your project against ISO 21500 standards and identifies missing artifacts.

1. Click the "Assess Gaps" card
2. Click "Propose Changes"
3. Review the gap assessment report in the modal
4. Click "Apply & Commit" to save the report

##### 2. Generate Artifact

Creates specific project management documents.

1. Click the "Generate Artifact" card
2. Enter the artifact name (e.g., `project_charter.md`)
3. Enter the artifact type (e.g., `project_charter`)
4. Click "Propose Changes"
5. Review the generated document
6. Click "Apply & Commit" to save

##### 3. Generate Plan

Creates a project schedule with timeline and Mermaid gantt chart.

1. Click the "Generate Plan" card
2. Click "Propose Changes"
3. Review the generated schedule
4. Click "Apply & Commit" to save

#### View Artifacts

1. Click the "Artifacts" tab
2. See all generated documents
3. Click any artifact to view its content

#### View Project Documents

All project documents are stored in `./projectDocs/` as a separate git repository:

```bash
cd projectDocs
git log                    # View commit history
ls -la PROJ001/           # View project files
cat PROJ001/project.json  # View project metadata
```

### Using the CLI Clients

Both the TUI and Advanced Client provide command-line access for automation:

#### Using the CLI Clients

Both the TUI and Advanced Client provide command-line access for automation.

**TUI Client (`apps/tui/`)** - Simple CLI:

```bash
# Create a project
docker compose run tui projects create --key PROJ001 --name "My Project"

# List projects
docker compose run tui projects list

# Propose command
docker compose run tui commands propose --project PROJ001 --command assess_gaps

# Apply proposal
docker compose run tui commands apply --project PROJ001 --proposal <proposal-id>
```

**Advanced Client (`client/`)** - CLI + Interactive TUI:

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

**Client Usage Summary:**

| Client                          | Best For                                  | Documentation                                                          |
| ------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------- |
| **TUI** (`apps/tui/`)           | Simple CLI automation, quick commands     | [apps/tui/README.md](apps/tui/README.md)                               |
| **Advanced Client** (`client/`) | Interactive terminal + CLI, rich feedback | [client/README.md](client/README.md)                                   |
| **WebUI** (separate repo)       | Visual interface, team collaboration      | [WebUI Repository](https://github.com/blecx/AI-Agent-Framework-Client) |

For more examples and detailed documentation, see the respective client README files.

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

- **Python 3.12** (matches GitHub Actions CI)
- **Git**
- **Node.js 18+** (for web UI)
- (Optional) LM Studio or OpenAI-compatible LLM endpoint

### Setup Steps

1. **Clone the repository:**

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

1. **Run the intelligent setup script:**

The setup script uses Python 3.12 to create the virtual environment and sets up your environment.

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

- 🔍 Detects Python 3.12 on your system
- 🔒 Fails fast with install instructions if Python 3.12 is missing
- 📦 Creates `.venv/` with Python 3.12
- ⬆️ Upgrades pip and installs all dependencies
- 💡 Provides helpful install instructions if Python 3.12 is missing

This will:

- Create a virtual environment in `.venv/`
- Install all Python dependencies
- Display next steps

1. **Activate the virtual environment:**

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

1. **Create project documents directory:**

```bash
mkdir projectDocs
```

1. **Configure LLM (optional):**

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

1. **Run the API server:**

```bash
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

The API will be available at:

- <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

1. **(Optional) Run the Web UI:**

```bash
# In a new terminal
cd apps/web
npm install
npm run dev
```

The web UI will be available at <http://localhost:5173>

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
- Explore the API documentation at <http://localhost:8000/docs>
- Customize templates for your specific needs
- Integrate with CI/CD pipelines for automated project management

## Support

For issues or questions:

- Check the [README.md](README.md) for detailed documentation
- Review API logs: `docker compose logs api`
- Review web logs: `docker compose logs web`
- Check the GitHub repository for updates
