# Project Plan (AI-Agent-Framework)

Last updated: 2026-01-10 (UTC)

## Project goal
Evolve the current MVP into a **full‑featured, multi‑team, professional WebUI client** with **feature parity with the TUI** (and a clear path to exceed it), enabling day‑to‑day use by multiple teams working concurrently across shared agents, tools, runs, and artifacts.

This plan is written to be kept **in sync with GitHub Issues** across:
- **blecx/AI-Agent-Framework** (backend + core engine)
- **blecx/AI-Agent-Framework-Client** (WebUI client)

---

## North-star outcomes
- A production-grade WebUI that matches TUI workflows for: creating/running agents, managing tools, streaming logs, inspecting artifacts, and operating multiple concurrent runs.
- Multi-team readiness: org/workspace boundaries, roles, secrets separation, audit trails, and safe collaboration.
- Clear contract between core and clients via a stable API and event model.
- Maintainable delivery: CI, tests, observability, release process, docs.

---

## 3-step execution plan (MVP → Pro)

### Step 1 — Parity foundation (make WebUI equivalent to TUI)
**Objective:** deliver the minimal set of capabilities necessary so a team can perform all critical TUI flows in the WebUI.

Key deliverables
- Stable API contract and versioning strategy (backend) + typed client SDK (client)
- Realtime event/streaming support (SSE/WebSocket) for logs, tool calls, and run state
- Core entities and UX flows: Agents, Runs, Tools, Artifacts, Logs
- Authn/z and basic user/workspace separation
- Baseline test coverage (API + UI smoke) and CI gates

Exit criteria
- Any workflow doable in TUI is doable in WebUI without regressions.


### Step 2 — Multi-team collaboration (professionalize)
**Objective:** enable robust multi-user, multi-workspace operation with safety, governance, and collaboration.

Key deliverables
- Workspaces/orgs, roles (RBAC), invitations, membership management
- Audit logging + run/tool history retention policies
- Secrets management model (scoped secrets, rotation) and secure tool configuration
- Concurrency and ownership controls (locks, run permissions)
- Shareable links, run/thread collaboration, commenting/annotations

Exit criteria
- Two independent teams can use the system concurrently without leaking data, stepping on each other’s resources, or losing traceability.


### Step 3 — Scale, extensibility, and enterprise polish
**Objective:** improve reliability, extensibility, and operator experience to reach “professional tool” maturity.

Key deliverables
- Plugin architecture for tools/agents + marketplace-ready packaging
- Observability: metrics, tracing, structured logs, dashboards
- Performance tuning for long runs, high event volume, large artifacts
- Offline/async job handling, retries, backpressure, resumable runs
- Releases: semantic versioning, changelogs, migration guides, upgrade tooling

Exit criteria
- Confident upgrades, predictable behavior under load, and an extensible platform with strong developer ergonomics.

---

## Mandatory top 10 capabilities (must-have)
These capabilities are required for the WebUI to be considered a full-featured professional client with TUI parity.

1. **TUI parity flows**: create/configure agents; start/stop runs; view run history.
2. **Realtime streaming**: logs/events/tool calls streamed live with clear state transitions.
3. **Workspace + RBAC baseline**: users, workspaces, role-based permissions.
4. **Tool management UI**: install/configure/enable tools; per-workspace tool availability.
5. **Secrets handling**: scoped secrets for tools/providers (never exposed to UI).
6. **Artifacts & files**: browse/download artifacts, outputs, and run attachments.
7. **Run inspector**: timeline view of steps, tool calls, prompts, responses, errors.
8. **Search & filtering**: runs/agents/tools searchable; filters by status, workspace, tags.
9. **Reliability & error UX**: retries, clear failure reasons, safe cancellation.
10. **Observability basics**: health endpoints, structured logs, minimal metrics.

---

## High-value nice-to-haves (top 10)
These are not required for parity but materially increase adoption and team productivity.

1. **Collaboration features**: comments, mentions, reactions on runs/threads.
2. **Run templates & presets**: reusable run configs, tool/agent bundles.
3. **Prompt/version management**: diff, history, rollback for agent configs.
4. **Policy controls**: allow/deny lists, cost budgets, rate limits.
5. **SSO/OIDC & SCIM**: enterprise identity integration.
6. **Fine-grained audit exports**: CSV/JSON exports for compliance.
7. **Notifications**: email/webhooks/Slack for run completion and failures.
8. **Plugin marketplace UI**: discover/install verified tool/plugin packages.
9. **Multi-model routing UI**: choose providers/models per agent/run with guardrails.
10. **Performance UX**: virtualized logs, partial loading, artifact streaming.

---

## Cross-repo status table (kept in sync with GitHub Issues)
This table is a **living index** and should be updated whenever issues are created/renamed/closed.

**How to keep in sync**
- For each row, link the canonical issue in the appropriate repository.
- Prefer one “tracking” issue that links to sub-issues. Keep the row pointing to the tracker.
- Update Status and Target as issues progress.

| Area | Repo | Tracking Issue | Status | Target |
|---|---|---|---|---|
| API contract + versioning | AI-Agent-Framework | (create issue) | Not started | Step 1 |
| Realtime events/streaming (SSE/WS) | AI-Agent-Framework | (create issue) | Not started | Step 1 |
| Typed client SDK | AI-Agent-Framework | (create issue) | Not started | Step 1 |
| WebUI core flows (Agents/Runs/Tools/Artifacts) | AI-Agent-Framework-Client | (create issue) | Not started | Step 1 |
| Auth + workspace baseline | AI-Agent-Framework | (create issue) | Not started | Step 1 |
| Tool management UI | AI-Agent-Framework-Client | (create issue) | Not started | Step 1 |
| Secrets model + storage | AI-Agent-Framework | (create issue) | Not started | Step 1/2 |
| Run inspector (timeline/tool calls) | AI-Agent-Framework-Client | (create issue) | Not started | Step 1 |
| Search & filtering | AI-Agent-Framework-Client | (create issue) | Not started | Step 1 |
| Observability basics | AI-Agent-Framework | (create issue) | Not started | Step 1 |
| RBAC + invitations | AI-Agent-Framework | (create issue) | Not started | Step 2 |
| Audit logging + retention | AI-Agent-Framework | (create issue) | Not started | Step 2 |
| Collaboration (share links/comments) | AI-Agent-Framework-Client | (create issue) | Not started | Step 2 |
| Plugin architecture | AI-Agent-Framework | (create issue) | Not started | Step 3 |
| Marketplace UI | AI-Agent-Framework-Client | (create issue) | Not started | Step 3 |
| Release process + migrations | AI-Agent-Framework | (create issue) | Not started | Step 3 |

---

## Notes / conventions
- Keep this file aligned with docs/project-plan.md (same structure; docs can be more verbose).
- Use consistent naming between plan headings and GitHub issue titles.
