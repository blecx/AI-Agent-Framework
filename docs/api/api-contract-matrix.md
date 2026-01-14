# API Contract Matrix - Phase 1 Client Compatibility

This document provides a comprehensive mapping of API endpoints to client usage patterns after Phase 1 implementation.

## Endpoint Alignment Status

### ✅ Implemented - Project CRUD

| Client Usage | Endpoint | Method | Status | Notes |
|-------------|----------|--------|--------|-------|
| `getProject(key)` | `/api/v1/projects/{key}` | GET | ✅ Implemented | Returns ProjectInfo |
| `updateProject(key, data)` | `/api/v1/projects/{key}` | PUT | ✅ Implemented | Updates name, methodology |
| `deleteProject(key)` | `/api/v1/projects/{key}` | DELETE | ✅ Implemented | Soft-delete with audit trail |
| `createProject(data)` | `/api/v1/projects` | POST | ✅ Existing | Already implemented |
| `listProjects()` | `/api/v1/projects` | GET | ✅ Existing | Already implemented |

### ✅ Implemented - Info Endpoint

| Client Usage | Endpoint | Method | Status | Notes |
|-------------|----------|--------|--------|-------|
| `getInfo()` | `/info` | GET | ✅ Implemented | Returns { name, version } |
| `getInfo()` | `/api/v1/info` | GET | ✅ Implemented | Versioned, includes api_version |

### ✅ Implemented - Proposal API (Compatibility Layer)

| Client Usage | Endpoint | Method | Status | Notes |
|-------------|----------|--------|--------|-------|
| `createProposal(projectKey, command, params)` | `/api/v1/projects/{key}/proposals` | POST | ✅ Implemented | Wraps propose_command |
| `listProposals(projectKey)` | `/api/v1/projects/{key}/proposals` | GET | ✅ Implemented | Returns ProposalList |
| `getProposal(projectKey, proposalId)` | `/api/v1/projects/{key}/proposals/{id}` | GET | ✅ Implemented | Returns Proposal |
| `applyProposal(projectKey, proposalId)` | `/api/v1/projects/{key}/proposals/{id}/apply` | POST | ✅ Implemented | Applies proposal |
| `rejectProposal(projectKey, proposalId)` | `/api/v1/projects/{key}/proposals/{id}/reject` | POST | ✅ Implemented | Rejects proposal |

**Persistence**: Proposals are stored as NDJSON in `{project}/proposals/proposals.ndjson`

### ✅ Implemented - Command History

| Client Usage | Endpoint | Method | Status | Notes |
|-------------|----------|--------|--------|-------|
| `executeCommand(projectKey, command, params)` | `/api/v1/commands` | POST | ✅ Implemented | Global command execution |
| `getCommand(commandId)` | `/api/v1/commands/{id}` | GET | ✅ Implemented | Returns CommandHistory |
| `listCommands(projectKey?)` | `/api/v1/commands` | GET | ✅ Implemented | Optional projectKey filter |

**Persistence**: Commands are stored as NDJSON in `{project}/commands/commands.ndjson`

### ✅ Existing - Other Endpoints

| Client Usage | Endpoint | Method | Status | Notes |
|-------------|----------|--------|--------|-------|
| Project state | `/api/v1/projects/{key}/state` | GET | ✅ Existing | Already implemented |
| Artifacts | `/api/v1/projects/{key}/artifacts` | GET | ✅ Existing | Already implemented |
| Workflow | `/api/v1/projects/{key}/workflow/state` | GET | ✅ Existing | Already implemented |
| RAID | `/api/v1/projects/{key}/raid` | GET/POST/PUT/DELETE | ✅ Existing | Already implemented |
| Governance | `/api/v1/projects/{key}/governance` | GET/POST/PUT | ✅ Existing | Already implemented |
| Health | `/health`, `/api/v1/health` | GET | ✅ Existing | Already implemented |

