# Phase 6: AI Agent Toolbox Extraction Plan

## Objective
Decouple the "AI Agent Framework" (the automated dev workflows, custom agents, dynamic skills, Maestro backend, and MCP servers) from the actual "ProjectBuilder / ISO 21500" FastApi/React application codebase.

By extracting the AI logic into a standalone **Trunk / Template Repository**, we achieve:
1. A portable "AI Developer Toolchain" that can be git-cloned/copied to *any* new project.
2. Independent lifecycle versioning for the agents separately from the app logic.
3. Clean documentation domains (no longer mixing app architecture with AI toolchain instructions).

---

## 1. Repository Splitting Strategy

### To Be Extracted (The "Trunk" Repo)
This payload will become the baseline for the new repository (e.g., `github-copilot-agent-toolbox` or `ai-agent-trunk`):
- **Agent Definitions:** `.github/agents/` (Custom Copilot agents) and `.copilot/skills/` (XML structured skills).
- **Core Orchestration:** `agents/` (Python Maestro framework, agent registry, router, coder).
- **Tooling:** `scripts/` (Work issue, PR merge CLI wrappers, architectural py-tests).
- **Context Layer (MCP):** `apps/mcp/` and `docker-compose.mcp-*.yml` (Memory, Bus, Bash Gateway, etc.).
- **VSCode Configs:** `.vscode/settings.json` (auto-approve mappings & MCP ports) & `tasks.json`.

### To Remain (The "ProjectBuilder" App Repo)
- **Application Code:** `apps/api/` (Backend), `_external/AI-Agent-Framework-Client/` (Frontend), `projectDocs/`.
- **App Infra:** Product-specific `docker-compose.yml` (Nginx, Uvicorn logic).
- **Templates:** `.github/prompts/drafting-issue.md`, `planning-feature.md` (Product-specific specs).

---

## 2. Where AI Documentation Belongs

**Problem:** Currently, `docs/` is heavily polluted with AI tool workflows mixed with FastApi/Docker app logic.
**Solution:**
1. **In the New Trunk Repo:** Move all agent documentation (like `AUTOMATIONS.md`, `docs/agents/`, `VSCODE-GLOBAL-SETTINGS.md`) directly into its root `README.md` and a dedicated `docs/` folder. Since the repo's sole purpose *is* the AI toolchain, it should command the root documentation structure.
2. **In the Target (App) Repo:** The app repository should possess exactly **one** file for AI toolchain context: `.github/copilot-instructions.md`. This file will serve as the bridge telling any local Copilot instance: *"Hey, this repo uses the standardized Agent Toolbox located in `.github/agents`. Check out `.copilot/skills` for its constraints."*

---

## 3. Clear Setup Flow (To be featured on the Trunk's README)

When pasting this Trunk into a new project, the initialization must be deterministic. The AI Toolbox must explicitly outline the required **MCP Server** boot-up logic to give the agents external capabilities:

### **Step 1: Python Agent Environment**
```bash
./setup-ai-pipeline.sh
# Creates virtual env, installs dependencies for the Maestro backend (.venv).
```

### **Step 2: MCP (Model Context Protocol) Infrastructure**
The agents rely on Dockerized MCP servers for repository access, execution, and memory. The Trunk repo will have a master `docker-compose.agents.yml` grouping these:

```bash
# 1. Start the core MCP bus and memory context:
docker compose -f docker-compose.mcp-memory-bus.yml up -d

# 2. Start execution gateways (Bash/Git/Github/Architecture):
docker compose -f docker-compose.mcp-bash-gateway.yml up -d
docker compose -f docker-compose.repo-fundamentals-mcp.yml up -d
docker compose -f docker-compose.mcp-github-ops.yml up -d
docker compose -f docker-compose.mcp-offline-docs.yml up -d
```

### **Step 3: VS Code Workspace Wiring**
Ensure the project's `.vscode/settings.json` activates:
- `"chat.tools.subagent.autoApprove": { ... }` 
- The `mcp.servers` port maps:
  - `bashGateway` -> Port 3011
  - `git` -> Port 3012
  - `search` -> Port 3013
  - etc...

### **Step 4: Environment Key Binding**
Provide an `.env.agents` file template ensuring keys required for sub-services (like Context7 documentation parsing) are loaded into the workspace before executing the bots:
`CONTEXT7_API_KEY=YOUR_KEY`
