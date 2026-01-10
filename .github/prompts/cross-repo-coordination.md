# Cross-Repo Change Coordination Template

Use this prompt to help coordinate changes across the AI-Agent-Framework (backend) and AI-Agent-Framework-Client (frontend) repositories.

## Prompt

```
I need to coordinate a change across both repositories:
- AI-Agent-Framework (FastAPI backend)
- AI-Agent-Framework-Client (React/Vite frontend)

Change Description: [DESCRIBE THE CHANGE]

Please help me plan the coordination including:

1. **Impact Analysis**:
   - What changes in the backend?
   - What changes in the frontend?
   - Is this a breaking change?
   - Backwards compatibility considerations

2. **Implementation Order**:
   - Which repo to update first?
   - Can changes be made independently?
   - Do we need feature flags or versioning?

3. **Issue Creation Strategy**:
   - Backend issue title and key points
   - Frontend issue title and key points
   - How to link them (cross-repo references)

4. **API Contract**:
   - Document the API changes explicitly
   - Request/response formats
   - New/modified endpoints
   - Deprecation notices (if applicable)

5. **Testing Strategy**:
   - How to test backend changes independently?
   - How to test frontend with new backend?
   - Integration testing approach
   - Fallback behavior during transition

6. **Coordination Checklist**:
   - [ ] Backend issue created
   - [ ] Frontend issue created
   - [ ] Issues cross-referenced
   - [ ] API contract documented
   - [ ] Backend PR ready
   - [ ] Frontend PR ready
   - [ ] Integration tested
   - [ ] Merge order determined
   - [ ] Deployment coordinated

7. **Communication Plan**:
   - Who needs to be notified?
   - Timeline for changes
   - Rollback plan if issues arise
```

## Example Usage

**Input:**
```
Change Description: Add authentication to API endpoints using JWT tokens
```

**Expected Output:**
```markdown
## Cross-Repo Coordination: Add JWT Authentication

### Impact Analysis

**Backend (AI-Agent-Framework):**
- Add JWT middleware to FastAPI
- Protect existing endpoints with auth decorator
- Add /auth/login and /auth/refresh endpoints
- Update OpenAPI docs with security scheme
- Add user model and token generation

**Frontend (AI-Agent-Framework-Client):**
- Add login form component
- Store JWT in localStorage/secure cookie
- Add auth interceptor to API client
- Handle token refresh
- Redirect to login on 401
- Update all API calls to include token

**Breaking Change:** Yes
- All API endpoints except /auth/* will require authentication
- Existing clients will get 401 responses

**Backwards Compatibility:**
- Phase 1: Add auth but keep endpoints accessible (opt-in)
- Phase 2: Enforce auth after frontend is ready
- Use feature flag: `ENABLE_AUTH_ENFORCEMENT`

### Implementation Order

1. **Backend Phase 1** (Non-breaking)
   - Add auth middleware with feature flag disabled
   - Add /auth/login endpoint
   - Test authentication works when enabled
   - Merge to main (no impact yet)

2. **Frontend Phase 1** (Parallel)
   - Add login UI and auth logic
   - Update API client for tokens
   - Test against backend with flag enabled locally
   - Merge to main (gracefully handles no auth)

3. **Backend Phase 2** (Breaking)
   - Enable auth enforcement via feature flag
   - Remove feature flag after validation
   - Deploy coordinated with frontend

### Issue Creation

**Backend Issue (AI-Agent-Framework):**
```
Title: Add JWT authentication middleware

Description:
Implement JWT-based authentication for API endpoints to secure access.

Phase 1 (Non-breaking):
- Add JWT middleware with ENABLE_AUTH_ENFORCEMENT=false
- Implement /auth/login endpoint
- Add user model and token generation
- Document API changes

Phase 2 (Breaking):
- Enable auth enforcement
- Update all endpoints to require authentication

API Contract:
POST /auth/login
Request: { "username": "...", "password": "..." }
Response: { "access_token": "...", "refresh_token": "...", "expires_in": 3600 }

Protected endpoints require:
Header: Authorization: Bearer <token>

Related: blecx/AI-Agent-Framework-Client#XXX
```

**Frontend Issue (AI-Agent-Framework-Client):**
```
Title: Add JWT authentication and login flow

Description:
Implement login UI and auth handling to work with new JWT authentication.

