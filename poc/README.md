# PoC LLM Gateway

Lightweight OpenAI-compatible HTTP gateway that forwards chat-completion
requests to a **GitHub Copilot** upstream. Useful for local development,
CI, and experiments – no vendor SDK lock-in.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Gateway and provider health status |
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat completions |

### `POST /v1/chat/completions`

Request body (JSON):

```json
{
  "model": "medium",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user",   "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 4096
}
```

The `model` field accepts either:
- A **policy tier** (`small` | `medium` | `large`) – mapped to concrete model IDs.
- An **explicit Copilot model ID** (e.g. `gpt-4o`, `o3-mini`, `claude-3.5-sonnet`).

---

## Configuration

All configuration is via environment variables. **No secrets are ever
hard-coded**; supply them at runtime or via Docker secrets (see below).

### Core gateway settings

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_PROVIDER` | `copilot` | Active provider: `copilot` or `stub` |
| `GATEWAY_FALLBACK_TO_STUB` | `false` | Fall back to stub when Copilot is misconfigured |

### Copilot upstream

| Variable | Default | Description |
|----------|---------|-------------|
| `COPILOT_API_KEY` | *(required)* | GitHub Copilot / Models API token |
| `COPILOT_BASE_URL` | `https://api.githubcopilot.com` | Override the Copilot API base URL |
| `COPILOT_TIMEOUT` | `60` | HTTP request timeout (seconds) |

> **Docker secret alternative**: mount the token at
> `/run/secrets/copilot_api_key`. The gateway reads it automatically when
> `COPILOT_API_KEY` is not set.

### Model routing (tier → model ID)

| Variable | Default | Description |
|----------|---------|-------------|
| `COPILOT_MODEL_SMALL` | `gpt-4o-mini` | Model for the `small` policy tier |
| `COPILOT_MODEL_MEDIUM` | `gpt-4o` | Model for the `medium` policy tier |
| `COPILOT_MODEL_LARGE` | `o3-mini` | Model for the `large` policy tier |

Default mapping:

| Tier | Default model | Typical use |
|------|--------------|-------------|
| `small` | `gpt-4o-mini` | Classification, summarization, fast responses |
| `medium` | `gpt-4o` | Balanced capability / cost (default) |
| `large` | `o3-mini` | Complex reasoning, planning |

---

## Running locally

### 1. Install dependencies

```bash
pip install -r poc/requirements.txt
```

### 2. Export your Copilot token

```bash
export COPILOT_API_KEY=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Start the gateway

```bash
uvicorn poc.main:app --reload --port 8080
```

### 4. Verify

```bash
curl http://localhost:8080/health
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"small","messages":[{"role":"user","content":"Ping"}]}'
```

---

## Running with Docker / Docker secrets

```yaml
# docker-compose.yml fragment
services:
  llm-gateway:
    build: poc/
    environment:
      GATEWAY_PROVIDER: copilot
      GATEWAY_FALLBACK_TO_STUB: "false"
    secrets:
      - copilot_api_key
    ports:
      - "8080:8080"

secrets:
  copilot_api_key:
    file: ./secrets/copilot_api_key.txt   # plain-text token, NOT committed
```

---

## Offline / stub mode

Set `GATEWAY_PROVIDER=stub` (or `GATEWAY_FALLBACK_TO_STUB=true`) to run
without any credentials. The stub returns deterministic canned responses
and is safe for CI pipelines and local development.

```bash
GATEWAY_PROVIDER=stub uvicorn poc.main:app --port 8080
```

---

## Startup validation

On startup the gateway:
1. Calls `build_provider()` which validates the configuration.
2. Calls `provider.health()` and logs the result.
3. **Fails fast** (raises `RuntimeError`) if the requested provider is
   misconfigured and `GATEWAY_FALLBACK_TO_STUB` is not enabled.

Example startup log (Copilot configured):

```
INFO  Gateway startup: Provider: copilot (configured)
INFO  Provider health: Copilot provider is configured.
```

Example startup log (fallback to stub):

```
INFO  Gateway startup: Provider: stub (fallback – Copilot key missing; …)
WARNING Provider health: Copilot provider is NOT configured: …
```

---

## Running tests

```bash
python -m pytest tests/product/test_poc_gateway.py -v
```

Tests cover provider selection, config validation, model routing, stub
behaviour, CopilotProvider health reporting, and the HTTP endpoints.
No network access or credentials are required to run the tests.
