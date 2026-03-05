# AI Agent Framework – PoC (S1)

> **Status**: PoC / Sprint 1 – not production-ready.  See [roadmap](#roadmap) for future work.

A **multi-agent local coding framework** that runs entirely in Docker on Debian (or any Linux/macOS host with Docker), orchestrated through a central **Hub** service.  VS Code is the suggested control centre; no extension is required at this stage.

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Docker Compose (poc/)                                          │
│                                                                 │
│  ┌──────────┐   REST    ┌────────────────────────────────────┐  │
│  │  hub     │◄──────────│  agent-generalist  (LLM tasks)     │  │
│  │ FastAPI  │           │  python-runner     (pytest)        │  │
│  │ Postgres │           └────────────────────────────────────┘  │
│  └────┬─────┘                                                   │
│       │                 ┌─────────────────┐                     │
│       └────────────────►│  llm-gateway    │ (stub / Ollama)     │
│                         └─────────────────┘                     │
│  Volumes: pgdata / artifacts / repos                            │
└─────────────────────────────────────────────────────────────────┘
        ▲
        │  agentctl (CLI)   – runs on host or in a container
```

### Services

| Service | Port | Description |
|---|---|---|
| `hub` | 8000 | FastAPI orchestrator + Postgres persistence |
| `db` | 5432 | PostgreSQL 16 |
| `llm-gateway` | 8080 | LLM proxy stub (offline) or real upstream |
| `agent-generalist` | – | Polling agent: SPEC_NORMALIZE → STORY_SPLIT → TASK_DECOMPOSE → PATCH_IMPLEMENT |
| `python-runner` | – | Polling runner: RUN_TESTS_PYTHON |

---

## Prerequisites

- Docker ≥ 24 and Docker Compose v2 (`docker compose`)
- Python ≥ 3.10 on the host (for the CLI)
- (Optional) A GitHub personal access token for private repos

---

## Quick-start

```bash
# 1. Clone and enter the poc directory
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework/poc

# 2. Copy and edit env vars (defaults work for offline/stub mode)
cp .env.example .env

# 3. Start all services
docker compose up --build -d

# 4. Verify everything is healthy
docker compose ps
curl http://localhost:8000/health   # {"status":"ok","service":"hub"}
curl http://localhost:8080/health   # {"status":"ok","service":"llm-gateway","mode":"stub"}

# 5. Install the CLI (in a venv recommended)
python -m venv .venv
source .venv/bin/activate
pip install -e cli/

# 6. Create a run
agentctl run create --repo octocat/Hello-World --ref main

# 7. Watch tasks progress
agentctl run status <run_id>
agentctl logs tail <run_id>
```

---

## Environment variables

### Hub (`hub/.env` or `docker-compose.yml`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://hub:hubpass@db:5432/hubdb` | Postgres connection string |
| `ARTIFACT_DIR` | `/data/artifacts` | Directory for uploaded artifacts |
| `REPOS_DIR` | `/data/repos` | Directory for canonical repo clones / worktrees |

### LLM Gateway

| Variable | Default | Description |
|---|---|---|
| `UPSTREAM_LLM_URL` | *(empty)* | Upstream LLM URL (e.g. `http://host.docker.internal:11434` for Ollama).  Leave blank for stub mode. |

### Agent Generalist

| Variable | Default | Description |
|---|---|---|
| `HUB_URL` | `http://hub:8000` | Hub base URL |
| `LLM_GATEWAY_URL` | `http://llm-gateway:8080` | LLM gateway URL |
| `POLL_INTERVAL` | `5` | Seconds between polls |
| `LEASE_SECONDS` | `180` | Task lease duration |
| `GITHUB_TOKEN` | *(empty)* | GitHub PAT for private repo clones |

### Python Runner

| Variable | Default | Description |
|---|---|---|
| `HUB_URL` | `http://hub:8000` | Hub base URL |
| `TEST_COMMAND` | `pytest -q` | Command to run tests |
| `POLL_INTERVAL` | `5` | Seconds between polls |
| `LEASE_SECONDS` | `300` | Task lease duration |

### CLI (`agentctl`)

| Variable | Default | Description |
|---|---|---|
| `HUB_URL` | `http://localhost:8000` | Hub base URL |

---

## CLI reference (`agentctl`)

```
Usage: agentctl [OPTIONS] COMMAND [ARGS]...

Commands:
  run     Manage runs
  task    Manage tasks
  config  Hub configuration
  logs    View logs

Run commands:
  run create    --repo owner/repo --ref <ref> [--spec path/to/spec.md]
  run status    <run_id>
  run list      [--limit N]

Task commands:
  task list     --run <run_id>
  task approve  <task_id>        # when approvals are enabled

Config commands:
  config set-approvals  on|off
  config get            <key>
  config list

Logs commands:
  logs tail  <run_id>  [--interval SECS]
```

---

## Workflow

```
run create
    └─► SPEC_NORMALIZE   (agent-generalist + LLM)
            └─► STORY_SPLIT    (agent-generalist + LLM)
                    └─► TASK_DECOMPOSE   (agent-generalist + LLM)
                                └─► PATCH_IMPLEMENT   (agent-generalist + LLM + git diff)
                                            └─► RUN_TESTS_PYTHON   (python-runner + pytest)
```

1. `agentctl run create` POSTs to the Hub which inserts the run and the default 5-task DAG into Postgres.
2. Each agent polls `/tasks/poll?task_type=<type>` and claims available tasks via `/tasks/{id}/claim`.
3. The agent calls the LLM gateway for reasoning tasks and uploads patch artifacts for `PATCH_IMPLEMENT`.
4. The Python runner downloads a repo snapshot tarball, runs `pytest -q`, and uploads the log.
5. All statuses and artifact metadata persist in Postgres; files on the shared `artifacts` volume.

---

## Approval mode

By default tasks are **fully autonomous** (no approvals required).

To require manual approval before each task is picked up:

```bash
agentctl config set-approvals on
```

Then approve each task individually:

```bash
agentctl task list --run <run_id>
agentctl task approve <task_id>
```

Disable approvals:

```bash
agentctl config set-approvals off
```

---

## Using VS Code as control centre

Add the following to `.vscode/tasks.json` in the repo root for one-click shortcuts:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "PoC: Start stack",
      "type": "shell",
      "command": "docker compose up --build -d",
      "options": { "cwd": "${workspaceFolder}/poc" },
      "group": "build"
    },
    {
      "label": "PoC: Stop stack",
      "type": "shell",
      "command": "docker compose down",
      "options": { "cwd": "${workspaceFolder}/poc" }
    },
    {
      "label": "PoC: Create run (prompt)",
      "type": "shell",
      "command": "agentctl run create --repo ${input:repo} --ref ${input:ref}",
      "options": { "cwd": "${workspaceFolder}/poc" }
    },
    {
      "label": "PoC: Hub logs",
      "type": "shell",
      "command": "docker compose logs -f hub",
      "options": { "cwd": "${workspaceFolder}/poc" }
    }
  ],
  "inputs": [
    { "id": "repo", "type": "promptString", "description": "GitHub owner/repo" },
    { "id": "ref",  "type": "promptString", "description": "git ref", "default": "main" }
  ]
}
```

A VS Code extension is planned for S2/MVP (out of scope for PoC).

---

## Connecting a real LLM

### Ollama (local)

```bash
# On the host
ollama pull llama3
# In poc/.env
UPSTREAM_LLM_URL=http://host.docker.internal:11434
```

Then restart `llm-gateway`:

```bash
docker compose restart llm-gateway
```

### OpenAI-compatible

Set `UPSTREAM_LLM_URL` to any OpenAI-compatible endpoint (e.g. LM Studio, vLLM).

---

## Hub REST API (summary)

| Method | Path | Description |
|---|---|---|
| POST | `/runs` | Create run + default task DAG |
| GET | `/runs` | List runs |
| GET | `/runs/{id}` | Get run |
| GET | `/runs/{id}/tasks` | List tasks for run |
| POST | `/runs/{id}/tasks` | Add custom task |
| POST | `/runs/{id}/spec` | Upload spec.md |
| GET | `/tasks/poll?task_type=` | Poll available tasks |
| POST | `/tasks/{id}/claim` | Claim task (lease) |
| POST | `/tasks/{id}/heartbeat` | Renew lease |
| POST | `/tasks/{id}/complete` | Mark task complete |
| POST | `/tasks/{id}/fail` | Mark task failed |
| POST | `/tasks/{id}/approve` | Approve task (when approvals on) |
| POST | `/artifacts/{task_id}/upload` | Upload artifact file |
| GET | `/artifacts/{id}/download` | Download artifact |
| GET | `/config` | List config |
| PUT | `/config/{key}` | Set config value |
| POST | `/repos/{run_id}/prepare` | Clone/fetch repo + create worktree |
| POST | `/repos/{run_id}/apply-patch` | Apply patch to worktree |
| GET | `/repos/{run_id}/snapshot` | Download repo snapshot tar.gz |
| GET | `/health` | Health check |

Full interactive docs: http://localhost:8000/docs

---

## Roadmap

| Phase | Label | Description |
|---|---|---|
| **S1** | **PoC** ← *you are here* | Single generalist agent + python-runner, stub LLM, no approval UX |
| S2 | MVP | Multiple specialised agents (architect, tester, reviewer), real LLM policies, approval UI |
| S3 | Hardening | Multi-repo support, retry/back-off, RBAC, audit log |
| 9C | VS Code Extension | Full IDE integration, run panel, diff viewer |

---

## Development

```bash
# Run hub locally (needs Postgres)
cd poc/hub
pip install -r requirements.txt
DATABASE_URL=postgresql://hub:hubpass@localhost:5432/hubdb uvicorn main:app --reload

# Run CLI locally
cd poc/cli
pip install -e .
agentctl --help
```

### Code style

- Python: `ruff` (see `ruff.toml` at repo root)
- Line length: 100

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Hub fails to start | Check DB is healthy: `docker compose logs db` |
| Tasks stuck in `pending` | Agents not running or deps not met; check `docker compose logs agent-generalist` |
| `git clone` fails in agent | Set `GITHUB_TOKEN` in `.env` for private repos |
| LLM calls return stubs | Expected in offline mode; set `UPSTREAM_LLM_URL` to use a real LLM |
