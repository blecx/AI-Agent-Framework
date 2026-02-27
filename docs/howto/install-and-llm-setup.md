# Install & LLM Setup Guide

This guide is the complete reference for installing and running the project in two modes:

- **Docker images / containers** (recommended for consistency)
- **Local codebase setup** (recommended for development)

It also includes LLM connection examples for:

1. GitHub (Copilot/GitHub Models)
2. OpenAI
3. Local LLMs (LM Studio and Ollama)

For a shorter version, see [QUICKSTART.md](../../QUICKSTART.md).

---

## Prerequisites

- Python 3.10+ (3.12 recommended)
- Node.js 20+ (for local web client development)
- Git
- Docker Engine + Docker Compose plugin

---

## Option A: Docker images and containers

### A1. Clone repository

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

### A2. Configure LLM (optional)

The compose file mounts `configs/llm.default.json` into the API container by default.

To customize provider/model settings, create your own config and update the mount in `docker-compose.yml` if needed:

```bash
cp configs/llm.default.json configs/llm.json
```

Then change the API volume mount from:

- `./configs/llm.default.json:/config/llm.json:ro`

to:

- `./configs/llm.json:/config/llm.json:ro`

### A3. Build and start all services

```bash
docker compose up --build
```

Services started:

- `api` (FastAPI backend) on `:8000`
- `web` (Nginx + web app) on `:8080`
- `client` (optional terminal client)
- `tui` (optional CLI/TUI container)

### A4. Access endpoints

- Web UI: <http://localhost:8080>
- API: <http://localhost:8000>
- Swagger docs: <http://localhost:8000/docs>

### A5. Optional image-only workflow

If you want to explicitly build images first:

```bash
docker compose build
docker compose up
```

Or build individual images:

```bash
docker build -f docker/api/Dockerfile -t iso21500-api:local .
docker build -f docker/web/Dockerfile -t iso21500-web:local .
docker build -f client/Dockerfile -t ai-agent-client:local ./client
docker build -f docker/Dockerfile.tui -t iso21500-tui:local .
```

---

## Option B: Local install from the codebase

### B1. Clone repository

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

### B2. Setup Python backend environment

Linux/macOS:

```bash
./setup.sh
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\setup.ps1
.\.venv\Scripts\Activate.ps1
```

### B3. Create docs storage directory

```bash
mkdir -p projectDocs
```

### B4. Configure LLM (optional)

```bash
cp configs/llm.default.json configs/llm.json
```

### B5. Start backend API

```bash
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

### B6. Start local web client (optional)

In another terminal:

```bash
cd apps/web
npm install
npm run dev
```

Local endpoints:

- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- Web dev server: <http://localhost:5173>

---

## LLM connection configuration

The backend reads LLM settings from JSON config (`LLM_CONFIG_PATH`, defaults to `/config/llm.json` in Docker).

For local runs, create `configs/llm.json`.

### 1) GitHub (Copilot/GitHub Models)

Use GitHub Models endpoint with a GitHub token:

```json
{
  "provider": "github",
  "base_url": "https://models.github.ai/inference",
  "api_key": "github_pat_your_token_here",
  "model": "openai/gpt-5.1-codex",
  "temperature": 0.2,
  "max_tokens": 16384,
  "timeout": 300
}
```

### 2) OpenAI

```json
{
  "provider": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-your-openai-key",
  "model": "gpt-4.1",
  "temperature": 0.2,
  "max_tokens": 8192,
  "timeout": 120
}
```

### OpenAI Images (Mockups)

Some workflow steps can optionally generate UI mockup images using the OpenAI Images API (`gpt-image-1`).

- Set `OPENAI_API_KEY` in your environment (never commit this).
- Outputs are written under `.tmp/mockups/issue-<n>/` and include an `index.html` you can open directly.

### 3) Local models

#### LM Studio

Start LM Studio server (default `:1234`) and use:

```json
{
  "provider": "lmstudio",
  "base_url": "http://localhost:1234/v1",
  "api_key": "lm-studio",
  "model": "local-model",
  "temperature": 0.2,
  "max_tokens": 8192,
  "timeout": 120
}
```

#### Ollama (OpenAI-compatible endpoint)

Ensure Ollama is running and use:

```json
{
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model": "llama3.1:8b",
  "temperature": 0.2,
  "max_tokens": 8192,
  "timeout": 120
}
```

### Docker networking note for local LLMs

If API runs in Docker but your LLM runs on the host machine:

- Prefer `http://host.docker.internal:<port>/v1`
- On Linux, if `host.docker.internal` is unavailable, use your host bridge IP

Examples:

- LM Studio in Docker mode: `http://host.docker.internal:1234/v1`
- Ollama in Docker mode: `http://host.docker.internal:11434/v1`

---

## Verify installation

```bash
curl http://localhost:8000/health
```

Expected: JSON with `"status": "healthy"`.

If LLM is not reachable, the system still runs and falls back to template-based generation.

---

## Troubleshooting quick hits

- **API cannot reach local LLM while using Docker**:
  - switch `localhost` to `host.docker.internal`
- **Port conflict (8000/8080/5173)**:
  - stop existing process or remap ports in compose/dev config
- **Missing Python venv support on Linux**:
  - install distro package for venv (example: `python3.12-venv`)
- **No `configs/llm.json`**:
  - copy from `configs/llm.default.json`

---

## Related docs

- [Quick Start](../../QUICKSTART.md)
- [Development Guide](../development.md)
- [Main README](../../README.md)
