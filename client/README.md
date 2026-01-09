# AI Agent API Client

A standalone Python CLI client for consuming the AI Agent REST API. This client demonstrates API usage without the web UI and enables automation, scripting, and CI/CD integration.

## Purpose

The AI Agent API Client serves as:

- **API Consumer**: Demonstrates how to interact with the AI Agent API
- **Automation Tool**: Enables scripting and batch operations
- **CI/CD Integration**: Can be used in automated pipelines
- **Testing Tool**: Useful for API testing and validation
- **Independent Component**: Runs separately from the main application

## Architecture

The client is completely independent from the AI Agent application:

- **No shared code**: Uses only the REST API interface
- **Separate container**: Runs in its own Docker container
- **API-first design**: Validates the API-first architecture
- **Optional component**: Not required for core functionality

## Features

The client supports all major API operations:

- ✅ **Health Check**: Verify API availability
- ✅ **Project Management**: Create and list projects
- ✅ **State Queries**: Get project state and metadata
- ✅ **Command Proposal**: Preview changes before applying
- ✅ **Command Apply**: Execute and commit changes
- ✅ **Artifacts**: List and retrieve project artifacts
- ✅ **Demo Workflow**: Run complete end-to-end workflow

## Installation

### Option 1: Docker (Recommended)

Using Docker Compose (from repository root):

```bash
# Build and run the client
docker compose run client --help

# Run a specific command
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

### Command Overview

```bash
# Show all commands
python -m src.client --help

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

## When to Use the Client vs Web UI

### Use the Client for:

- **Automation**: Scripting repetitive tasks
- **CI/CD Integration**: Automated project management in pipelines
- **Batch Operations**: Processing multiple projects
- **API Testing**: Validating API functionality
- **Command-line Workflows**: When GUI is not available
- **Integration**: Connecting to other tools and systems

### Use the Web UI for:

- **Interactive Use**: Creating and managing projects manually
- **Visual Review**: Reviewing diffs and proposals visually
- **Exploration**: Browsing artifacts and project state
- **User-friendly**: Non-technical users
- **Rich Features**: Full visual experience

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
