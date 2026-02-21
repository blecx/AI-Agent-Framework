# Issue authoring for planning specs

Author issues in `planning/issues/*.yml` using the canonical schema in `planning/issues/README.md`.

## Required quality rules

Each issue entry must include:

- Stable source ID (`id` or `number`)
- Non-empty `title`
- Non-empty `labels`
- Size metadata (`size_estimate`/`size` or `size:*` label)
- A complete markdown `body` with required sections

## Required body sections

- `## Goal / Problem Statement`
- `## Scope`
- `## Acceptance Criteria`
- `## Technical Approach`
- `## Testing Requirements`
- `## Documentation Updates`
- `## Cross-Repository Coordination`

## Local checks before publish

- `./scripts/validate_issue_specs.sh`
- `./scripts/validate_prompts.sh`

## Notes

- Legacy structured entries are accepted temporarily for migration.
- New content should be canonical `body` format.
