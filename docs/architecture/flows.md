# Interaction Flows and Sequence Diagrams

**Date:** 2026-01-11  
**Status:** Active  
**Last Updated:** 2026-01-11

## Overview

This document provides detailed interaction flows for key operations in the AI-Agent-Framework. Each flow is illustrated with sequence diagrams showing component interactions, data transformations, and decision points.

## Core Flows

### 1. Project Creation Flow

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant ProjectsRouter
    participant GitManager
    participant ProjectDocs
    
    User->>WebUI: Click "Create Project"
    WebUI->>User: Show project form
    User->>WebUI: Enter key="PROJ001", name="My Project"
    WebUI->>ProjectsRouter: POST /projects {key, name}
    
    Note over ProjectsRouter: Validate request
    ProjectsRouter->>ProjectsRouter: Check key format ^[a-zA-Z0-9_-]+$
    ProjectsRouter->>GitManager: create_project("PROJ001", "My Project")
    
    Note over GitManager: Initialize project
    GitManager->>ProjectDocs: Create directory PROJ001/
    GitManager->>ProjectDocs: Create project.json
    GitManager->>ProjectDocs: Create subdirectories (artifacts/, events/, etc.)
    GitManager->>ProjectDocs: git add .
    GitManager->>ProjectDocs: git commit -m "[PROJ001] Initialize project"
    
    GitManager-->>ProjectsRouter: ProjectInfo {key, name, created_at, updated_at}
    ProjectsRouter-->>WebUI: 201 Created {project info}
    WebUI-->>User: Show success + redirect to project view
```

**Key Points:**
- Validation happens at router level (Pydantic models)
- Git operations are atomic (all or nothing)
- Project directory structure created upfront
- Initial commit provides version history baseline

**Error Scenarios:**
- **409 Conflict:** Project key already exists
- **400 Bad Request:** Invalid key format
- **500 Internal Error:** Git operation failed

### 2. Propose/Apply Workflow (with LLM)

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant CommandsRouter
    participant CommandService
    participant GitManager
    participant LLMService
    participant OpenAI
    participant AuditService
    participant ProjectDocs
    
    Note over User,ProjectDocs: Phase 1: Propose
    User->>WebUI: Select "Generate Charter"
    WebUI->>CommandsRouter: POST /commands/propose {command: "generate_artifact", params: {artifact_type: "charter"}}
    CommandsRouter->>CommandService: propose_command("PROJ001", "generate_artifact", params)
    
    Note over CommandService: Gather context
    CommandService->>GitManager: read_file("PROJ001", "project.json")
    GitManager-->>CommandService: Project metadata
    CommandService->>GitManager: list_artifacts("PROJ001")
    GitManager-->>CommandService: Existing artifacts list
    
    Note over CommandService: Generate with LLM
    CommandService->>LLMService: generate(prompt, context)
    LLMService->>OpenAI: POST /v1/chat/completions
    alt LLM Success
        OpenAI-->>LLMService: Generated content
    else LLM Unavailable
        LLMService->>LLMService: _fallback_to_template()
    end
    LLMService-->>CommandService: Generated charter content
    
    Note over CommandService: Create proposal
    CommandService->>CommandService: Generate unified diff
    CommandService->>CommandService: Create proposal ID (UUID)
    CommandService->>CommandService: Store proposal in memory
    CommandService->>AuditService: log_event(COMMAND_PROPOSED)
    AuditService->>ProjectDocs: Append to events.ndjson
    
    CommandService-->>CommandsRouter: CommandProposal {proposal_id, file_changes, diff}
    CommandsRouter-->>WebUI: 200 OK {proposal}
    WebUI-->>User: Show diff viewer modal
    
    Note over User,ProjectDocs: Phase 2: Review
    User->>User: Review changes in diff viewer
    User->>WebUI: Click "Apply Changes"
    
    Note over User,ProjectDocs: Phase 3: Apply
    WebUI->>CommandsRouter: POST /commands/apply {proposal_id}
    CommandsRouter->>CommandService: apply_proposal("PROJ001", proposal_id)
    
    Note over CommandService: Commit changes
    CommandService->>CommandService: Retrieve proposal from memory
    CommandService->>GitManager: commit_changes("PROJ001", message, file_changes)
    GitManager->>ProjectDocs: Write artifacts/charter.md
    GitManager->>ProjectDocs: git add artifacts/charter.md
    GitManager->>ProjectDocs: git commit -m "[PROJ001] Generate project charter"
    GitManager-->>CommandService: Commit hash
    
    CommandService->>AuditService: log_event(COMMAND_APPLIED)
    AuditService->>ProjectDocs: Append to events.ndjson
    CommandService-->>CommandsRouter: CommandApplyResult {commit_hash, changed_files}
    CommandsRouter-->>WebUI: 200 OK {result}
    WebUI-->>User: Show success notification
```

