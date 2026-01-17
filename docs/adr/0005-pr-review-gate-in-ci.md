# ADR-0005: Enforce PR Review Gate in CI

**Date:** 2026-01-17  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [Backend CI workflow](../../.github/workflows/ci.yml), [PR template](../../.github/pull_request_template.md), [Review rubric prompt](../../.github/prompts/pr-review-rubric.md)

## Context

This project relies on a predictable workflow (Plan → Issues → PRs) and is frequently modified by both humans and agents.
In practice, PRs can fail review quality when they lack:

- A clear goal/context
- Verifiable acceptance criteria
- Evidence that validation was actually run
- Hygiene/safety guarantees (e.g., no committed `projectDocs/` or local secrets)

We need a lightweight, automatable mechanism that prevents under-specified PRs from merging while still allowing reviewers to focus on the code.

## Decision

Add a CI “PR review gate” for pull requests that validates the PR description structure and requires:

- Required sections exist (goal, acceptance criteria, validation evidence, hygiene)
- Checkboxes in those sections are present and checked
- For backend code changes under `apps/api/`, require explicit evidence that tests were run (checked `pytest` validation item), even when tests were not modified

This gate is implemented using `actions/github-script` in the backend CI workflow.

## Rationale

- PR descriptions are the shared contract between humans/agents and reviewers.
- A structured template + automated validation reduces review back-and-forth.
- Requiring _test execution evidence_ is more realistic than requiring test-file modifications for every backend change.

## Consequences

### Positive

- Higher PR quality and more deterministic reviews
- Clearer traceability (Goal → AC → Validation Evidence)
- Reduced risk of unsafe commits (repo hygiene checks)

### Negative / Tradeoffs

- Contributors must follow the template closely
- The gate can be strict if headings/checkbox formatting changes

## Alternatives Considered

- **No gate; rely on human review only:** insufficient consistency for agent-assisted changes
- **Require test-file modifications on every backend change:** causes false failures for formatting/docs-only or refactors; encourages noisy “test touch” commits
