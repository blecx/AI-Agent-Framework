# Audit Rule Pack v1 (Cross-Artifact)

This note summarizes the first backend cross-artifact audit rule pack introduced for Step 3 hardening.

## Rules

- `cross_reference`
  - Validates RAID `related_deliverables` references against deliverables in `artifacts/pmp.json`.
  - Emits an error when a referenced deliverable does not exist.

- `date_consistency`
  - Validates milestone `due_date` values in `artifacts/pmp.json` against project start/end dates from `metadata.json`.
  - Emits an error for dates before project start and a warning for dates after project end.

- `owner_validation`
  - Validates RAID `owner` values against governance team IDs in `artifacts/governance.json`.
  - Emits a warning when owner identifiers are unknown.

- `dependency_cycles`
  - Detects cycles in deliverable dependency graphs defined in `artifacts/pmp.json`.
  - Emits an error for detected cycles.

## Deterministic Output Behavior

Audit issues are sorted deterministically before being returned, using stable keys:

1. `rule`
2. `severity`
3. `artifact`
4. `item_id` / `milestone_id`
5. `message`

This ensures identical input data produces identical issue ordering and messages across runs.

## Validation Commands

- `./.venv/bin/python -m pytest tests/unit/test_audit_service.py -k "audit and cross" -q`
- `./.venv/bin/python -m pytest tests/integration/test_audit_rules.py -q`