**Key Points:**
- Two-phase workflow: propose → review → apply
- Context gathered from existing project state
- LLM integration with graceful fallback
- All changes committed atomically via git
- Full audit trail of propose and apply events

**Timing:**
- Propose: 1-5 seconds (LLM dependent)
- Apply: <1 second (git operations)

### 3. Governance Decision with RAID Linkage

```mermaid
sequenceDiagram
    actor PM as Project Manager
    participant WebUI
    participant GovernanceRouter
    participant RAIDRouter
    participant GovernanceService
    participant RAIDService
    participant GitManager
    participant ProjectDocs
    
    Note over PM,ProjectDocs: Step 1: Create Risk
    PM->>WebUI: Create RAID item (risk)
    WebUI->>RAIDRouter: POST /raid {type: "risk", title: "Resource retention risk", ...}
    RAIDRouter->>RAIDService: create_item("PROJ001", data)
    RAIDService->>GitManager: Read raid_register.json
    RAIDService->>RAIDService: Generate RISK001 ID
    RAIDService->>GitManager: Write updated raid_register.json
    GitManager->>ProjectDocs: git commit "[PROJ001] Create risk RISK001"
    RAIDService-->>RAIDRouter: RAIDItem {id: "RISK001", ...}
    RAIDRouter-->>WebUI: 201 Created
    WebUI-->>PM: Show risk created
    
    Note over PM,ProjectDocs: Step 2: Make Decision
    PM->>WebUI: Create governance decision
    WebUI->>GovernanceRouter: POST /governance/decisions {title: "Approve retention bonus", ...}
    GovernanceRouter->>GovernanceService: create_decision("PROJ001", data)
    GovernanceService->>GitManager: Read decisions.json
    GovernanceService->>GovernanceService: Generate DEC001 ID
    GovernanceService->>GitManager: Write updated decisions.json
    GitManager->>ProjectDocs: git commit "[PROJ001] Create decision DEC001"
    GovernanceService-->>GovernanceRouter: DecisionLogEntry {id: "DEC001", ...}
    GovernanceRouter-->>WebUI: 201 Created
    WebUI-->>PM: Show decision created
    
    Note over PM,ProjectDocs: Step 3: Link Decision to Risk
    PM->>WebUI: Link decision to risk
    WebUI->>GovernanceRouter: POST /governance/decisions/DEC001/link-raid/RISK001
    GovernanceRouter->>GovernanceService: link_decision_to_raid("DEC001", "RISK001")
    
    Note over GovernanceService: Update decision
    GovernanceService->>GitManager: Read decisions.json
    GovernanceService->>GovernanceService: Add RISK001 to linked_raid_ids
    GovernanceService->>GitManager: Write decisions.json
    
    Note over GovernanceService: Update RAID item (bidirectional)
    GovernanceService->>RAIDService: Update RAID item linked_decisions
    RAIDService->>GitManager: Read raid_register.json
    RAIDService->>RAIDService: Add DEC001 to linked_decisions
    RAIDService->>GitManager: Write raid_register.json
    
    GitManager->>ProjectDocs: git commit "[PROJ001] Link decision DEC001 to risk RISK001"
    GovernanceService-->>GovernanceRouter: Updated decision
    GovernanceRouter-->>WebUI: 200 OK
    WebUI-->>PM: Show linkage complete
    
    Note over PM,ProjectDocs: Step 4: Query Traceability
    PM->>WebUI: View risks for decision
    WebUI->>RAIDRouter: GET /raid/by-decision/DEC001
    RAIDRouter->>RAIDService: get_items_by_decision("DEC001")
    RAIDService->>GitManager: Read raid_register.json
    RAIDService->>RAIDService: Filter items where DEC001 in linked_decisions
    RAIDService-->>RAIDRouter: RAIDItemList {items: [RISK001]}
    RAIDRouter-->>WebUI: 200 OK {items}
    WebUI-->>PM: Show linked risks
```

