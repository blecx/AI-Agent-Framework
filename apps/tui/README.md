# TUI Client - ISO 21500 AI-Agent Framework

A command-line interface (TUI - Text User Interface) for interacting with the ISO 21500 AI-Agent Framework API.

## Overview

The TUI client provides a simple, scriptable command-line interface for:
- Managing projects
- Proposing and applying commands
- Viewing and managing artifacts
- Running project audit checks
- Checking API health

## Features

- **Project Management**: Create projects, list all projects, view project details
- **Command Workflow**: Propose commands with preview, apply approved proposals
- **Artifact Access**: List and view project artifacts
- **Audit Command**: Run audit rules with severity summary and issue preview
- **Rich Output**: Formatted tables, syntax highlighting, and colored output
- **Docker Support**: Run via Docker or locally

## Installation

### Option 1: Docker (Recommended)

The TUI client can be run via Docker without any local Python setup:

```bash
# From repository root
docker compose build tui

# Run commands
docker compose run tui health
docker compose run tui projects list
```

### Option 2: Local Python

Requirements:
- Python 3.10 or higher
- pip

Setup:

```bash
cd apps/tui

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The TUI client uses environment variables for configuration.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | API endpoint URL | `http://localhost:8000` |
| `API_TIMEOUT` | Request timeout (seconds) | `30` |
| `API_KEY` | Optional API authentication key | _(empty)_ |

### Setting Environment Variables

**Local Development:**

```bash
export API_BASE_URL=http://localhost:8000
export API_TIMEOUT=60
```

Or create a `.env` file in `apps/tui/`:

```env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

**Docker:**

Environment variables are configured in `docker-compose.yml`. The default configuration uses `http://api:8000` to communicate with the API service in the Docker network.

## Usage

### Command Structure

```bash
python main.py [GROUP] [COMMAND] [OPTIONS]
```

### Available Commands

#### General

```bash
# Show help
python main.py --help

# Check API health
python main.py health
```

#### Project Management

```bash
# Create a project
python main.py projects create --key PROJ001 --name "My Project"

# Create a project with optional description
python main.py projects create --key PROJ001 --name "My Project" --description "Initial project context"

# List all projects
python main.py projects list

# List projects as JSON (for scripting)
python main.py projects list --format json

# Get project details and state
python main.py projects get --key PROJ001

# Soft-delete project
python main.py projects delete --key PROJ001
```

#### Command Workflow (Propose/Apply)

```bash
# Propose a command (preview changes)
python main.py commands propose --project PROJ001 --command assess_gaps

# Propose artifact generation
python main.py commands propose \
  --project PROJ001 \
  --command generate_artifact \
  --artifact-name project_charter.md \
  --artifact-type project_charter

# Propose plan generation
python main.py commands propose --project PROJ001 --command generate_plan

# Apply a proposal (commits changes)
python main.py commands apply --project PROJ001 --proposal <proposal-id>

# Apply without confirmation prompt
python main.py commands apply --project PROJ001 --proposal <proposal-id> -y
```

#### Proposals Management

```bash
# List proposals for a project
python main.py proposals list --project PROJ001

# List filtered proposals
python main.py proposals list --project PROJ001 --status pending --change-type update

# Get proposal details
python main.py proposals get --project PROJ001 --id <proposal-id>

# Apply a proposal
python main.py proposals apply --project PROJ001 --id <proposal-id>

# Reject a proposal with reason
python main.py proposals reject --project PROJ001 --id <proposal-id> --reason "Insufficient rationale"
```

#### Artifact Management

```bash
# List artifacts for a project
python main.py artifacts list --project PROJ001

# View artifact content
python main.py artifacts get --project PROJ001 --path artifacts/gap_assessment.md
```

#### RAID Management

```bash
# Add a RAID risk item
python main.py raid add \
  --project PROJ001 \
  --type risk \
  --title "Schedule risk" \
  --description "Vendor delivery may slip" \
  --owner "PM" \
  --priority high

# List RAID items
python main.py raid list --project PROJ001

# Filter RAID items
python main.py raid list --project PROJ001 --type risk --status open --priority high

# Get a RAID item by ID
python main.py raid get --project PROJ001 --id RISK001

# Update a RAID item
python main.py raid update --project PROJ001 --id RISK001 --status in_progress

# Delete a RAID item
python main.py raid delete --project PROJ001 --id RISK001
```

