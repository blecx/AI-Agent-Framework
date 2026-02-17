# Documentation Quality Backlog

**Date:** 2026-02-17  
**Scope:** `docs/tutorials/**` + source-of-truth audit from `apps/api/**` and `apps/tui/**`  
**Method:** Route/command parity audit, coverage-gap scan, and tutorial artifact consistency review

## Source-of-truth baseline

### API surfaces verified

- Global commands: `POST/GET /api/v1/commands` and `GET /api/v1/commands/{command_id}`
- Workflow audit endpoints: `/projects/{project_key}/audit-events`, `/projects/{project_key}/audit`, `/projects/audit/bulk`, `/projects/{project_key}/audit/history`
- Governance endpoints: `/projects/{project_key}/governance/metadata`, `/projects/{project_key}/governance/decisions*`
- Template CRUD: `/api/v1/templates`
- Blueprint CRUD: `/api/v1/blueprints`
- Agent skills endpoints: `/api/v1/agents/{agent_id}/skills*`

### TUI command surface verified

- Available groups: `projects`, `commands`, `artifacts`, `config`, `health`
- Explicitly not exposed as TUI groups: `raid`, `workflow` (REST-only path in current tutorials)

## Qualified findings

### DOC-001

- **Category:** `accuracy`
- **Severity:** `high`
- **Location:** `docs/tutorials/validation/expected-outputs/advanced/01-hybrid-workflow.json` (step 3 command)
- **Evidence:**
  - Stale expected output uses `python main.py raid add --project TEST ...`
  - TUI command groups in `apps/tui/main.py` include `projects|commands|artifacts|config|health` only.
  - Tutorial baseline explicitly states no `raid` or `workflow` TUI groups: `docs/tutorials/tui-basics/01-quick-start.md` line 29.
- **User impact:** Validation artifacts can mislead users into trying unsupported TUI commands.
- **Proposed fix:** Replace stale expected output command with REST RAID action example or mark as REST-only validation step.
- **Workflow target:**
  - `plan-item`: P1-Validation-fixtures parity
  - `issue`: Docs validation fixture command parity
  - `pr-scope`: `docs/tutorials/validation/expected-outputs/advanced/01-hybrid-workflow.json`

### DOC-002

- **Category:** `undocumented-artifact`
- **Severity:** `medium`
- **Location:** Missing coverage in `docs/tutorials/**` for templates API
- **Evidence:**
  - Templates router exists with CRUD in `apps/api/routers/templates.py` (`@router.post/get/put/delete` lines 31, 50, 62, 85, 117).
  - Versioned route mounted in `apps/api/main.py` line 220 (`/api/v1/templates`).
  - No tutorial coverage found for `/api/v1/templates` in `docs/tutorials/**` during this audit.
- **User impact:** Users cannot discover how to manage system templates from tutorial docs.
- **Proposed fix:** Add an advanced tutorial for template lifecycle (create/list/get/update/delete) with curl and expected responses.
- **Workflow target:**
  - `plan-item`: P2-Template tutorial coverage
  - `issue`: Add templates API tutorial
  - `pr-scope`: `docs/tutorials/advanced/04-templates-api.md` + README links

### DOC-003

- **Category:** `undocumented-artifact`
- **Severity:** `medium`
- **Location:** Missing coverage in `docs/tutorials/**` for blueprints API
- **Evidence:**
  - Blueprints CRUD endpoints defined in `apps/api/routers/blueprints.py` (lines 31, 50, 62, 85, 112).
  - Versioned route mounted in `apps/api/main.py` line 222 (`/api/v1/blueprints`).
  - No tutorial coverage found for `/api/v1/blueprints` in `docs/tutorials/**` during this audit.
- **User impact:** Blueprint-driven artifact generation path is not discoverable for tutorial users.
- **Proposed fix:** Add blueprint tutorial and cross-link from artifact workflows.
- **Workflow target:**
  - `plan-item`: P3-Blueprint tutorial coverage
  - `issue`: Add blueprints API tutorial
  - `pr-scope`: `docs/tutorials/advanced/05-blueprints-api.md` + cross-links

### DOC-004

- **Category:** `undocumented-artifact`
- **Severity:** `medium`
- **Location:** Missing coverage in `docs/tutorials/**` for agent skills API
- **Evidence:**
  - Skills endpoints exist in `apps/api/routers/skills.py` (lines 30, 50, 85, 124, 164, 206).
  - Versioned prefix mounted in `apps/api/main.py` line 219 (`/api/v1/agents`).
  - No tutorial references found for `/api/v1/agents/{agent_id}/skills*` in `docs/tutorials/**` during this audit.
- **User impact:** Cognitive skills (memory/planning/learning) are effectively hidden from tutorial users.
- **Proposed fix:** Add dedicated API tutorial for skills usage with practical examples.
- **Workflow target:**
  - `plan-item`: P4-Skills tutorial coverage
  - `issue`: Add agent skills API tutorial
  - `pr-scope`: `docs/tutorials/advanced/06-agent-skills-api.md` + README links