**Key Points:**
- Bidirectional linking (decision ↔ RAID)
- Each operation committed separately
- Traceability maintained in both directions
- Queryable by decision or RAID item

### 4. Workflow State Transition

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant WorkflowRouter
    participant WorkflowService
    participant GitManager
    participant AuditService
    participant ProjectDocs
    
    Note over User,ProjectDocs: Initial State: INITIATING
    User->>WebUI: View project dashboard
    WebUI->>WorkflowRouter: GET /workflow/spine
    WorkflowRouter->>WorkflowService: get_spine("PROJ001")
    WorkflowService->>GitManager: Read workflow_state.json
    WorkflowService-->>WorkflowRouter: WorkflowStateInfo {current_state: "initiating"}
    WorkflowRouter-->>WebUI: 200 OK
    WebUI-->>User: Show "Project in Initiating phase"
    
    Note over User,ProjectDocs: Transition Request
    User->>WebUI: Click "Move to Planning"
    WebUI->>WorkflowRouter: POST /workflow/spine/execute {to_state: "planning", actor: "PM"}
    WorkflowRouter->>WorkflowService: execute_step("PROJ001", "planning", "PM")
    
    Note over WorkflowService: Validate transition
    WorkflowService->>WorkflowService: validate_transition("initiating", "planning")
    alt Valid Transition
        WorkflowService->>WorkflowService: Allowed
    else Invalid Transition
        WorkflowService-->>WorkflowRouter: 400 Bad Request "Invalid transition"
        WorkflowRouter-->>WebUI: 400 Error
        WebUI-->>User: Show error message
    end
    
    Note over WorkflowService: Update state
    WorkflowService->>GitManager: Read workflow_state.json
    WorkflowService->>WorkflowService: Create transition record
    WorkflowService->>WorkflowService: Update current_state to "planning"
    WorkflowService->>GitManager: Write workflow_state.json
    GitManager->>ProjectDocs: git commit "[PROJ001] Transition to planning phase"
    
    WorkflowService->>AuditService: log_event(WORKFLOW_STATE_CHANGED)
    AuditService->>ProjectDocs: Append to events.ndjson
    
    WorkflowService-->>WorkflowRouter: WorkflowStateInfo {current_state: "planning", ...}
    WorkflowRouter-->>WebUI: 200 OK
    WebUI-->>User: Show "Project moved to Planning"
```

**Key Points:**
- State transitions validated against ISO 21500 rules
- Transition history maintained
- Audit events logged for compliance
- UI reflects new state immediately

**Allowed Transitions:**
```mermaid
stateDiagram-v2
    [*] --> initiating
    initiating --> planning
    planning --> executing
    executing --> monitoring
    monitoring --> executing: Iteration
    executing --> closing
    closing --> closed
    closed --> [*]
```

### 5. Artifact Browsing and Retrieval

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant ArtifactsRouter
    participant GitManager
    participant ProjectDocs
    
    Note over User,ProjectDocs: List Artifacts
    User->>WebUI: Navigate to "Artifacts" tab
    WebUI->>ArtifactsRouter: GET /artifacts
    ArtifactsRouter->>GitManager: list_artifacts("PROJ001")
    GitManager->>ProjectDocs: List files in PROJ001/artifacts/
    GitManager->>ProjectDocs: Get git log for each file
    GitManager-->>ArtifactsRouter: List of ArtifactInfo with versions
    ArtifactsRouter-->>WebUI: 200 OK {artifacts: [...]}
    WebUI-->>User: Show artifacts table
    
    Note over User,ProjectDocs: View Artifact Content
    User->>WebUI: Click "charter.md"
    WebUI->>ArtifactsRouter: GET /artifacts/artifacts/charter.md
    ArtifactsRouter->>GitManager: read_file("PROJ001", "artifacts/charter.md")
    GitManager->>ProjectDocs: Read file content
    GitManager-->>ArtifactsRouter: File content (markdown)
    ArtifactsRouter-->>WebUI: 200 OK {content: "# Project Charter\n..."}
    WebUI->>WebUI: Render markdown with syntax highlighting
    WebUI-->>User: Show formatted charter
    
    Note over User,ProjectDocs: View Version History
    User->>WebUI: Click "Version History"
    WebUI->>ArtifactsRouter: GET /artifacts/artifacts/charter.md?versions=true
    ArtifactsRouter->>GitManager: get_file_versions("PROJ001", "artifacts/charter.md")
    GitManager->>ProjectDocs: git log -- artifacts/charter.md
    GitManager-->>ArtifactsRouter: Version list with commits
    ArtifactsRouter-->>WebUI: 200 OK {versions: [...]}
    WebUI-->>User: Show version timeline
```

