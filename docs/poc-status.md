# PoC Work — Open Pull Requests Status

> Generated: 2026-03-05  
> Scope: `blecx/AI-Agent-Framework` — all open PRs as of this date

---

## TL;DR

**Yes — scaffolding has already been pushed.**  
Four draft PRs created on 2026-03-05 contain PoC work:

| PR | Title | Branch | Files | +Lines | Status |
|----|-------|--------|-------|--------|--------|
| [#734](https://github.com/blecx/AI-Agent-Framework/pull/734) | fix(poc/hub): upgrade python-multipart 0.0.9 → 0.0.22 | `copilot/implement-poc-framework` | 30 | +2 665 | Draft |
| [#735](https://github.com/blecx/AI-Agent-Framework/pull/735) | feat(poc): LLM gateway PoC with GitHub Models/Copilot support, health check, and unit tests | `copilot/update-llm-gateway-copilot-support` | 12 | +1 343 | Draft |
| [#736](https://github.com/blecx/AI-Agent-Framework/pull/736) | feat(poc): GitHub Copilot upstream support in PoC LLM gateway | `copilot/add-copilot-upstream-support` | 11 | +1 161 | Draft |
| [#737](https://github.com/blecx/AI-Agent-Framework/pull/737) | feat(poc): Provider-abstracted LLM gateway with OpenAI-compat and Copilot adapters | `copilot/update-llm-gateway-copilot` | 10 | +1 111 | Draft |

**All four PRs are drafts and have not been merged into `main`.**  
`main` currently has **no `poc/` directory**.

---

## PR Details

### PR #734 — Full PoC Scaffold (S1)

**Branch:** `copilot/implement-poc-framework`  
**URL:** <https://github.com/blecx/AI-Agent-Framework/pull/734>  
**Scope:** The most comprehensive PR — implements the full S1 PoC stack described in the original design doc.

**Files introduced under `poc/`:**

```
poc/
├── .env.example
├── README.md                          (336 lines)
├── docker-compose.yml                 (98 lines — full multi-service stack)
├── hub/
│   ├── Dockerfile
│   ├── alembic.ini + alembic/         (Postgres migrations)
│   ├── database.py, main.py, models.py, schemas.py
│   └── routers/
│       ├── artifacts.py, config.py, repos.py, runs.py, tasks.py
├── agent-generalist/
│   ├── Dockerfile
│   └── agent.py                       (318 lines — polling agent)
├── cli/
│   ├── agentctl.py                    (297 lines — Typer CLI: run/task/logs commands)
│   └── pyproject.toml, requirements.txt
└── llm-gateway/
    └── Dockerfile
```

**Also adds:**
- `.editorconfig`
- `.github/workflows/ci-poc.yml` (CI workflow for the PoC)
- `.vscode/tasks.json` updates
- `README.md` project-level updates

**Note:** The PR title says "upgrade python-multipart" (a security fix) but the branch `copilot/implement-poc-framework` contains the entire PoC scaffold. The security fix (`python-multipart 0.0.9 → 0.0.22` in `poc/hub/requirements.txt`) is included within the larger implementation PR. **Action required:** The PR title and description should be updated to accurately reflect the full PoC scaffold scope before merging, to ensure the commit history is meaningful and reviewable.

---

### PR #735 — LLM Gateway v1 (GitHub Models + Copilot stub)

**Branch:** `copilot/update-llm-gateway-copilot-support`  
**URL:** <https://github.com/blecx/AI-Agent-Framework/pull/735>  
**Scope:** Standalone LLM gateway under `poc/gateway/` with:
- `LLMProvider` ABC → `GitHubModelsProvider` (real HTTP calls) + `CopilotProvider` (stub, raises `NotImplementedError` with clear TODOs) + `StubProvider`
- Model policy routing (logical roles: `planning`, `coding`, `review` → model IDs)
- `GET /health`, `POST /v1/chat/completions` FastAPI endpoints
- 34 unit tests in `tests/poc/`
- Token prefix validation (`ghp_`, `github_pat_`, etc.)

---

### PR #736 — LLM Gateway v2 (Copilot provider with fallback)

**Branch:** `copilot/add-copilot-upstream-support`  
**URL:** <https://github.com/blecx/AI-Agent-Framework/pull/736>  
**Scope:** Refactored gateway with a different provider hierarchy:

```
poc/
├── main.py, routing.py, requirements.txt, README.md
└── providers/
    ├── base.py     (LLMProvider ABC)
    ├── copilot.py  (httpx; resolves key from env or Docker secret)
    ├── factory.py  (selection + fallback logic)
    └── stub.py
```

**Selection logic:**
```
GATEWAY_PROVIDER=stub              → StubProvider
GATEWAY_PROVIDER=copilot
  + COPILOT_API_KEY set            → CopilotProvider (real HTTP)
  + key missing + FALLBACK=true    → StubProvider (warn)
  + key missing + FALLBACK=false   → ValueError at startup (fail fast)
```
39 unit tests in `tests/product/test_poc_gateway.py`.

---

### PR #737 — LLM Gateway v3 (Provider abstraction, openai_compat primary)

**Branch:** `copilot/update-llm-gateway-copilot`  
**URL:** <https://github.com/blecx/AI-Agent-Framework/pull/737>  
**Scope:** Most opinionated version — acknowledges that Copilot has no public standalone API-key endpoint and promotes `openai_compat` as the primary production upstream.

```
poc/llm_gateway/
├── __init__.py
├── gateway.py        (GatewayConfig resolution: dict → path → env → defaults)
├── providers/
│   ├── base.py       (LLMProvider, ProviderError, ConfigurationError)
│   ├── openai_compat.py   (calls any POST /chat/completions — OpenAI, Azure, GitHub Models, Ollama)
│   └── copilot.py    (ConfigurationError with actionable instructions; fallback_to_stub)
└── config.json       (default config)
```

**Design note:** The `copilot` adapter deliberately does NOT wrap `openai_compat` — it exists to validate config and emit a human-readable error, keeping "Copilot limitation" concern separate from the HTTP transport layer.
32 unit tests in `tests/unit/test_poc_llm_gateway.py`.

---

## Scaffolding Confirmation

**Scaffolding status: ✅ pushed (in draft PRs, not yet merged)**

| Component | PR | Pushed to branch? | Merged to main? |
|-----------|----|--------------------|-----------------|
| PoC Docker Compose stack | #734 | ✅ | ❌ |
| Hub service (FastAPI + Postgres + Alembic) | #734 | ✅ | ❌ |
| Generalist agent (polling) | #734 | ✅ | ❌ |
| CLI (`agentctl`) | #734 | ✅ | ❌ |
| LLM gateway (stub) | #734 | ✅ | ❌ |
| LLM gateway (GitHub Models provider) | #735 | ✅ | ❌ |
| LLM gateway (Copilot provider w/ fallback) | #736 | ✅ | ❌ |
| LLM gateway (openai_compat + Copilot error adapter) | #737 | ✅ | ❌ |
| PoC CI workflow | #734 | ✅ | ❌ |
| python-runner service | ❌ not yet | — | — |

---

## Recommended Next Steps

1. **Select a canonical LLM gateway approach** — PRs #735, #736, #737 are three competing implementations.  
   Recommendation: **PR #737** (`openai_compat` primary) is the most pragmatic given GitHub Copilot's documented API limitations; close #735 and #736.

2. **Merge PR #734 first** (core scaffold) once the LLM gateway choice is finalized and the title/description is corrected to reflect that it is the full PoC scaffold (not just a security fix).

3. **Add `python-runner` service** — it was specified in the original PoC requirements but is not present in any open PR.

4. **Mark PRs ready for review** when the above decisions are made (remove Draft status).
