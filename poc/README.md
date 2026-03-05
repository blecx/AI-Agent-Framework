# PoC — LLM Gateway

A lightweight, provider-abstracted LLM chat-completion gateway for the
AI-Agent-Framework proof-of-concept stack.

---

## Contents

- [Overview](#overview)
- [Quick start](#quick-start)
- [Provider reference](#provider-reference)
  - [openai\_compat](#openai_compat-recommended)
  - [copilot](#copilot)
- [Configuration reference](#configuration-reference)
- [Running the tests](#running-the-tests)

---

## Overview

The gateway exposes a single `LLMGateway` class that routes chat-completion
requests to a configurable upstream provider.  A provider abstraction
(`LLMProvider`) makes it straightforward to add new upstreams without touching
the rest of the stack.

```
┌────────────────────────────────────────────┐
│               LLMGateway                  │
│  ┌──────────────┐   ┌───────────────────┐ │
│  │  openai_compat│   │  copilot (stub/err)│ │
│  └──────┬───────┘   └────────┬──────────┘ │
│         │ POST /chat/completions│          │
│         ▼                     ▼            │
│   Real upstream         Stub reply /       │
│ (OpenAI / Azure /        ConfigurationError │
│  GitHub Models / LM Studio …)              │
└────────────────────────────────────────────┘
```

---

## Quick start

```python
from poc.llm_gateway import LLMGateway

# Point at any OpenAI-compatible endpoint
gw = LLMGateway({
    "provider": "openai_compat",
    "base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "model": "gpt-4o",
})

reply = await gw.chat_completion([
    {"role": "user", "content": "Summarise ISO 21500 in one sentence."}
])
print(reply)
```

For local development without a real LLM:

```python
gw = LLMGateway({
    "provider": "copilot",
    "fallback_to_stub": True,   # returns a synthetic reply
})
```

---

## Provider reference

### `openai_compat` (recommended)

Connects to **any HTTP server that implements the OpenAI
`POST /chat/completions` API**.

| Config key | Required | Description |
|---|---|---|
| `base_url` | ✅ | Full base URL, e.g. `https://api.openai.com/v1` |
| `api_key` | ✅ | Bearer token / API key |
| `model` | ✅ | Model ID, e.g. `gpt-4o` |
| `temperature` | — | Sampling temperature (default `0.7`) |
| `max_tokens` | — | Max output tokens (default `4096`) |
| `timeout` | — | HTTP timeout in seconds (default `120`) |

**Compatible upstreams:**

| Upstream | `base_url` example |
|---|---|
| OpenAI | `https://api.openai.com/v1` |
| Azure OpenAI | `https://<resource>.openai.azure.com/openai/deployments/<deployment>` |
| GitHub Models | `https://models.github.ai/inference` |
| LM Studio (local) | `http://localhost:1234/v1` |
| Ollama (local) | `http://localhost:11434/v1` |

**Example — GitHub Models:**

```json
{
  "provider": "openai_compat",
  "base_url": "https://models.github.ai/inference",
  "api_key": "<your-github-pat>",
  "model": "openai/gpt-4o"
}
```

Set `LLM_GATEWAY_CONFIG=/path/to/config.json` or pass the dict directly to
`LLMGateway(config={...})`.

---

### `copilot`

> **Important — why this provider exists**
>
> GitHub Copilot **does not** expose a publicly documented,
> API-key-authenticated chat-completions endpoint that arbitrary
> third-party gateways can call.  The `copilot` provider is therefore a
> *configuration-validation adapter*, not a functional upstream.

#### Normal mode (no real endpoint configured)

`LLMGateway({"provider": "copilot"})` — any call to
`chat_completion()` or `validate()` raises a `ConfigurationError` with a
clear explanation and instructions on what to do instead:

```
ConfigurationError: The 'copilot' provider cannot be used as a standalone
LLM gateway upstream: GitHub Copilot does not provide a publicly documented
API-key-authenticated chat-completions endpoint for arbitrary third-party
gateways.

To use a live LLM with this gateway, switch to 'provider: openai_compat'
and supply:
  - base_url: your OpenAI-compatible endpoint (e.g. https://api.openai.com/v1)
  - api_key:  your API key or bearer token
  - model:    the model ID (e.g. gpt-4o)
...
```

#### Stub mode (`fallback_to_stub: true`)

```json
{
  "provider": "copilot",
  "fallback_to_stub": true
}
```

All `chat_completion()` calls return a static synthetic reply so the rest
of the stack works end-to-end without a real LLM backend.  `health()`
reports `status: degraded / mode: stub`.

#### What would be needed to use a real Copilot endpoint

If your organisation manages a **GitHub Copilot enterprise endpoint** that
exposes an OpenAI-compatible API (some GitHub Enterprise Cloud customers have
access to this via a custom integration), you can use it today by switching to
`provider: openai_compat` and providing:

| Config key | Value |
|---|---|
| `provider` | `openai_compat` |
| `base_url` | The enterprise endpoint URL supplied by your org admin |
| `api_key` | A short-lived OAuth bearer token or service-account token |
| `model` | The model ID provided by the endpoint |

There is no action required in this gateway — no code changes are needed.

---

## Configuration reference

All keys with their defaults:

```json
{
  "provider":        "openai_compat",
  "base_url":        "",
  "api_key":         "",
  "model":           "",
  "temperature":     0.7,
  "max_tokens":      4096,
  "timeout":         120,
  "fallback_to_stub": false
}
```

**Configuration resolution order** (`GatewayConfig`):

1. Explicit `config=` dict passed to `LLMGateway(config={...})`.
2. `config_path=` argument to `GatewayConfig`.
3. `LLM_GATEWAY_CONFIG` environment variable (path to a JSON file).
4. `poc/llm_gateway/config.json` (local override; **add to `.gitignore`**).
5. Built-in defaults above.

Never commit `api_key` values.  Use the `LLM_GATEWAY_CONFIG` env var or
inject secrets at runtime.

---

## Running the tests

```bash
# From the repo root
PYTHONPATH=.:apps/api pytest tests/unit/test_poc_llm_gateway.py -v
```

The test suite covers:

- Default configuration and overrides
- Provider selection and routing (including unknown provider errors)
- `openai_compat` config validation (missing/placeholder keys)
- `openai_compat` HTTP success and error paths (mocked)
- `copilot` validation with and without `fallback_to_stub`
- `copilot` stub reply behaviour
- `LLMGateway.health()` for both providers