**Key Points:**
- Read-only operations (no mutations)
- Git log provides complete version history
- Markdown rendered in UI with syntax highlighting
- Fast operations (<100ms typical)

### 6. RAID Filtering Workflow

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant RAIDRouter
    participant RAIDService
    participant GitManager
    participant ProjectDocs
    
    Note over User,ProjectDocs: View All RAID Items
    User->>WebUI: Navigate to RAID register
    WebUI->>RAIDRouter: GET /raid
    RAIDRouter->>RAIDService: list_items("PROJ001", {})
    RAIDService->>GitManager: Read raid_register.json
    RAIDService-->>RAIDRouter: RAIDItemList {items: [...], total: 50}
    RAIDRouter-->>WebUI: 200 OK
    WebUI-->>User: Show all 50 items
    
    Note over User,ProjectDocs: Filter by Type
    User->>WebUI: Select filter "Type: Risk"
    WebUI->>RAIDRouter: GET /raid?type=risk
    RAIDRouter->>RAIDService: list_items("PROJ001", {type: "risk"})
    RAIDService->>GitManager: Read raid_register.json
    RAIDService->>RAIDService: Filter items where type == "risk"
    RAIDService-->>RAIDRouter: RAIDItemList {items: [...], total: 20, filtered_by: {type: "risk"}}
    RAIDRouter-->>WebUI: 200 OK
    WebUI-->>User: Show 20 risks
    
    Note over User,ProjectDocs: Add Priority Filter
    User->>WebUI: Add filter "Priority: High"
    WebUI->>RAIDRouter: GET /raid?type=risk&priority=high
    RAIDRouter->>RAIDService: list_items("PROJ001", {type: "risk", priority: "high"})
    RAIDService->>GitManager: Read raid_register.json
    RAIDService->>RAIDService: Filter: type=="risk" AND priority=="high"
    RAIDService-->>RAIDRouter: RAIDItemList {items: [...], total: 8, filtered_by: {...}}
    RAIDRouter-->>WebUI: 200 OK
    WebUI-->>User: Show 8 high-priority risks
    
    Note over User,ProjectDocs: Add Status Filter
    User->>WebUI: Add filter "Status: Open"
    WebUI->>RAIDRouter: GET /raid?type=risk&priority=high&status=open
    RAIDRouter->>RAIDService: list_items("PROJ001", {type: "risk", priority: "high", status: "open"})
    RAIDService->>GitManager: Read raid_register.json
    RAIDService->>RAIDService: Filter: type=="risk" AND priority=="high" AND status=="open"
    RAIDService-->>RAIDRouter: RAIDItemList {items: [...], total: 5}
    RAIDRouter-->>WebUI: 200 OK
    WebUI-->>User: Show 5 open high-priority risks