### DOC-005

- **Category:** `coverage-gap`
- **Severity:** `medium`
- **Location:** Missing governance walkthrough in `docs/tutorials/**`
- **Evidence:**
  - Governance metadata/decision endpoints exist in `apps/api/routers/governance.py` (lines 28, 48, 81, 113, 129, 150, 175).
  - Governance routers are mounted in `apps/api/main.py` (v1 + deprecated includes around lines 211 and 252).
  - No governance endpoint tutorial references found in `docs/tutorials/**` during this audit.
- **User impact:** ISO governance capabilities are under-documented despite shipping in API.
- **Proposed fix:** Add governance tutorial covering metadata + decision log + RAID linkage.
- **Workflow target:**
  - `plan-item`: P5-Governance docs coverage
  - `issue`: Add governance API tutorial
  - `pr-scope`: `docs/tutorials/advanced/07-governance-api.md`

### DOC-006

- **Category:** `coverage-gap`
- **Severity:** `medium`
- **Location:** Missing workflow audit endpoints coverage in tutorials
- **Evidence:**
  - Workflow audit endpoints exist in `apps/api/routers/workflow.py`:
    - `GET /{project_key}/audit-events` (line 109)
    - `POST /{project_key}/audit` (line 162)
    - `POST /audit/bulk` (line 199)
    - `GET /{project_key}/audit/history` (line 273)
  - Current tutorials cover workflow state and allowed-transitions, but not audit endpoints.
- **User impact:** Users miss audit/assurance workflows that are core to governance and compliance.
- **Proposed fix:** Extend workflow tutorial with an “Audit Operations” section including examples and outputs.
- **Workflow target:**
  - `plan-item`: P6-Workflow audit tutorial extension
  - `issue`: Document workflow audit endpoints
  - `pr-scope`: `docs/tutorials/gui-basics/05-workflow-states.md` + `docs/tutorials/tui-basics/05-full-lifecycle.md`

### DOC-007

- **Category:** `coverage-gap`
- **Severity:** `low`
- **Location:** Missing global commands-history API coverage in tutorials
- **Evidence:**
  - Global command endpoints in `apps/api/routers/commands_global.py` (lines 23, 97, 116).
  - Mounted at `/api/v1/commands` in `apps/api/main.py` line 193.
  - Tutorials focus on project-scoped propose/apply but do not cover global command history retrieval.
- **User impact:** Users lack guidance for command observability/history use cases.
- **Proposed fix:** Add a short section in automation tutorial for command execution history queries.
- **Workflow target:**
  - `plan-item`: P7-Command history docs
  - `issue`: Document global commands endpoints
  - `pr-scope`: `docs/tutorials/advanced/03-automation-scripting.md`

### DOC-008

- **Category:** `consistency`
- **Severity:** `low`
- **Location:** `docs/tutorials/VALIDATION-REPORT.md` vs current validation fixtures
- **Evidence:**
  - Report states stale unsupported CLI usage was removed.
  - A stale unsupported TUI command remains in validation expected outputs (`DOC-001`).
- **User impact:** Readers may over-trust report completeness and miss remaining drift.
- **Proposed fix:** Update report wording to “tutorial guidance refreshed; validation fixtures still under follow-up” or close the fixture gap first and then revalidate report claims.
- **Workflow target:**
  - `plan-item`: P8-Validation report truthfulness
  - `issue`: Align validation report with fixture status
  - `pr-scope`: `docs/tutorials/VALIDATION-REPORT.md`

## Prioritized mitigation batches (Plan → Issue → PR → Merge)

- **Batch A (High impact, small):** `DOC-001`, `DOC-008`
- Goal: Remove known stale command drift and align validation report language.
- Status: ✅ Merged via PR #321

- **Batch B (Medium impact, additive):** `DOC-006`, `DOC-007`
- Goal: Close audit/history coverage gaps in existing tutorials.
- Status: ✅ Merged via PR #322

- **Batch C (Medium impact, additive):** `DOC-002`, `DOC-003`
- Goal: Add templates/blueprints capability tutorials.
- Status: ✅ Merged via PR #323

- **Batch D (Medium impact, additive):** `DOC-004`, `DOC-005`
- Goal: Add skills + governance tutorials for complete API capability coverage.
- Status: ✅ Merged via PR #324

## Traceability map

| Finding ID | Plan Item | Issue | PR Scope |
| --- | --- | --- | --- |
| DOC-001 | P1 | Backlog item | #321 |
| DOC-008 | P8 | Backlog item | #321 |
| DOC-006 | P6 | Backlog item | #322 |
| DOC-007 | P7 | Backlog item | #322 |
| DOC-002 | P2 | Backlog item | #323 |
| DOC-003 | P3 | Backlog item | #323 |
| DOC-004 | P4 | Backlog item | #324 |
| DOC-005 | P5 | Backlog item | #324 |

---

**Status:** ✅ All current findings remediated (2026-02-17)
