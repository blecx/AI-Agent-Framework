# AI Agent API Client

A standalone Python client for consuming the AI Agent REST API. Features both a Terminal User Interface (TUI) for interactive use and a command-line interface (CLI) for automation and scripting.

## Interfaces

### 🖥️ Terminal User Interface (TUI) - NEW!

An interactive, visual terminal interface built with Textual:

- **Visual Navigation**: Navigate through menus and screens with keyboard or mouse
- **Project Management**: Browse projects, create new ones, view details
- **Command Execution**: Run commands with real-time feedback
- **Artifact Viewing**: Browse and view generated artifacts
- **Real-time Updates**: See command output and results as they happen

**Launch the TUI:**
```bash
# Using Docker
docker compose run client tui

# Using local Python
python -m src.client tui
```

### 📟 Command Line Interface (CLI)

Traditional CLI for automation and scripting:

- **Scriptable**: Use in bash scripts and automation
- **CI/CD Ready**: Perfect for automated pipelines
- **Batch Operations**: Process multiple operations
- **Output Parsing**: JSON-friendly output for scripting

## Purpose

The AI Agent API Client serves as:

- **Interactive Tool**: TUI for hands-on project management
- **API Consumer**: Demonstrates how to interact with the AI Agent API
- **Automation Tool**: CLI enables scripting and batch operations
- **CI/CD Integration**: Can be used in automated pipelines
- **Testing Tool**: Useful for API testing and validation
- **Independent Component**: Runs separately from the main application

## Architecture

The client is completely independent from the AI Agent application:

- **No shared code**: Uses only the REST API interface
- **Separate container**: Runs in its own Docker container
- **API-first design**: Validates the API-first architecture
- **Optional component**: Not required for core functionality
- **Dual interface**: TUI for interactivity, CLI for automation

## Features

The client supports all major API operations in both TUI and CLI modes:

- ✅ **Health Check**: Verify API availability
- ✅ **Project Management**: Create and list projects
- ✅ **State Queries**: Get project state and metadata
- ✅ **Command Proposal**: Preview changes before applying
- ✅ **Command Apply**: Execute and commit changes
- ✅ **Artifacts**: List and retrieve project artifacts
- ✅ **Demo Workflow**: Run complete end-to-end workflow (CLI only)
- ✅ **Interactive TUI**: Visual interface for all operations (NEW!)

## Installation

### Option 1: Docker (Recommended)

Using Docker Compose (from repository root):

```bash
# Launch the TUI (default)
docker compose run client

# Or explicitly launch TUI
docker compose run client tui

# Use CLI commands
docker compose run client --help
docker compose run client create-project --key TEST001 --name "Test Project"
```

### Option 2: Local Python Environment

Requirements:
- Python 3.10+
- pip

Setup:

```bash
cd client

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The client uses environment variables for configuration.

### Create .env file

```bash
cp .env.example .env
# Edit .env with your settings
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | AI Agent API base URL | `http://localhost:8000` |
| `API_TIMEOUT` | Request timeout in seconds | `30` |

### Docker Configuration

When running via Docker Compose, the API URL is automatically set to `http://api:8000` (Docker network).

When running locally, use `http://localhost:8000` (or the appropriate host).

## Usage

### TUI (Terminal User Interface) - Interactive Mode

The TUI provides a visual, menu-driven interface:

**Launch the TUI:**
```bash
# Using Docker
docker compose run client tui

# Using local Python
python -m src.client tui
```

**TUI Features:**

1. **Main Menu**
   - 📁 Projects: Browse and manage projects
   - ❤️ Health Check: Verify API status
   - ❌ Exit: Close the application

2. **Project Management**
   - List all projects with details
   - Create new projects with forms
   - Select projects to view details

3. **Project Details (Tabbed Interface)**
   - **Info Tab**: View project metadata (name, key, dates)
   - **Commands Tab**: Run commands (Assess Gaps, Generate Artifact, Generate Plan)
   - **Artifacts Tab**: Browse generated artifacts

4. **Command Execution**
   - Propose commands with real-time feedback
   - Review proposed changes
   - Apply changes and commit to repository

**Keyboard Shortcuts:**
- `q` - Quit application
- `d` - Toggle dark/light mode
- `Escape` - Go back/cancel
- `Tab` - Navigate between elements
- Arrow keys - Navigate menus and lists
- `Enter` - Select/activate

