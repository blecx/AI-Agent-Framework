# UX Skill: Context Sources

Derive product intent from:

- `README.md`
- `docs/development.md`
- `docs/WORK-ISSUE-WORKFLOW.md`
- active UI code under `_external/AI-Agent-Framework-Client/client/`

Always summarize inferred intent before proposing navigation/layout changes.

Source precedence for conflicts:
1. Implemented runtime/CI behavior
2. Active code paths and tests
3. Current workflow documentation
4. Historical planning notes

Confidence rule:
- If confidence is low due to missing evidence, record it as a requirement gap.
