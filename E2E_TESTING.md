# End-to-End Testing Guide

## Overview

This document describes the E2E testing approach for the AI-Agent-Framework, including coordination between the backend (this repository) and the client repository.

## Backend E2E Support

The backend provides a test harness for E2E testing via `tests/e2e/backend_e2e_runner.py`.

### Running the Backend E2E Harness

#### Start Backend Server

```bash
# Start backend on default port 8000
python tests/e2e/backend_e2e_runner.py --mode server

# Start on custom port
python tests/e2e/backend_e2e_runner.py --mode server --port 8080

# Use custom docs path
python tests/e2e/backend_e2e_runner.py --mode server --docs-path /tmp/test-docs
```

#### Health Check

```bash
# Check if backend is healthy
python tests/e2e/backend_e2e_runner.py --mode health-check --url http://localhost:8000
```

#### Run Validation Suite

```bash
# Run full validation against running backend
python tests/e2e/backend_e2e_runner.py --mode validate --url http://localhost:8000

# Wait for backend to start, then validate
python tests/e2e/backend_e2e_runner.py --mode wait-and-validate --url http://localhost:8000 --timeout 60
```

### Backend E2E Test Scenarios

The backend E2E harness validates:

1. **Health Check**: Verifies `/health` endpoint returns healthy status
2. **Project Creation**: Creates a test project via `POST /projects`
3. **Project Listing**: Lists projects via `GET /projects`
4. **Project State**: Retrieves project state via `GET /projects/{key}/state`
5. **Artifact Listing**: Lists artifacts via `GET /projects/{key}/artifacts`
6. **Command Proposal**: Proposes a command via `POST /projects/{key}/commands/propose`

## Client E2E Testing (Cross-Repo)

### Architecture

```
┌─────────────────────────────────────────────┐
│  Client Repository (AI-Agent-Framework-      │
│                     Client)                  │
│  ┌─────────────────────────────────────┐    │
│  │  E2E Tests (Playwright/Cypress)     │    │
│  │  - UI Workflows                     │    │
│  │  - API Integration                  │    │
│  └────────────┬────────────────────────┘    │
│               │ HTTP Requests                │
└───────────────┼─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│  Backend Repository (AI-Agent-Framework)    │
│  ┌─────────────────────────────────────┐    │
│  │  FastAPI Backend                    │    │
│  │  - Project Management APIs          │    │
│  │  - Command APIs                     │    │
│  │  - Artifact APIs                    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Setup for Cross-Repo E2E

#### Option 1: Manual Backend Start

1. **In Backend Repo** (Terminal 1):
   ```bash
   cd AI-Agent-Framework
   python tests/e2e/backend_e2e_runner.py --mode server
   ```

2. **In Client Repo** (Terminal 2):
   ```bash
   cd AI-Agent-Framework-Client
   # Set backend URL
   export BACKEND_URL=http://localhost:8000
   # Run client E2E tests
   npm run test:e2e
   ```

#### Option 2: Docker Compose (Recommended)

Create a `docker-compose.e2e.yml` in the client repo:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ../AI-Agent-Framework
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - PROJECT_DOCS_PATH=/tmp/test-docs
    volumes:
      - backend-docs:/tmp/test-docs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 5s
      timeout: 3s
      retries: 10

  client-e2e:
    build:
      context: .
      dockerfile: Dockerfile.e2e
    depends_on:
      backend:
        condition: service_healthy
    environment:
      - BACKEND_URL=http://backend:8000
    command: npm run test:e2e

volumes:
  backend-docs:
```

Run with:
```bash
docker-compose -f docker-compose.e2e.yml up --abort-on-container-exit
```

#### Option 3: GitHub Actions Workflow

In the client repo, create `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Client Repo
        uses: actions/checkout@v4
        with:
          path: client
      
      - name: Checkout Backend Repo
        uses: actions/checkout@v4
        with:
          repository: blecx/AI-Agent-Framework
          path: backend
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Start Backend
        run: |
          cd backend
          mkdir -p /tmp/e2e-docs
          python tests/e2e/backend_e2e_runner.py --mode server --docs-path /tmp/e2e-docs &
          python tests/e2e/backend_e2e_runner.py --mode wait-and-validate --timeout 60
      
      - name: Install Client Dependencies
        run: |
          cd client
          npm ci
      
      - name: Run Client E2E Tests
        run: |
          cd client
          npm run test:e2e
        env:
          BACKEND_URL: http://localhost:8000
      
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-test-results
          path: client/test-results/
```

### Client E2E Test Examples

#### Example 1: Playwright Test (Recommended)

