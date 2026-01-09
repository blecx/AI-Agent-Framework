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

## Using the System

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

### Running Locally (Development)

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

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
