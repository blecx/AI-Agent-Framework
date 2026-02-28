# blecs UX Authority — Requirements & Gap Mitigation Plan

## Goal

Improve UX governance quality by strengthening `blecs-ux-authority`, validating all dependent modules/skills, and closing requirement gaps through a strict Plan → Issue → PR loop.

## Scope

### In Scope
- UX authority prompt contract hardening.
- UX module consistency checks and improvements.
- Related skills improvements (`design_guidelines`, `coder_change_plan`).
- Requirement coverage audit and explicit gap tracking.
- Standards-compliant issue slicing for backend and client follow-up.

### Out of Scope
- Broad product redesign.
- New UI features not tied to governance quality.
- Unrelated workflow automation changes.

## Requirement Baseline

1. Mandatory UX consultation for UI-affecting scope.
2. Deterministic decision contract: `UX_DECISION: PASS|CHANGES`.
3. Explicit requirement checks (navigation, responsive, grouping, a11y, PR evidence).
4. Explicit requirement-gap reporting with blocking/non-blocking disposition.
5. Traceable evidence in workflow artifacts and PR bodies.
6. Anti-bypass behavior for ambiguous scope.

## Detailed Gap-Check Plan

### Phase A — Contract Integrity (Prompt/Module Layer)
- Compare authority prompt with UX modules for schema parity.
- Verify all modules support the same decision vocabulary and checklist.
- Flag gaps: missing section, ambiguous criteria, conflicting language.

### Phase B — Runtime Enforcement Layer
- Verify workflow gate parsing and decision persistence behavior.
- Verify non-PASS decisions block progress in expected stages.
- Flag gaps: parser brittleness, weak failure messaging, bypass conditions.

### Phase C — Skills Layer
- Verify skills emit deterministic, requirement-aware outputs.
- Verify machine-usable artifacts exist for downstream issue/PR slicing.
- Flag gaps: missing fields, weak gap mapping, poor traceability.

### Phase D — CI & Policy Layer
- Verify PR evidence gates align with authority contract fields.
- Verify backend/client CI expectations are consistent.
- Flag gaps: schema drift between templates/scripts/workflows.

### Phase E — Regression Coverage Layer
- Add/adjust focused unit tests for authority-adjacent skills/modules.
- Add anti-bypass checks where behavior is policy-critical.
- Flag gaps: untested negative paths, weak edge-case coverage.

## Gap Classification Rubric

- **Blocking Gap:** Can permit merge/review without valid UX authority decision/evidence.
- **Major Gap:** Decision quality materially degraded but hard block still present.
- **Minor Gap:** Documentation/consistency issue with low bypass risk.

## Plan → Issue → PR Loop (Mandatory)

1. **Plan**
   - Update this plan with newly found gaps and severity.
   - Map each blocking/major gap to one issue only.
2. **Issue**
   - Create one issue per gap slice (S/M/L), with strict acceptance criteria.
   - Tag by domain (`agents`, `webui/ux`, `ci/cd`, `size:*`, `step:*`).
3. **PR**
   - Implement one issue per PR.
   - Include UX decision evidence and validation output in PR body.
   - Merge only when CI and UX evidence gates pass.
4. **Post-PR**
   - Re-run requirement matrix to confirm gap closure.
   - Update plan status and remove resolved gaps from active list.

## Validation Commands

- `./scripts/validate_prompts.sh`
- `./.venv/bin/python -m pytest tests/unit/test_designer_skills.py -q`
- `./.venv/bin/python -m scripts.check_issue_specs --paths "planning/issues/*.yml" --no-legacy --strict-sections`

## Current Status (This Iteration)

- Prompt contract strengthened with requirement/gap sections.
- UX modules aligned with anti-bypass + evidence rules.
- Related skills upgraded for requirement-aware outputs.
- Critical naming mismatch (`blecx` → `blecs`) fixed in workflow-authority agent definition.
- Requirement matrix artifact persisted per UX consultation run:
   - Path: `.tmp/ux-requirement-matrix-issue-<n>.md`
   - Columns: `Requirement | Status | Blocking | Evidence`
   - Categories: `navigation`, `responsive`, `grouping`, `a11y`, `pr_evidence`
