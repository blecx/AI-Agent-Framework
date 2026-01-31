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
   - **Workflow State Management**: Projects follow ISO 21500 aligned states with deterministic transitions.

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
   - **Audit Event System**: All significant actions are tracked in NDJSON format with full traceability.

---

## Workflow State Machine (ISO 21500 Aligned)

Projects follow a deterministic workflow state machine aligned with ISO 21500 project phases:

### States

1. **Initiating** - Project initiation and authorization
2. **Planning** - Project planning and preparation
3. **Executing** - Project execution and deliverable production
4. **Monitoring** - Performance monitoring and control
5. **Closing** - Project closure activities
6. **Closed** - Project formally closed (terminal state)

### Valid State Transitions

The workflow enforces these valid transitions:

- **Initiating → Planning**: Move to planning phase
- **Planning → Executing**: Start execution
- **Planning → Initiating**: Return to initiation for refinement
- **Executing → Monitoring**: Begin monitoring phase
- **Executing → Planning**: Return to planning for adjustment
- **Monitoring → Executing**: Return to execution for corrections
- **Monitoring → Closing**: Begin closure activities
- **Closing → Closed**: Finalize project closure

Invalid transitions (e.g., Initiating → Closed) are rejected with validation errors.

### API Endpoints

- `GET /api/v1/projects/{id}/workflow/state` - Get current workflow state
- `PATCH /api/v1/projects/{id}/workflow/state` - Transition to new state (validated)
- `GET /api/v1/projects/{id}/workflow/allowed-transitions` - Get valid transitions from current state

---

## Audit Event System

All significant project actions are logged as audit events in NDJSON format for compliance and traceability.

### Event Schema

Each audit event includes:

- `event_id`: Unique identifier (UUID)
- `event_type`: Type of event (e.g., workflow_state_changed, governance_metadata_created)
- `timestamp`: ISO 8601 timestamp
- `actor`: User or system that triggered the event
- `correlation_id`: Optional request correlation ID for tracing
- `project_key`: Associated project
- `payload_summary`: Event-specific data summary
- `resource_hash`: Optional SHA-256 hash for compliance

### Event Types

- `project_created` - Project creation
- `project_updated` - Project metadata updates
- `workflow_state_changed` - Workflow state transitions
- `governance_metadata_created/updated` - Governance changes
- `decision_created` - Decision log entries
- `raid_item_created/updated` - RAID register updates
- `artifact_created/updated` - Artifact changes
- `command_proposed/applied` - Command workflow actions

### API Endpoints

- `GET /api/v1/projects/{id}/audit-events` - Retrieve audit events
  - Query parameters: `event_type`, `actor`, `since`, `until`, `limit`, `offset`
  - Supports filtering and pagination

### Storage

Events are stored in `{project}/events/audit.ndjson` as append-only NDJSON (newline-delimited JSON) for:

- Efficient append operations
- Easy parsing and streaming
- Git-friendly format
- Compliance audit trails

---

## Step 1 (Thin Slice): RAID + Workflow States

**Step 1 is explicitly defined as a thin, end-to-end slice focused on:**

- **RAID Register** (Risks, Assumptions, Issues, Dependencies) – complete CRUD operations with filtering and tracking.
- **Workflow State Management** – deterministic ISO 21500-aligned state transitions (Initiating → Planning → Executing → Monitoring → Closing → Closed).
- **Audit Event System** – comprehensive event logging for all significant project actions.

### Step 1 Outcomes

By the end of Step 1, the system must support:

- Creating/selecting a project.
- Managing **RAID items** with full CRUD operations via WebUI and API.
- Transitioning projects through **workflow states** with validation.
- Capturing all significant actions in the **audit event log**.
- Testing all functionality (unit, integration, E2E tests).

### What's NOT in Step 1

The following features are explicitly moved to **Step 2** or later:

- **PMP (Project Management Plan)** artifacts
- **Templates** for artifact generation
- **Blueprints** for process definition
- **Proposals** workflow (AI-assisted changes)
- **Cross-artifact audits** and validation
- **AI-assisted content generation**

Step 1 establishes the foundational infrastructure (RAID tracking, workflow states, audit events) that later steps will build upon.

### Required Step 1 Capabilities

**RAID Register (minimum columns)**:

- Type (Risk/Assumption/Issue/Dependency)
- Title
- Description
- Owner
- Status (open, in-progress, mitigated, closed)
- Priority (low/medium/high)
- Impact assessment
- Due date / review date
- Mitigation strategy (for risks)

**Workflow State Management**:

- States: Initiating, Planning, Executing, Monitoring, Closing, Closed
- Valid transitions enforced (see "Workflow State Machine" section above)
- State history tracked in audit events

**Audit Event System**:

- All RAID operations logged (create, update, delete)
- All workflow transitions logged
- All project updates logged
- Events queryable with filtering and pagination

---

## WebUI Requirements (Step 1)

- Project selector / project creation page
- **RAID register management**:
  - List view with filtering (by type, status, priority)
  - Detail view for individual RAID items
  - Create/edit/delete RAID items
  - Sorting and pagination
- **Workflow state management**:
  - Display current project state
  - Workflow transition controls
  - Visual workflow diagram
- **Audit event log**:
  - Chronological event list
  - Filtering by event type, actor, date range
  - Event details and traceability

## Step 2 and Beyond

The following capabilities are planned for Step 2 or later phases:

- **PMP (Project Management Plan)** artifact generation
- **Templates** and **Blueprints** for artifact generation
- **AI-assisted content generation** and suggestions
- **Proposals workflow** (review and apply changes)
- **Cross-artifact audits** and validation
- **Advanced artifact relationships** and dependencies
- **Artifact editor** with structured fields + markdown
- **Blueprint-driven UI** navigation

These features build upon the Step 1 foundation (RAID + Workflow + Audit) to provide comprehensive project management capabilities.

## AI + Blueprint Behavior (Future Steps)

In future phases, AI and blueprints will enable:

- Blueprint defines which artifacts are required and the schema/required fields.
- AI can:
  - Draft initial artifacts from minimal project metadata.
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
