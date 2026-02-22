# Plan: blecs Agent Migration

## Decision Answer

Current state is not fully compliant with your latest requirement because the implemented namespace is blecx, not blecs.

This rewritten plan enforces:

- own namespace: blecs
- Spec Kit-compatible behavior
- no interference with upstream Spec Kit

1. Introduce blecs UX/workflow authority agents.
2. Add reusable UX modules and delegation policy.
3. Wire autonomous workflow UX consultation gate.
4. Enforce PR UX evidence in CI for UI-affecting changes.
5. Migrate remaining agent prompts to consume workflow packets and UX delegation policy.

## Namespace and Compatibility Model

1. Keep core Spec Kit-compatible commands under a dedicated speckit command domain.
2. Introduce blecs command domain as additive extensions only.
3. Do not override, rename, or alter core Spec Kit-compatible command semantics.
4. Keep custom agent definitions separate from command prompt directories to prevent collisions.

## Non-Interference Rules

- blecs extensions must not shadow speckit command names.
- blecs commands may consume workflow packets and UX gates but must not mutate core Spec Kit flow contracts.
- CI checks validate coexistence, not replacement, of Spec Kit-compatible behavior.

## Phase 1 Completion Status

Status: Phase 1 completed and namespace alignment completed (blecs)

Delivered:

- UX authority and workflow authority custom agents
- reusable UX modules and mandatory delegation policy
- Spec Kit-compatible command prompt domains (`speckit.*` and `blecs.*`)
- runtime UX gate in autonomous workflow execution
- CI UX review gate for UI-affecting changes
- delegation wiring in existing agent contracts and rails

Namespace alignment completed:

- renamed namespace assets to blecs
- updated delegation references to `blecs-ux-authority`
- updated command extension names to `blecs.*`

## Optimization Recommendations

1. Add a shared UI-impact detector utility so runtime and CI use identical scope logic.
2. Add a validator for `.github/agents/speckit/*.md` and `.github/agents/blecs/*.md` frontmatter/contract checks.
3. Add a compact workflow-packet cache to reduce repeated long-context reads.
4. Add automated tests for CI gate logic (positive and negative PR-body examples).
5. Add model-role option for dedicated `ux` role in `agents/llm_client.py` when needed.

## Phase 2 Plan: Integration and Transition

1. Integrate `speckit.*` and `blecs.*` commands into operational scripts (`scripts/work-issue.py` and related workflows).
2. Route all issue planning to workflow packets from `blecs-workflow-authority`.
3. Require and persist UX consultation artifacts for UI issues in `.tmp/` and PR body evidence.
4. Migrate remaining agent prompts/workflows to consume Spec Kit artifacts (`.specify/` + `specs/`).
5. Add documentation for day-to-day usage and migration order across backend/client repos.
6. Add regression checks to ensure no agent bypasses UX authority for graphical design scope.

## Phase 2 Started

Started work completed:

- execution flow now builds a workflow packet (blecs workflow authority contract) before planning
- execution flow now persists UX consultation artifacts in `.tmp/ux-consult-issue-<issue>.md`
- UX gate runtime prompt text now uses blecs namespace

## Requirement Coverage Review

1. Own namespace (`blecs`) is implemented.
2. Spec Kit-compatible core flow remains in `speckit.*` command prompts.
3. blecs extensions are additive and separate from core speckit commands.
4. Directory and naming separation avoids collision with custom agent files.
5. Mandatory UX consultation is enforced in runtime flow, prompts, and CI gate text.

Open items (phase 2 continuation):

- operational script-level invocation of `speckit.*` command flow
- dedicated validators for command prompt contracts
- anti-bypass automated tests for UI/UX consultation policy

## Phase 2 Acceptance Criteria

- blecs namespace is the only custom extension namespace.
- speckit-compatible commands continue to behave as expected.
- no naming or discovery conflict between custom agents and command prompts.
- UX authority consultation remains mandatory for UI-affecting work.

## Phase 2 Issue Slicing (Canonical)

Issue slicing is now formalized in `planning/issues/phase-2-blecs-ux-authority.yml` with backend-first dependency order:

1. `P2-BE-01` Contract validator for `speckit.*` + `blecs.*` boundaries (S)
2. `P2-BE-02` Operational script wiring to explicit Spec Kit stage flow (M)
3. `P2-BE-03` Anti-bypass runtime/CI tests for mandatory UX consultation (M)
4. `P2-BE-04` Migration playbook and operational documentation (S)
5. `P2-UX-01` Client workflow consumption of UX packet contract (S)
6. `P2-UX-02` Client CI UX evidence gate alignment (S)

This sequencing preserves backend-first dependency constraints and keeps each issue small/reviewable for one-issue-per-PR execution.