**Mouse Support:**
- Click buttons to activate
- Click table rows to select
- Scroll through content

### CLI (Command Line Interface) - Scripting Mode

The CLI provides traditional command-line access for automation:

### Command Overview

```bash
# Show all commands
python -m src.client --help

# Launch TUI
python -m src.client tui

# Check API health
python -m src.client health

# Create a new project
python -m src.client create-project --key PROJ001 --name "My Project"

# List all projects
python -m src.client list-projects

# Get project state
python -m src.client get-state --key PROJ001

# Propose a command (preview changes)
python -m src.client propose --key PROJ001 --command assess_gaps

# Apply a proposal
python -m src.client apply --key PROJ001 --proposal-id <proposal-id>

# List artifacts
python -m src.client list-artifacts --key PROJ001

# Get artifact content
python -m src.client get-artifact --key PROJ001 --path artifacts/gap_assessment.md

# Run complete demo workflow
python -m src.client demo --key DEMO001 --name "Demo Project"
```

### Example Workflows

#### Workflow 1: Create Project and Assess Gaps

```bash
# 1. Create project
python -m src.client create-project --key PROJ001 --name "Website Redesign"

# 2. Assess gaps (propose)
python -m src.client propose --key PROJ001 --command assess_gaps

# Note the proposal_id from output, then apply:
# 3. Apply the proposal
python -m src.client apply --key PROJ001 --proposal-id <proposal-id>

# 4. View artifacts
python -m src.client list-artifacts --key PROJ001
```

#### Workflow 2: Generate Artifact

```bash
# 1. Propose artifact generation
python -m src.client propose \
  --key PROJ001 \
  --command generate_artifact \
  --artifact-name project_charter.md \
  --artifact-type project_charter

# 2. Apply the proposal
python -m src.client apply --key PROJ001 --proposal-id <proposal-id>

# 3. View the artifact
python -m src.client get-artifact --key PROJ001 --path artifacts/project_charter.md
```

#### Workflow 3: Generate Project Plan

```bash
# 1. Propose plan generation
python -m src.client propose --key PROJ001 --command generate_plan

# 2. Apply the proposal
python -m src.client apply --key PROJ001 --proposal-id <proposal-id>

# 3. View the schedule
python -m src.client get-artifact --key PROJ001 --path artifacts/schedule.md
```

#### Workflow 4: Quick Demo (Automated)

```bash
# Run complete workflow automatically
python -m src.client demo --key DEMO001 --name "Demo Project"

# Without gaps assessment
python -m src.client demo --key DEMO002 --name "Another Demo" --no-run-gaps
```

## Docker Usage

### Running via Docker Compose

From the repository root:

```bash
# Show help
docker compose run client --help

# Health check
docker compose run client health

# Create project
docker compose run client create-project --key TEST001 --name "Test"

# List projects
docker compose run client list-projects

# Run demo
docker compose run client demo --key DEMO001 --name "Demo"
```

### Running Standalone Container

```bash
# Build the image
docker build -t ai-agent-client ./client

# Run with custom API URL
docker run --rm \
  -e API_BASE_URL=http://your-api-host:8000 \
  ai-agent-client health

# Run interactively
docker run --rm -it ai-agent-client /bin/bash
```

## Local Development

### Running Locally

1. Ensure the API is running (locally or via Docker)
2. Configure `.env` with correct `API_BASE_URL`
3. Run commands:

```bash
cd client
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run commands
python -m src.client health
python -m src.client list-projects
```

### Testing with Local API

If running the API locally (not Docker):

```bash
# Terminal 1: Start API
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Terminal 2: Use client
cd client
export API_BASE_URL=http://localhost:8000  # or edit .env
python -m src.client health
```

### Testing with Docker API

If the API is running in Docker:

```bash
# Start API via Docker Compose
docker compose up api

# In another terminal, use client locally
cd client
export API_BASE_URL=http://localhost:8000
python -m src.client health
```

## API Commands Reference

### Projects

- `create-project`: Create a new project
  - `--key`: Project key (required, alphanumeric with dashes/underscores)
  - `--name`: Project name (required)

- `list-projects`: List all projects

- `get-state`: Get project state
  - `--key`: Project key (required)

### Commands

