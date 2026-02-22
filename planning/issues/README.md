# Planning Issue Specs

This directory stores issue specifications used for deterministic issue publishing.

## Canonical schema

Each file is a YAML mapping where repository aliases map to issue entries:

- `AI-Agent-Framework` (backend repository)
- `AI-Agent-Framework-Client` (client repository)

Each issue entry must include:

- `id` **or** `number`: stable source identifier (string)
- `title`: issue title (string)
- `labels`: non-empty list of labels
- `size_estimate` (or `size`, or `size:*` label)
- `body`: markdown containing all required sections:
  - `## Goal / Problem Statement`
  - `## Scope`
  - `## Acceptance Criteria`
  - `## Technical Approach`
  - `## Testing Requirements`
  - `## Documentation Updates`
  - `## Cross-Repository Coordination`

### Token-budget compliance (recommended)

For autonomous execution in constrained model environments, include concise issue bodies and avoid long narrative sections.

- Keep issue scope small (`S`/`M`) and one-issue-per-PR.
- Prefer short, runnable validation command lists.
- Reference files/paths instead of embedding long document excerpts.
- Add an optional section:
  - `## Token Budget Constraints`
  - checklist items for compact planning/review packets.

### Example (canonical)

```yaml
AI-Agent-Framework:
  - id: BE-001
    title: "Example backend issue"
    labels: ["backend/api", "size:S"]
    size_estimate: "S"
    body: |
      ## Goal / Problem Statement
      Explain the objective.

      ## Scope
      ### In Scope
      - Item A
      ### Out of Scope
      - Item B
      ### Dependencies
      - None

      ## Acceptance Criteria
      - [ ] Criterion 1

      ## Technical Approach
      - Implementation notes

      ## Testing Requirements
      - `pytest tests/unit -q`

      ## Documentation Updates
      - [ ] Update docs/development.md

      ## Cross-Repository Coordination
      No
```

## Migration note (legacy → canonical)

Older specs may use a structured shape (`plan`, `issue_template`, `tasks`, `dependencies`) instead of markdown `body`.

- Legacy format is still accepted by `scripts/check_issue_specs.py` during migration.
- The publisher converts legacy entries into canonical markdown issue bodies automatically.
- New or updated entries should use canonical `body` format.

## Validation

Run checks locally:

- `./scripts/validate_issue_specs.sh`
- `./scripts/validate_prompts.sh`

Strict mode (canonical-only, no legacy compatibility):

- `./.venv/bin/python scripts/check_issue_specs.py --paths "planning/issues/*.yml" --no-legacy --strict-sections`