```

**Supported Filters:**
- `type` - risk, assumption, issue, dependency
- `status` - open, in_progress, mitigated, closed, accepted
- `priority` - critical, high, medium, low
- `owner` - owner name/ID

**Filter Combination:** All filters use AND logic

### 7. Audit Event Retrieval

```mermaid
sequenceDiagram
    actor Admin
    participant WebUI
    participant WorkflowRouter
    participant AuditService
    participant ProjectDocs
    
    Admin->>WebUI: Navigate to "Audit Trail"
    WebUI->>WorkflowRouter: GET /workflow/audit/events?limit=100
    WorkflowRouter->>AuditService: get_events("PROJ001", {limit: 100})
    AuditService->>ProjectDocs: Read events.ndjson
    AuditService->>AuditService: Parse NDJSON (last 100 lines)
    AuditService-->>WorkflowRouter: AuditEventList {events: [...], total: 100}
    WorkflowRouter-->>WebUI: 200 OK
    WebUI-->>Admin: Show audit trail table
    
    Note over Admin,ProjectDocs: Filter by Event Type
    Admin->>WebUI: Filter "Event Type: Command Applied"
    WebUI->>WorkflowRouter: GET /audit/events?event_type=command_applied
    WorkflowRouter->>AuditService: get_events("PROJ001", {event_type: "command_applied"})
    AuditService->>ProjectDocs: Read events.ndjson
    AuditService->>AuditService: Filter where event_type == "command_applied"
    AuditService-->>WorkflowRouter: AuditEventList {events: [...]}
    WorkflowRouter-->>WebUI: 200 OK
    WebUI-->>Admin: Show filtered events
```

**Key Points:**
- NDJSON format for append-only audit log
- Privacy by design: only hashes stored by default
- Efficient pagination with limit/offset
- Filterable by event type, actor, date range

## Error Handling Flows

### Error Scenario: Proposal Not Found

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant CommandsRouter
    participant CommandService
    
    User->>WebUI: Click "Apply" (expired proposal)
    WebUI->>CommandsRouter: POST /commands/apply {proposal_id: "expired_id"}
    CommandsRouter->>CommandService: apply_proposal("PROJ001", "expired_id")
    CommandService->>CommandService: Lookup proposal in memory
    CommandService-->>CommandsRouter: None (not found)
    CommandsRouter-->>WebUI: 404 Not Found {detail: "Proposal not found or expired"}
    WebUI-->>User: Show error notification
```

### Error Scenario: Invalid State Transition

```mermaid
sequenceDiagram
    actor User
    participant WebUI
    participant WorkflowRouter
    participant WorkflowService
    
    User->>WebUI: Try to move from "initiating" to "closing"
    WebUI->>WorkflowRouter: POST /workflow/spine/execute {to_state: "closing"}
    WorkflowRouter->>WorkflowService: execute_step("PROJ001", "closing")
    WorkflowService->>WorkflowService: validate_transition("initiating", "closing")
    WorkflowService-->>WorkflowRouter: 400 Bad Request {detail: "Invalid transition"}
    WorkflowRouter-->>WebUI: 400 Error
    WebUI-->>User: Show error "Cannot skip workflow phases"
```

## Performance Optimization

### Caching Strategy

```mermaid
graph TB
    Request[API Request] --> Cache{Cache Hit?}
    Cache -->|Yes| Return[Return Cached Data]
    Cache -->|No| GitRead[Read from Git]
    GitRead --> Store[Store in Cache]
    Store --> Return
    
    TTL[TTL Expiry] --> Invalidate[Invalidate Cache]
    Mutation[Write Operation] --> Invalidate
```

**Cacheable Operations:**
- Project metadata (TTL: 5 minutes)
- Artifact listings (TTL: 1 minute)
- RAID register (invalidate on mutation)

### Async Operations

Long-running operations use async patterns:

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Background
    
    Client->>API: POST /commands/propose (long LLM call)
    API->>Background: Spawn async task
    API-->>Client: 202 Accepted {task_id: "abc123"}
    
    loop Poll Status
        Client->>API: GET /tasks/abc123/status
        API-->>Client: 200 OK {status: "processing"}
    end
    
    Background->>Background: Complete LLM call
    Background->>API: Update task status
    
    Client->>API: GET /tasks/abc123/status
    API-->>Client: 200 OK {status: "complete", result: {...}}
```

**Note:** Currently not implemented, but planned for future enhancement

## Related Documentation

- [Module Architecture](modules.md) - Component responsibilities
- [Data Models](data-models.md) - Request/response schemas
- [Extensibility Guide](extensibility.md) - Adding new flows
- [API Integration Guide](../api/client-integration-guide.md) - Client implementation

---

**Last Updated:** 2026-01-11  
**Maintained By:** Development Team  
**Status:** Active
