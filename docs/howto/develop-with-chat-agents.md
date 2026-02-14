# Develop with Chat AI-Agents (VS Code)

This guide describes the *preferred* development workflow for this repository using the built-in VS Code Chat participants and the repo’s agent workflow prompts.

It’s designed for the common loop:

- You have a plan
- The plan becomes one or more GitHub issues
- Each issue becomes **one PR**
- PRs are merged and issues closed via the standard merge workflow

> Terminology note
>
> - **Chat participant**: appears in the VS Code agent/participant menu (typed as `@something`). These are provided by a VS Code extension.
> - **Agent workflow prompt**: a versioned “how to run the workflow” document in `.github/prompts/agents/`.

---

## Prerequisites

- VS Code **1.85+** (required for chat participant APIs)
- GitHub CLI installed + authenticated (`gh auth login`)
- Python environment set up (`./setup.sh`) and `.venv` created
- `projectDocs/` exists (required by the API and many workflows)

### One-time setup (recommended)

1. Create the local venv and install deps:

   ```bash
   ./setup.sh
   source .venv/bin/activate
   ```

2. Ensure `projectDocs/` exists:

   ```bash
   mkdir -p projectDocs
   ```

3. (Optional) configure LLM:

   - Prefer `LLM_CONFIG_PATH` or copy a sample config:

     ```bash
     cp configs/llm.default.json configs/llm.json
     ```

   > Note: `configs/llm.json` is user-specific and should not be committed.

---

## Make the chat participants available in VS Code

This repo includes a local VS Code extension under:

- `.vscode/extensions/issueagent/`

It provides these chat participants:

- `@issueagent` — selects the next issue and runs the autonomous issue workflow
- `@create-issue` — launcher for the *create-issue* workflow (opens the prompt + prints the copy/paste command)

### Install / enable the local extension

If you don’t see the participants in chat:

1. In VS Code: `Ctrl+Shift+P` → **Developer: Install Extension from Location...**
2. Select: `.vscode/extensions/issueagent`
3. `Ctrl+Shift+P` → **Developer: Reload Window**

Quick start reference: `ISSUEAGENT-CHAT-SETUP.md`

---

## The standard workflow chain (plan → issues → PRs → merge)

### 1) Plan work (optional but encouraged)

Use the planning workflow when you’re exploring scope, architecture, or breaking down a larger initiative:

- Workflow prompt: `.github/prompts/agents/Plan.md`
- Typical invocation:

  ```text
  @workspace /runSubagent Plan "<what you want to achieve>"
  ```

Output you want from planning:

- Clear goal and acceptance criteria
- Explicit scope boundaries (in/out)
- A short list of discrete deliverables that can become issues

### 2) Convert plan tasks into GitHub issues (create-issue)

When a plan yields actionable tasks, create issues **before** implementation.

You have two ergonomic options:

**Option A (discoverable in agent menu):**

- Type: `@create-issue`
- Provide a one-line description (recommended), e.g.:
  - `@create-issue Add JWT authentication to API endpoints`

`@create-issue` will:

- Open `.github/prompts/agents/create-issue.md`
- Show the exact copy/paste command to run the workflow via Copilot subagents

**Option B (direct):**

- Workflow prompt: `.github/prompts/agents/create-issue.md`
- Typical invocation:

  ```text
  @workspace /runSubagent create-issue "<issue description>"
  ```

Key behavior:

- `create-issue` is **issue creation only** (no PRs / no merges)
- Issues should follow `.github/ISSUE_TEMPLATE/feature_request.yml`
- For cross-repo changes, create linked issues in both repos and cross-reference

### 3) Implement one issue per PR (resolve-issue-dev)

For implementation, use the issue resolution workflow (or the `@issueagent` launcher).

#### Option A: fully automated selection + execution

- Type: `@issueagent`

This will:

- Pick the next issue in the required order
- Run the autonomous workflow (`scripts/work-issue.py --issue ...`)
- Stream progress into the chat

#### Option B: target a specific issue

- Use the workflow prompt: `.github/prompts/agents/resolve-issue-dev.md`
- Typical invocation:

  ```text
  @workspace /runSubagent resolve-issue-dev "implement issue #123"
  ```

Expected outputs:

- Code changes implemented according to acceptance criteria
- Tests added/updated
- Documentation updated (if required)
- A PR created

### 4) Merge PRs and close issues consistently (pr-merge)

Once a PR is ready, merge and close using the standard merge workflow.

- Docs: `docs/prmerge-command.md`
- Workflow prompt: `.github/prompts/agents/pr-merge.md`

This step matters because it enforces:

- PR description template compliance (CI gate)
- Clean merge + branch deletion
- Closing message with traceability
- Mandatory cleanup of temporary `.tmp/*` artifacts

### 5) Close issue only (no PR)

For purely administrative issues (or when no code change is needed):

- Workflow prompt: `.github/prompts/agents/close-issue.md`

---

## Recommended “daily” development loop

1. Start in VS Code chat
2. If you need to plan: run the planning workflow
3. For each resulting task: create a GitHub issue using `@create-issue`
4. Implement issues one-by-one (prefer `@issueagent` for sequential work)
5. Validate locally (tests/lint) as required
6. Merge via the merge workflow and ensure cleanup is done

---

## Guardrails (things that keep CI and the repo healthy)

- **Never commit** `projectDocs/` (it’s a separate git repo)
- **Never commit** `configs/llm.json` (local config)
- Keep routers thin; put logic in services/domain (DDD layering)
- Run the relevant test suite before merging
  - Backend: `pytest`
  - Web UI (if touched): `npm run lint && npm run build`

---

## Troubleshooting

### I don’t see `@issueagent` or `@create-issue`

- Ensure the local extension is installed from `.vscode/extensions/issueagent`
- Reload VS Code window
- Confirm VS Code is 1.85+

### `uvicorn` / python tools not found

- Activate the venv:

  ```bash
  source .venv/bin/activate
  ```

### Auto-approval prompts are slowing everything down

- See: `docs/VSCODE-GLOBAL-SETTINGS.md`
- Workspace settings: `.vscode/settings.json`

---

## Related references

- `ISSUEAGENT-CHAT-SETUP.md` — quick setup for the chat participant
- `.github/prompts/agents/README.md` — agent prompt catalog
- `docs/WORK-ISSUE-WORKFLOW.md` — detailed phase-based workflow definition
- `docs/prmerge-command.md` — merge + close + cleanup process