## Backward Compatibility

All new endpoints are available both versioned (`/api/v1/*`) and unversioned (`/*`) for backward compatibility.

### Versioned Routes (Recommended)
- `/api/v1/info`
- `/api/v1/projects/{key}`
- `/api/v1/projects/{key}/proposals`
- `/api/v1/commands`

### Unversioned Routes (Deprecated)
- `/info`
- `/projects/{key}`
- `/projects/{key}/proposals`
- `/commands`

## Data Models

### ProjectUpdate
```json
{
  "name": "string (optional)",
  "methodology": "string (optional)"
}
```

### Proposal
```json
{
  "id": "string",
  "project_key": "string",
  "command": "string",
  "params": {},
  "status": "pending|applied|rejected",
  "assistant_message": "string",
  "file_changes": [...],
  "draft_commit_message": "string",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "applied_at": "ISO 8601 timestamp (optional)",
  "rejected_at": "ISO 8601 timestamp (optional)",
  "commit_hash": "string (optional)"
}
```

### CommandHistory
```json
{
  "id": "string",
  "project_key": "string",
  "command": "string",
  "params": {},
  "status": "pending|running|completed|failed",
  "created_at": "ISO 8601 timestamp",
  "started_at": "ISO 8601 timestamp (optional)",
  "completed_at": "ISO 8601 timestamp (optional)",
  "proposal_id": "string (optional)",
  "commit_hash": "string (optional)",
  "error_message": "string (optional)"
}
```

## Client Integration Checklist

### For AI-Agent-Framework-Client

- [x] GET /api/v1/projects/{key} - Returns single project
- [x] PUT /api/v1/projects/{key} - Updates project
- [x] DELETE /api/v1/projects/{key} - Soft-deletes project
- [x] GET /info - Returns app name and version
- [x] POST /api/v1/projects/{key}/proposals - Creates proposal
- [x] GET /api/v1/projects/{key}/proposals - Lists proposals
- [x] GET /api/v1/projects/{key}/proposals/{id} - Gets proposal
- [x] POST /api/v1/projects/{key}/proposals/{id}/apply - Applies proposal
- [x] POST /api/v1/projects/{key}/proposals/{id}/reject - Rejects proposal
- [x] POST /api/v1/commands - Executes command globally
- [x] GET /api/v1/commands - Lists commands with optional filter
- [x] GET /api/v1/commands/{id} - Gets command by ID

## Testing Status

- **Project CRUD**: 7/7 tests passing
- **Info Endpoint**: 2/2 tests passing
- **Proposal API**: 8/8 tests passing
- **Command History**: 5/5 tests passing
- **Total New Tests**: 22/22 passing ✅
- **Existing Tests**: 120/120 passing ✅
- **Total**: 142/142 passing ✅

## Known Limitations

1. **Proposal Persistence**: Proposals are stored in project-specific NDJSON files. In-memory cache is not persisted across server restarts for the existing propose/apply flow.
2. **Command Execution**: The POST /commands endpoint executes commands synchronously. Long-running commands may timeout.
3. **Soft Delete**: Deleted projects are marked with a `deleted: true` flag but files remain in git. List operations may need to filter deleted projects.

## Migration Guide for Clients

### Updating apiClient.ts

1. **Update base URL** to use `/api/v1/` prefix:
   ```typescript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
   ```

2. **Remove workarounds** for missing endpoints - all client methods now have corresponding backend endpoints.

3. **Test integration** using the validation scenarios in `docs/api/cross-repo-validation.md`.

## Future Enhancements (Phase 2/3)

- [ ] Async command execution with status polling
- [ ] Proposal expiration and cleanup
- [ ] Enhanced command history filtering (by status, date range)
- [ ] Command execution priority queue
- [ ] Real-time command/proposal status updates via WebSocket

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-14  
**Related Issues**: #25  
**PR Branch**: `copilot/align-api-contract-phase-1`