#### Workflow Management

```bash
# Get current workflow state
python main.py workflow state --project PROJ001

# Transition workflow state
python main.py workflow transition \
  --project PROJ001 \
  --to-state planning \
  --actor "PM" \
  --reason "Charter approved"

# Show allowed transitions from current state
python main.py workflow allowed-transitions --project PROJ001

# List workflow audit events
python main.py workflow audit-events --project PROJ001

# Filter workflow audit events
python main.py workflow audit-events \
  --project PROJ001 \
  --event-type workflow_state_changed \
  --actor "PM" \
  --limit 20 \
  --offset 0
```

#### Audit Command

```bash
# Run full audit for a project
python main.py audit --project PROJ001

# Run a subset of rules (repeat --rule)
python main.py audit --project PROJ001 --rule required_fields --rule workflow_state

# Limit displayed issues
python main.py audit --project PROJ001 --limit 5
```

#### Configuration Management

```bash
# Show current configuration
python main.py config show

# Set API URL
python main.py config set --api-url http://localhost:8000

# Set API key
python main.py config set --api-key your-secret-key

# Set both URL and key
python main.py config set --api-url http://api:8000 --api-key mykey

# Reset configuration to defaults
python main.py config reset
```

### Docker Usage

When using Docker, prefix commands with `docker compose run tui`:

```bash
# Health check
docker compose run tui health

# Create project
docker compose run tui projects create --key TEST001 --name "Test Project"

# Create project with description
docker compose run tui projects create --key TEST001 --name "Test Project" --description "Smoke test project"

# List projects
docker compose run tui projects list

# List projects as JSON
docker compose run tui projects list --format json

# Get project state
docker compose run tui projects get --key TEST001

# Delete project
docker compose run tui projects delete --key TEST001

# Propose command
docker compose run tui commands propose --project TEST001 --command assess_gaps

# Apply proposal
docker compose run tui commands apply --project TEST001 --proposal <id>

# List proposals
docker compose run tui proposals list --project TEST001

# Apply proposal
docker compose run tui proposals apply --project TEST001 --id <id>

# List artifacts
docker compose run tui artifacts list --project TEST001

# Get workflow state
docker compose run tui workflow state --project TEST001

# Transition workflow state
docker compose run tui workflow transition --project TEST001 --to-state planning --actor PM

# List audit events
docker compose run tui workflow audit-events --project TEST001
```

## Example Workflows

### Workflow 1: Create Project and Assess Gaps

```bash
# 1. Create a new project
python main.py projects create --key WEBSITE --name "Website Redesign"

# 2. Propose gap assessment
python main.py commands propose --project WEBSITE --command assess_gaps

# 3. Review the proposed changes, then apply
python main.py commands apply --project WEBSITE --proposal <proposal-id>

# 4. View the generated gap assessment
python main.py artifacts get --project WEBSITE --path artifacts/gap_assessment.md
```

### Workflow 2: Generate Project Charter

```bash
# 1. Propose charter generation
python main.py commands propose \
  --project WEBSITE \
  --command generate_artifact \
  --artifact-name project_charter.md \
  --artifact-type project_charter

# 2. Apply the proposal
python main.py commands apply --project WEBSITE --proposal <proposal-id>

# 3. View the charter
python main.py artifacts get --project WEBSITE --path artifacts/project_charter.md
```

### Workflow 3: Generate Project Plan

```bash
# 1. Propose plan generation
python main.py commands propose --project WEBSITE --command generate_plan

# 2. Apply the proposal
python main.py commands apply --project WEBSITE --proposal <proposal-id>

# 3. List generated artifacts
python main.py artifacts list --project WEBSITE

# 4. View the schedule
python main.py artifacts get --project WEBSITE --path artifacts/schedule.md
```

## Local Development

### Running with Local API

If the API is running locally (not in Docker):

```bash
# Terminal 1: Start API
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Terminal 2: Run TUI
cd apps/tui
source .venv/bin/activate
export API_BASE_URL=http://localhost:8000
python main.py health
```

