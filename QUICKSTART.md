# Quick Start (Backend + Client)

This guide gives you the fastest path to run the AI-Agent-Framework with:

- **Backend API** (`apps/api`)
- **Web client** (`_external/AI-Agent-Framework-Client/client`)
- Optional terminal clients (`client/`, `apps/tui`)

For the full installation + LLM guide (Docker images, local setup, troubleshooting), see:

- [Install & LLM Setup Guide](docs/howto/install-and-llm-setup.md)

---

## 1) Prerequisites

- Python **3.10+** (3.12 recommended)
- Node.js **20+** (for local web development)
- Git
- Docker + Docker Compose (for containerized setup)

---

## 2) Fastest path: Docker images (recommended)

1. Clone and enter the repo:

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

1. (Optional) Create a custom LLM config:

```bash
cp configs/llm.default.json configs/llm.json
```

1. Pull and start prebuilt API/Web images:

```bash
docker compose pull api web
docker compose up -d api web
```

1. (Optional) Pin immutable image tags from CI/CD:

```bash
API_IMAGE=ghcr.io/blecx/ai-agent-framework-api:sha-<commit-sha> \
WEB_IMAGE=ghcr.io/blecx/ai-agent-framework-web:sha-<commit-sha> \
docker compose up -d api web
```

1. (Optional) Run terminal clients when needed:

```bash
docker compose --profile tools up -d client tui
```

1. Open:

- Web UI: <http://localhost:8080>
- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>

> If you want to build containers from local source code instead of pulling images, use `docker compose up --build`.

---

## 3) Local path: Codebase development setup

1. Clone and enter the repo:

```bash
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

1. Setup Python environment:

```bash
./setup.sh
source .venv/bin/activate
mkdir -p projectDocs
```

1. (Optional) Configure LLM:

```bash
cp configs/llm.default.json configs/llm.json
```

1. Start API:

```bash
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

1. Start web client in another terminal:

```bash
cd _external/AI-Agent-Framework-Client/client
npm install
npm run dev
```

1. Open:

- Web dev UI: <http://localhost:5173>
- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>

---

## 4) LLM setup examples

Create `configs/llm.json` and choose one profile.

### Example A: GitHub (Copilot/GitHub Models)

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

### Example B: OpenAI

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

### Example C: Local LLM (LM Studio or Ollama)

LM Studio:

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

Ollama (OpenAI-compatible endpoint):

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

> Docker note: when API runs in a container and your LLM runs on host, use `http://host.docker.internal:<port>/v1` (Linux fallback: host bridge IP).

---

## 5) Quick verification

- Health check:

```bash
curl http://localhost:8000/health
```

- Expected: JSON with `"status":"healthy"`

---

## 6) What to read next

- Full install + Docker image workflow + local setup + LLM deep dive:
  - [docs/howto/install-and-llm-setup.md](docs/howto/install-and-llm-setup.md)
- Development workflow:
  - [docs/development.md](docs/development.md)
- Main project docs:
  - [README.md](README.md)
