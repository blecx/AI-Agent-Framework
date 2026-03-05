# LLM Gateway PoC

Proof-of-concept LLM gateway that routes agent requests to an upstream LLM
provider.  Three providers are included:

| Provider | Status | Notes |
|---|---|---|
| `stub` | ✅ Fully functional | Default for local dev – no credentials needed |
| `github` | ✅ Fully functional | GitHub Models (`models.github.ai`) – OpenAI-compatible |
| `copilot` | 🚧 Stub / adapter | GitHub Copilot has no public programmatic API yet (see [Copilot note](#github-copilot-note)) |

---

## Quick start

```bash
# Install dependencies (from repo root)
pip install fastapi uvicorn httpx pydantic

# Start gateway with the default stub provider
cd poc
uvicorn gateway.app:app --reload --port 8080

# Health check
curl http://localhost:8080/health
```

---

## Configuration

### Environment variables

All variables are optional.  The gateway falls back to the `stub` provider
when none are set.

| Variable | Default | Description |
|---|---|---|
| `LLM_GATEWAY_PROVIDER` | `stub` | Provider to use: `github`, `copilot`, or `stub` |
| `LLM_GATEWAY_API_KEY` | _(empty)_ | API key / token.  Prefer provider-specific token vars below |
| `LLM_GATEWAY_BASE_URL` | _(provider default)_ | Override the upstream base URL |
| `LLM_GATEWAY_MODEL` | `openai/gpt-4o-mini` | Default model when no model is specified per request |
| `LLM_GATEWAY_TIMEOUT` | `60` | HTTP timeout in seconds |
| `LLM_GATEWAY_CONFIG` | _(none)_ | Path to a JSON config file (same schema as `configs/llm.*.json`) |
| `LLM_CONFIG_PATH` | _(none)_ | Shared config path (also read by `agents/llm_client.py`) |
| `GITHUB_TOKEN` | _(none)_ | GitHub PAT – preferred token source for `github` provider |
| `GH_TOKEN` | _(none)_ | Alias for `GITHUB_TOKEN` (GitHub CLI convention) |
| `GITHUB_PAT` | _(none)_ | Alternate PAT variable name |

> **Security**: Never commit secrets to source control.  Always use
> environment variables or a mounted secrets file that is excluded from git.

---

## GitHub Models provider (`provider=github`)

[GitHub Models](https://github.com/marketplace/models) exposes an
OpenAI-compatible chat-completions API at `https://models.github.ai/inference`.
It is the recommended production provider for this gateway.

### Authentication

1. Create a fine-grained GitHub Personal Access Token (PAT) at
   <https://github.com/settings/tokens>.  The token needs no special scopes
   for public model access (free tier).
2. Export it in your shell:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```
3. Set the provider:
   ```bash
   export LLM_GATEWAY_PROVIDER=github
   ```

Or use a config file (see [Config file](#config-file) below).

### Model policy

Agents can request a specific model or a logical role.  The gateway resolves
the model in this order:

1. **Explicit `model` field** in the request body – used as-is.
2. **`role` field** in the request body – looked up in the `model_policy`
   map from the active config.
3. **`default_model`** from config / `LLM_GATEWAY_MODEL` env var.

Example config with per-role policy:

```json
{
  "provider": "github",
  "api_key": "your-api-key-here",
  "model": "openai/gpt-4o-mini",
  "roles": {
    "planning": { "model": "openai/gpt-4o" },
    "coding":   { "model": "openai/gpt-4o-mini" },
    "review":   { "model": "openai/gpt-4o-mini" }
  }
}
```

Available models (non-exhaustive): `openai/gpt-4o`, `openai/gpt-4o-mini`,
`meta/meta-llama-3.1-70b-instruct`.  Full list:
<https://github.com/marketplace/models>

---

## GitHub Copilot note

GitHub Copilot **does not currently expose a stable public REST API** for
programmatic chat/completion requests outside of IDE plugins and
the official [GitHub Copilot Extensions](https://docs.github.com/en/copilot/building-copilot-extensions/about-building-copilot-extensions) framework.

The `copilot` provider in this gateway is therefore a **documented stub**:

- It correctly identifies itself as unconfigured (`is_configured() → False`).
- Calling `complete()` raises `NotImplementedError` with an actionable message.
- The `/health` endpoint returns HTTP 503 with instructions to use `github` instead.

### When a public Copilot API becomes available

The stub is designed to be replaced.  See `poc/gateway/providers/copilot.py`
for TODOs that mark every implementation point:

```
TODO: Replace the stub body in complete() with real HTTP calls once
      GitHub exposes a stable endpoint.
```

Expected auth flow (when available):

- Obtain an OAuth token via the GitHub Device-Flow **or** use a GitHub App
  Installation token with the `copilot` scope.
- Exchange it at: `POST https://api.github.com/copilot_internal/v2/token`
  _(internal/undocumented endpoint – subject to change)_
- Required environment variable: `GITHUB_COPILOT_TOKEN`

---

## Config file

The gateway accepts any config file that follows the same schema as
`configs/llm.default.json`.  Point to it via env var:

```bash
export LLM_GATEWAY_CONFIG=/path/to/my-llm-config.json
```

Or reuse the existing shared config:

```bash
export LLM_CONFIG_PATH=configs/llm.default.json
```

The env vars `LLM_GATEWAY_PROVIDER`, `LLM_GATEWAY_API_KEY`, etc. always
**override** values from the config file.

---

## API endpoints

### `GET /health`

Returns the health of the gateway and configured upstream provider.

**Response `200 OK`** (provider is configured):

```json
{
  "status": "ok",
  "provider": "github",
  "base_url": "https://models.github.ai/inference",
  "default_model": "openai/gpt-4o-mini",
  "model_policy": { "planning": "openai/gpt-4o" }
}
```

**Response `503 Service Unavailable`** (provider not configured):

```json
{
  "detail": {
    "status": "error",
    "provider": "github",
    "error": "No GitHub token found. Set GITHUB_TOKEN, GH_TOKEN, or GITHUB_PAT."
  }
}
```

### `POST /v1/chat/completions`

Proxy a chat-completion request to the upstream provider.

**Request body:**

```json
{
  "messages": [{"role": "user", "content": "Hello"}],
  "model": "openai/gpt-4o",
  "role": "planning",
  "temperature": 0.2,
  "max_tokens": 512
}
```

- `model` and `role` are both optional.  When both are omitted the
  `default_model` from config is used.
- `role` is looked up in the hub model policy; `model` overrides it.

---

## Running tests

```bash
# From the repo root
python -m pytest tests/poc/ -v
```

All tests are unit tests – no external API calls are made.

---

## Architecture

```
poc/
├── gateway/
│   ├── app.py           FastAPI app (health + completions endpoints)
│   ├── config.py        Config loading (env vars, JSON file, defaults)
│   ├── router.py        Provider selection & model resolution
│   └── providers/
│       ├── base.py      Abstract LLMProvider interface
│       ├── stub.py      Stub provider (local dev default)
│       ├── github_models.py  GitHub Models provider (OpenAI-compatible)
│       └── copilot.py   GitHub Copilot adapter stub (TODO)
└── README.md            This file

tests/poc/
└── test_routing.py      Unit tests for routing logic
```