```typescript
// client/tests/e2e/project-workflow.spec.ts
import { test, expect } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

test.describe('Project Management Workflow', () => {
  test('should create and manage a project', async ({ page }) => {
    // Navigate to app
    await page.goto('/');
    
    // Create new project
    await page.click('button:has-text("New Project")');
    await page.fill('input[name="projectKey"]', 'E2E001');
    await page.fill('input[name="projectName"]', 'E2E Test Project');
    await page.click('button:has-text("Create")');
    
    // Verify project appears in list
    await expect(page.locator('text=E2E Test Project')).toBeVisible();
    
    // Open project
    await page.click('text=E2E Test Project');
    
    // Verify project details loaded
    await expect(page.locator('h1:has-text("E2E Test Project")')).toBeVisible();
    
    // Verify backend API was called
    const apiResponse = await page.waitForResponse(
      `${BACKEND_URL}/projects/E2E001/state`
    );
    expect(apiResponse.status()).toBe(200);
  });
  
  test('should propose and apply a command', async ({ page }) => {
    // Navigate to existing project
    await page.goto('/projects/TEST001');
    
    // Select command
    await page.selectOption('select[name="command"]', 'assess_gaps');
    await page.click('button:has-text("Propose")');
    
    // Wait for proposal
    await expect(page.locator('.proposal-preview')).toBeVisible();
    
    // Apply command
    await page.click('button:has-text("Apply")');
    
    // Verify success
    await expect(page.locator('text=Changes applied')).toBeVisible();
  });
});
```

#### Example 2: API Contract Test

```typescript
// client/tests/e2e/api-contract.spec.ts
import { test, expect } from '@playwright/test';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

test.describe('Backend API Contract', () => {
  test('health endpoint returns expected format', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
    expect(data).toHaveProperty('docs_path');
    expect(data).toHaveProperty('docs_exists');
    expect(data).toHaveProperty('docs_is_git');
  });
  
  test('project CRUD operations work', async ({ request }) => {
    const projectKey = `API${Date.now()}`;
    
    // Create
    const createResponse = await request.post(`${BACKEND_URL}/projects`, {
      data: { key: projectKey, name: 'API Test Project' }
    });
    expect(createResponse.status()).toBe(201);
    
    // Read
    const getResponse = await request.get(
      `${BACKEND_URL}/projects/${projectKey}/state`
    );
    expect(getResponse.ok()).toBeTruthy();
    
    // List
    const listResponse = await request.get(`${BACKEND_URL}/projects`);
    const projects = await listResponse.json();
    expect(projects.some(p => p.key === projectKey)).toBeTruthy();
  });
});
```

### Best Practices

#### Backend (This Repo)

1. **Maintain API Stability**: Avoid breaking changes to API endpoints
2. **Version APIs**: Use `/api/v1/` prefix for versioned endpoints
3. **Document Changes**: Update OpenAPI/Swagger docs for all API changes
4. **Test Isolation**: Each E2E test run uses isolated temp directory
5. **Health Checks**: Always provide `/health` endpoint for readiness checks

#### Client Repo

1. **Mock When Possible**: Use mocks for unit/component tests
2. **E2E for Integration**: Reserve E2E for full integration scenarios
3. **Parallel Execution**: Ensure tests can run in parallel without conflicts
4. **Cleanup**: Clean up test data after E2E runs
5. **CI Integration**: Run E2E tests in CI pipeline

### Troubleshooting

#### Backend Not Starting

```bash
# Check if port is in use
lsof -i :8000

# Check backend logs
python tests/e2e/backend_e2e_runner.py --mode server 2>&1 | tee backend.log

# Verify dependencies
pip install -r requirements.txt
```

#### Client Can't Reach Backend

```bash
# Test backend health
curl http://localhost:8000/health

# Check backend URL in client
echo $BACKEND_URL

# Test from within Docker network (if using Docker)
docker exec client-container curl http://backend:8000/health
```

#### Tests Flaky/Timeout

- Increase timeout in backend runner: `--timeout 60`
- Add retry logic in client tests
- Ensure backend is fully initialized before running tests
- Use deterministic test data (avoid random IDs)

### Maintenance

#### Adding New API Endpoints

When adding new endpoints to the backend:

1. Update backend E2E validation in `backend_e2e_runner.py`
2. Document endpoint in OpenAPI/Swagger
3. Create client issue for E2E coverage
4. Add client E2E tests in client repo
5. Update this document with examples

#### Coordinating Breaking Changes

When making breaking API changes:

1. Create issues in both repos
2. Link issues for traceability
3. Implement backend changes first
4. Update backend E2E harness
5. Coordinate client PR after backend merge
6. Version the API if appropriate

## CI/CD Integration

### Backend CI

Backend tests run automatically on:
- Push to `main`
- Pull requests
- Manual workflow dispatch

See `.github/workflows/ci.yml` for configuration.

### Client CI with Backend

Client E2E tests should:
1. Start backend via E2E runner or Docker
2. Wait for backend health check
3. Run client E2E tests
4. Tear down backend

## Support

For questions or issues:
- Backend: Create issue in `blecx/AI-Agent-Framework`
- Client: Create issue in `blecx/AI-Agent-Framework-Client`
- Cross-repo: Link issues between repositories
