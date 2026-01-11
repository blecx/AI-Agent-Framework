# Project Plan (ISO 21500/21502 Artifact Workflow)

This repository is organized around an **ISO 21500 / ISO 21502** inspired project-management workflow implemented as a **WebUI** (with optional **TUI/CLI** support) that uses **AI + blueprints** to generate, validate, and audit project artifacts.

The goal is to provide a predictable, testable “artifact workflow spine” where:

- Projects are created and configured.
- Artifacts are generated from templates/blueprints and refined via AI.
- Proposals/changes are reviewed and applied with traceability.
- Audits ensure artifacts remain consistent, complete, and compliant.

## Guiding Principles

- **Artifact-first**: Work is driven by the creation and evolution of explicit project artifacts.
- **Thin-slice delivery**: Every step delivers a minimal, end-to-end usable slice.
- **Blueprint-driven**: Blueprints declare what artifacts exist, required fields, and relationships.
- **AI-assisted, human-controlled**: AI drafts; humans approve and merge.
- **Testable workflow**: Every workflow capability must be covered by functional tests and E2E flows.

---

## ISO Workflow Spine (WebUI + AI + Blueprints)

The spine is the set of workflow stages the product must support:

1. **Projects**
   - Create/select a project.
   - Configure metadata (name, sponsor, manager, dates, constraints).

2. **Artifacts**
   - Generate and manage project artifacts (e.g., charter, PMP, RAID, schedule baseline).
   - Track versions and status (draft / reviewed / approved).

3. **Templates**
   - Provide structured templates for artifacts (fields, schema, required sections).
   - Enable validation for completeness.

4. **Blueprints**
   - Define collections of templates and rules that represent a process or methodology.
   - Drive UI navigation and required artifact sets.

5. **Proposals**
   - Changes to artifacts occur via proposals (AI-generated or human-authored).
   - Proposals include diffs and rationale; accepted proposals update artifacts.

6. **Audit**
   - Automated checks across artifacts (consistency, required fields, cross-references).
   - Audit results are actionable (errors/warnings) and can open issues.

---

## Step 1 (Thin Slice): PMP + RAID

**Step 1 is explicitly defined as a thin, end-to-end slice that produces two core artifacts:**

- **PMP (Project Management Plan)** – minimal viable structure sufficient to drive execution.
- **RAID (Risks, Assumptions, Issues, Dependencies)** – minimal viable tracking table.

### Step 1 Outcomes

By the end of Step 1, the system must support:

- Creating/selecting a project.
- Generating **PMP** and **RAID** artifacts from templates/blueprints.
- Editing artifacts in a WebUI (and optionally via TUI).
- Proposing AI-assisted changes (proposal) and applying accepted proposals.
- Running an **audit** that validates required fields and cross-artifact references.

### Required Step 1 Artifact Definitions (Minimum)

- **PMP (minimum sections)**
  - Purpose/overview
  - Scope statement
  - Deliverables list
  - Milestones (coarse)
  - Roles & responsibilities
  - Communications plan (minimal)
  - Change control approach (proposal-based)

- **RAID (minimum columns)**
  - Type (Risk/Assumption/Issue/Dependency)
  - Description
  - Owner
  - Status
  - Impact (low/med/high)
  - Due date / review date

---

## WebUI Requirements (Step 1)

- Project selector / project creation page
- Artifact navigation (PMP, RAID)
- Artifact editor (structured fields + markdown where appropriate)
- Proposal creation (AI-assisted suggestion + human edit)
- Proposal review/apply flow
- Audit page showing results + links back to fix

## AI + Blueprint Behavior (Step 1)

- Blueprint defines which artifacts are required (PMP + RAID) and the schema/required fields.
- AI can:
  - Draft initial PMP/RAID from minimal project metadata.
  - Suggest improvements as proposals.
  - Explain audit failures and propose fixes.

---

## Testing & Quality Gates (Required)

All functionality added for this plan must be test-driven and gated by CI.

### Test Placement Rules

- Every feature must include **functional tests** placed in dedicated `tests/` directories.
- Use a structure appropriate to the codebase, e.g.:
  - `tests/unit/…`
  - `tests/integration/…`
  - `tests/functional/…`
  - `webui/tests/…` (if the WebUI has its own test directory)

### E2E Requirements

- Provide **TUI-driven E2E tests** that simulate the end-to-end workflow:
  - create/select project → generate PMP/RAID → edit → propose → apply → audit.
- E2E tests must run non-interactively (scripted) in CI.

### Documentation

- Add/maintain `tests/README.md` describing:
  - how tests are organized
  - how to run unit/functional/E2E tests locally
  - how to run the TUI E2E suite

### Quality Gates

- CI must fail if:
  - tests fail
  - required functional tests for new features are missing
  - `tests/README.md` is missing or out of date for the added test suites

---

## Tracking

- Step work is tracked via `planning/issues/step-1.yml`.
- The canonical plan lives in `PLAN.md`.
- `docs/project-plan.md` must remain an **exact copy** of `PLAN.md`.