Requirements:
- Login form component
- Token storage (localStorage)
- API client interceptor for auth header
- Token refresh logic
- Redirect to login on 401

Related: blecx/AI-Agent-Framework#YYY (Backend auth)

Depends on: Backend Phase 1 completion
```

### API Contract

**New Endpoints:**
```
POST /auth/login
Body: {
  "username": "string",
  "password": "string"
}
Response 200: {
  "access_token": "string",
  "refresh_token": "string",
  "expires_in": 3600
}
Response 401: {
  "detail": "Invalid credentials"
}

POST /auth/refresh
Body: {
  "refresh_token": "string"
}
Response 200: {
  "access_token": "string",
  "expires_in": 3600
}
```

**Modified Endpoints:**
All existing endpoints (except /auth/*) will require:
```
Header: Authorization: Bearer <access_token>

Response 401 if missing/invalid: {
  "detail": "Not authenticated"
}
```

### Testing Strategy

**Backend Independent Testing:**
```bash
# Setup
./setup.sh && source .venv/bin/activate
mkdir -p projectDocs

# Run with auth enabled
cd apps/api
export ENABLE_AUTH_ENFORCEMENT=true
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Test protected endpoint
TOKEN="<token from login>"
curl http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN"

# Test without token (should 401)
curl -i http://localhost:8000/api/projects
```

**Frontend with Backend:**
```bash
# Terminal 1: Run backend with auth
cd AI-Agent-Framework
source .venv/bin/activate
cd apps/api
export ENABLE_AUTH_ENFORCEMENT=true
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Terminal 2: Run frontend
cd AI-Agent-Framework-Client
npm install
npm run dev

# Test: Visit http://localhost:5173
# Should redirect to login
# After login, should access app normally
```

**Integration Testing:**
- Test full auth flow (login → access → logout)
- Test token expiration and refresh
- Test 401 redirect to login
- Test logout clears token
- Test protected routes vs public routes

### Coordination Checklist

- [ ] Backend Phase 1 issue created (#YYY)
- [ ] Frontend issue created (#XXX)
- [ ] Issues cross-referenced
- [ ] API contract documented in both issues
- [ ] Backend Phase 1 PR merged (auth available but not enforced)
- [ ] Frontend PR ready (tested against local backend)
- [ ] Integration tested (both services together)
- [ ] Frontend PR merged
- [ ] Backend Phase 2 PR ready (enable enforcement)
- [ ] Deployment coordinated (both deployed together)
- [ ] Monitoring in place for auth failures

### Communication Plan

**Before Starting:**
- Notify team of auth feature coming
- Share timeline (Week 1: Backend prep, Week 2: Frontend, Week 3: Enable)

**During Development:**
- Backend Phase 1 complete → notify frontend team
- Frontend ready → coordinate Phase 2 deployment

**Deployment:**
- Deploy backend Phase 2 and frontend together
- Monitor for 401 errors spike
- Have rollback plan (disable enforcement)

**Rollback Plan:**
If issues arise:
1. Set ENABLE_AUTH_ENFORCEMENT=false on backend
2. Redeploy backend only
3. Existing and new clients continue working
4. Fix issues and retry Phase 2
```

## Tips for Cross-Repo Coordination

- **Plan the API contract first** - agree on formats before implementation
- **Make backend changes backwards compatible when possible** - use feature flags
- **Version APIs for breaking changes** - e.g., /v1/ vs /v2/
- **Test integration early** - don't wait until both are "done"
- **Document changes clearly** - both teams need to understand impact
- **Coordinate deployments** - especially for breaking changes
- **Have rollback plans** - things can go wrong
- **Use semantic versioning** - helps track compatibility

## Common Cross-Repo Scenarios

1. **New Feature (Backend + Frontend)**
   - Backend first (API available)
   - Frontend second (consumes API)
   - Both can work independently

2. **Breaking Change**
   - Add new endpoint (non-breaking)
   - Update frontend to use new endpoint
   - Deprecate old endpoint
   - Remove old endpoint later

3. **Response Format Change**
   - Backend: Support both old and new format (version header)
   - Frontend: Update to request new format
   - Backend: Remove old format support

4. **New Required Field**
   - Backend: Make field optional initially
   - Frontend: Start sending field
   - Backend: Make field required after validation