### Running with Docker API

If the API is running in Docker:

```bash
# Terminal 1: Start API
docker compose up api

# Terminal 2: Run TUI locally
cd apps/tui
source .venv/bin/activate
export API_BASE_URL=http://localhost:8000
python main.py health
```

## Testing

### Basic Connectivity Test

```bash
# Check if API is reachable
python main.py health
```

Expected output:
```
✓ API is healthy!
╭─────── Health Status ───────╮
│ {                           │
│   "status": "healthy",      │
│   "docs_path": "...",       │
│   ...                       │
│ }                           │
╰─────────────────────────────╯
```

### End-to-End Test

```bash
# 1. Create test project
python main.py projects create --key TEST001 --name "Test Project"

# 2. Verify it appears in list
python main.py projects list

# 3. Get project details
python main.py projects get --key TEST001

# 4. Propose and apply a command
python main.py commands propose --project TEST001 --command assess_gaps
python main.py commands apply --project TEST001 --proposal <id>

# 5. List generated artifacts
python main.py artifacts list --project TEST001
```

## Troubleshooting

### Connection Issues

**Problem**: `Connection error: [Errno 111] Connection refused`

**Solutions**:
1. Verify API is running: `curl http://localhost:8000/health`
2. Check `API_BASE_URL` environment variable
3. For Docker: Use `http://api:8000` (internal network)
4. For local: Use `http://localhost:8000`

### Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'click'`

**Solutions**:
1. Activate virtual environment: `source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Verify you're in the correct directory: `cd apps/tui`

### HTTP 404 Errors

**Problem**: `HTTP 404 error - Project not found`

**Solutions**:
1. Verify project exists: `python main.py projects list`
2. Check project key spelling (case-sensitive)
3. Create project if needed

### Permission Denied

**Problem**: `Permission denied` when running `./main.py`

**Solutions**:
1. Make file executable: `chmod +x main.py`
2. Or run with Python explicitly: `python main.py`

## Project Structure

```
apps/tui/
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── api_client.py        # HTTP client for API
├── config.py            # Configuration management
├── utils.py             # Utility functions
├── commands/            # Command modules
│   ├── __init__.py
│   ├── projects.py      # Project management commands
│   ├── propose.py       # Propose/apply workflow
│   ├── artifacts.py     # Artifact commands
│   └── config.py        # Configuration commands
└── README.md            # This file
```

## Command Reference

### Projects Commands

- `projects create --key <KEY> --name <NAME>` - Create new project
- `projects list` - List all projects
- `projects get --key <KEY>` - Get project state

### Commands (Propose/Apply)

- `commands propose --project <KEY> --command <CMD>` - Propose command
- `commands apply --project <KEY> --proposal <ID>` - Apply proposal

Available commands: `assess_gaps`, `generate_artifact`, `generate_plan`

### Artifacts Commands

- `artifacts list --project <KEY>` - List project artifacts
- `artifacts get --project <KEY> --path <PATH>` - View artifact content

### Configuration Commands

- `config show` - Display current configuration
- `config set --api-url <URL>` - Set API base URL
- `config set --api-key <KEY>` - Set API authentication key
- `config reset` - Reset configuration to defaults

## Dependencies

- **click** (8.1.7): CLI framework
- **httpx** (0.27.0): Modern HTTP client
- **pydantic** (2.5.3): Data validation
- **python-dotenv** (1.0.0): Environment variable management
- **rich** (13.7.0): Terminal formatting and colors

## Contributing

When adding new commands:

1. Add the API method to `api_client.py`
2. Create or update a command module in `commands/`
3. Import and register the command in `main.py`
4. Update this README with usage examples

## Security Notes

- Never commit `.env` files with sensitive credentials
- Use `API_KEY` environment variable for authentication
- The client does not store any data locally
- All data is managed by the API server

## License

Part of the AI-Agent-Framework repository.

## Support

- API Documentation: `http://localhost:8000/docs`
- Main Repository: Check repository README.md
- Issues: Report via GitHub Issues

---

**Version**: 1.0.0  
**Part of**: ISO 21500 AI-Agent Framework  
**API Compatibility**: 1.0.0