- `propose`: Propose a command (preview changes)
  - `--key`: Project key (required)
  - `--command`: Command name (required): `assess_gaps`, `generate_artifact`, `generate_plan`
  - `--artifact-name`: For `generate_artifact` only
  - `--artifact-type`: For `generate_artifact` only

- `apply`: Apply a command proposal
  - `--key`: Project key (required)
  - `--proposal-id`: Proposal ID from propose command (required)

### Artifacts

- `list-artifacts`: List project artifacts
  - `--key`: Project key (required)

- `get-artifact`: Get artifact content
  - `--key`: Project key (required)
  - `--path`: Artifact path (required)

### Utilities

- `health`: Check API health status

- `demo`: Run complete demo workflow
  - `--key`: Project key (required)
  - `--name`: Project name (required)
  - `--run-gaps/--no-run-gaps`: Run assess_gaps after project creation (default: yes)

- `tui`: Launch Terminal User Interface (NEW!)
  - Interactive visual interface
  - Menu-driven navigation
  - Real-time feedback

## When to Use TUI vs CLI vs Web UI

### Use the TUI (Terminal User Interface) for:

- 🖥️ **Interactive Terminal Work**: When you prefer visual navigation in a terminal
- 🎯 **Quick Tasks**: Fast access to common operations without typing commands
- 📊 **Real-time Feedback**: See command execution and results as they happen
- 🚀 **Learning**: Discover features through menus and visual guidance
- 🔄 **Workflow Management**: Navigate between projects and commands easily
- 💻 **SSH/Remote Sessions**: Full functionality over terminal-only connections

### Use the CLI (Command Line) for:

- 🤖 **Automation**: Scripting repetitive tasks
- 🔧 **CI/CD Integration**: Automated project management in pipelines
- 📦 **Batch Operations**: Processing multiple projects
- 🧪 **API Testing**: Validating API functionality
- 📝 **Documentation**: Command examples in docs and tutorials
- 🔌 **Integration**: Connecting to other tools and systems

### Use the Web UI for:

- 🌐 **Rich Visual Interface**: Full graphical experience with modern UI
- 👥 **Non-technical Users**: User-friendly for all skill levels
- 🔍 **Visual Review**: Detailed diff viewing and proposal comparison
- 🗂️ **Exploration**: Browse artifacts and project state visually
- 📱 **Cross-platform**: Access from any device with a browser
- 🎨 **Advanced Features**: Full feature set with visual enhancements

## Troubleshooting

### Cannot Connect to API

**Problem**: `Connection refused` or timeout errors

**Solutions**:
1. Verify API is running: `curl http://localhost:8000/health`
2. Check `API_BASE_URL` in `.env`
3. For Docker: Use `http://api:8000` (not `localhost`)
4. For local: Use `http://localhost:8000`

### HTTP 404 Errors

**Problem**: Project not found

**Solutions**:
1. Verify project exists: `python -m src.client list-projects`
2. Check project key spelling
3. Create project if needed: `python -m src.client create-project`

### HTTP 400 Errors

**Problem**: Invalid request parameters

**Solutions**:
1. Check required parameters are provided
2. Verify parameter format (e.g., project key pattern)
3. For `generate_artifact`, ensure `--artifact-name` and `--artifact-type` are provided

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solutions**:
1. Ensure virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Run from correct directory: `cd client`

## Development

### Adding New Commands

1. Add API client method in `src/client.py` (`APIClient` class)
2. Add CLI command function with `@cli.command()` decorator
3. Update this README with usage instructions

### Project Structure

```
client/
├── src/
│   ├── __init__.py           # Package init
│   ├── __main__.py           # Module entry point
│   └── client.py             # Main CLI implementation
├── Dockerfile                # Docker image definition
├── requirements.txt          # Python dependencies
├── .env.example              # Example configuration
└── README.md                 # This file
```

## Contributing

When contributing to the client:

1. Keep it independent from the main application
2. Use only the REST API (no shared code)
3. Update documentation for new features
4. Test both local and Docker usage
5. Follow existing CLI patterns (Click library)

## Security Notes

- Never commit `.env` files with real credentials
- Use environment variables for configuration
- The client does not store sensitive data
- All data is managed by the API server

## License

This client is part of the AI-Agent-Framework repository.

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review API documentation at `http://localhost:8000/docs`
- Check Docker logs: `docker compose logs client`

---

**Version**: 1.0.0  
**Part of**: AI-Agent-Framework  
**API Version**: 1.0.0
