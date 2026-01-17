# ADR-0006: Reusable Workflow for Client API Integration Tests

**Date:** 2026-01-17  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [Reusable workflow](../../.github/workflows/reusable-client-api-integration.yml), [Client integration guide](../api/client-integration-guide.md)

## Context

The project has multiple API consumers (web UI, CLI/TUI, and an external React/TypeScript client repository).
Client repositories need a reliable way to validate API compatibility in CI.

Challenges:

- The client repo CI needs a running backend API instance.
- Starting the backend should be consistent across repos.
- The backend compose setup bind-mounts `./projectDocs`, which must exist for the container to start.

## Decision

Provide a reusable GitHub Actions workflow in the backend repository that:

1. Checks out the caller (client) repository
2. Checks out the backend repository into `server/`
3. Ensures `server/projectDocs/` exists (for Docker bind-mount)
4. Starts the API container via `docker compose`
5. Waits for the health endpoint
6. Runs client tests with `API_BASE_URL` set
7. Tears down containers

Client repositories call this workflow to run deterministic API smoke checks (e.g., `npm run test:api`).

## Rationale

- Centralizes the “bring up backend for client CI” logic in one place
- Improves consistency and reduces duplicated YAML across repos
- Encourages stable API contracts and rapid feedback for integration breaks

## Consequences

### Positive

- Repeatable client API validation in CI
- Faster onboarding for new clients
- Less workflow drift between repositories

### Negative / Tradeoffs

- Client CI depends on the backend repo workflow interface remaining stable
- Docker-based integration tests add runtime cost to CI (mitigated via path filters and conditional runs)

## Alternatives Considered

- **Copy/paste compose startup into each client repo:** leads to drift and inconsistent fixes
- **Mock/stub API in client CI:** reduces confidence for real integration and contract compatibility
