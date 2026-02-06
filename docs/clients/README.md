# Client Documentation

**AI-Agent-Framework - Client Integration Guide**

This guide provides comprehensive documentation for all available clients and instructions for building custom clients.

---

## Overview

The AI-Agent Framework provides multiple client interfaces, all consuming the same REST API:

| Client | Type | Location | Status | Documentation |
|--------|------|----------|--------|---------------|
| **Web UI** | Graphical | `apps/web/` | ✅ Included | Integrated with Docker |
| **TUI** | Command-line | `apps/tui/` | ✅ Included | [apps/tui/README.md](../../apps/tui/README.md) |
| **Advanced Client** | CLI + Interactive | `client/` | ✅ Included | [client/README.md](../../client/README.md) |
| **WebUI** | Graphical (Enhanced) | Separate repo | ⚪ Optional | [GitHub Repository](https://github.com/blecx/AI-Agent-Framework-Client) |

---

## Available Clients

### 1. Web UI (Included)

**Location:** `apps/web/`

A React/Vite-based web interface included in the main repository.

**Features:**
- Project creation and selection
- Visual command execution
- Diff viewer for proposals
- Artifact browsing
- Real-time status updates

**Setup:**
```bash
# Docker (recommended)
docker compose up web

# Access at http://localhost:8080
```

**Best for:**
- Quick setup and deployment
- Basic project management
- Visual interaction
- Integrated Docker environment

---

### 2. TUI Client

**Location:** `apps/tui/`

A simple command-line interface for automation and scripting.

**Features:**
- Project management (create, list, get)
- Command workflow (propose, apply)
- Artifact access
- Rich terminal output with colors
- Scriptable and CI/CD-friendly

**Setup:**
```bash
# Docker
docker compose run tui health
docker compose run tui projects list

# Local
cd apps/tui
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py health
```

**Best for:**
- CI/CD pipelines
- Automation scripts
- Quick command-line operations
- Minimal environments

**Documentation:** [apps/tui/README.md](../../apps/tui/README.md)

---

### 3. Advanced Client

**Location:** `client/`

A Python client with both traditional CLI and interactive TUI modes (using Textual).

**Features:**
- **CLI Mode**: Traditional command-line interface
- **Interactive TUI Mode**: Visual terminal interface with menus
- Full API coverage
- Demo workflows
- Rich output formatting
- Mouse and keyboard navigation (TUI mode)

**Setup:**
```bash
# Docker - Interactive TUI
docker compose run client

# Docker - CLI
docker compose run client health
docker compose run client list-projects

# Local
cd client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.client tui  # Interactive
python -m src.client health  # CLI
```

**Best for:**
- Terminal-based workflows
- SSH/remote sessions with visual navigation
- API testing and validation
- Interactive and automated operations

**Documentation:** [client/README.md](../../client/README.md)

---

### 4. WebUI (Separate Repository)

**Repository:** [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)

An enhanced web interface in a separate repository with additional features.

**Features:**
- Enhanced UI/UX
- Additional customization options
- Independent release cycle
- Team collaboration features

**Setup:**
```bash
# Clone the repository
git clone https://github.com/blecx/AI-Agent-Framework-Client.git
cd AI-Agent-Framework-Client

# Follow setup instructions in the WebUI repository README
```

**Best for:**
- Enhanced features beyond basic web UI
- Customizable interface
- Independent updates
- Team collaboration

**Documentation:** See [WebUI Repository](https://github.com/blecx/AI-Agent-Framework-Client)

---

## Client Comparison

### Quick Comparison Table

| Feature | Web UI | TUI | Advanced Client | WebUI |
|---------|--------|-----|-----------------|-------|
| **Interface** | Browser | CLI | CLI + Interactive | Browser |
| **Setup** | 🟢 Easy | 🟢 Easy | 🟢 Easy | 🟡 Moderate |
| **Automation** | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Limited |
| **Visual Feedback** | ✅ Full | ⚪ Basic | 🟢 Rich | ✅ Full |
| **Remote Access** | ✅ Browser | ✅ SSH/Terminal | ✅ SSH/Terminal | ✅ Browser |
| **Scripting** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Updates** | 🔒 Coupled | 🔒 Coupled | 🔒 Coupled | ✅ Independent |

### Use Case Matrix

| Use Case | Recommended Client |
|----------|-------------------|
| Quick testing | Web UI, TUI |
| CI/CD automation | TUI, Advanced Client |
| Interactive management | Web UI, WebUI |
| Remote terminal work | Advanced Client |
| Team collaboration | WebUI |
| API validation | TUI, Advanced Client |
| Visual diff review | Web UI, WebUI |
| Scripting workflows | TUI, Advanced Client |
| Custom integrations | Build custom client |

---

## API Reference

All clients interact with the same REST API. Full API documentation is available at `http://localhost:8000/docs` (OpenAPI/Swagger).

### Core Endpoints

#### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "docs_exists": true
}
```

---

#### Create Project
```
POST /projects
Content-Type: application/json

{
  "key": "PROJ001",
  "name": "My Project"
}
```

**Response:**
```json
{
  "key": "PROJ001",
  "name": "My Project",
  "created_at": "2026-01-09T20:00:00Z"
}
```

---

#### List Projects
```
GET /projects
```

**Response:**
```json
{
  "projects": [
    {
      "key": "PROJ001",
      "name": "My Project",
      "created_at": "2026-01-09T20:00:00Z"
    }
  ]
}
```

---

#### Get Project State
```
GET /projects/{key}/state
```

**Response:**
```json
{
  "project": {
    "key": "PROJ001",
    "name": "My Project"
  },
  "artifacts": [...],
  "last_commit": "..."
}
```

---

#### Propose Command
```
POST /projects/{key}/commands/propose
Content-Type: application/json

{
  "command": "assess_gaps"
}
```

**Response:**
```json
{
  "proposal_id": "abc123",
  "message": "Generated gap assessment",
  "files": [
    {
      "path": "reports/gap_assessment.md",
      "content": "...",
      "change_type": "create"
    }
  ],
  "diff": "..."
}
```

---

#### Apply Proposal
```
POST /projects/{key}/commands/apply
Content-Type: application/json

{
  "proposal_id": "abc123"
}
```

**Response:**
```json
{
  "commit_hash": "def456",
  "message": "[PROJ001] Add gap assessment report"
}
```

---

#### List Artifacts
```
GET /projects/{key}/artifacts
```

**Response:**
```json
{
  "artifacts": [
    {
      "path": "artifacts/project_charter.md",
      "size": 1234,
      "modified": "2026-01-09T20:00:00Z"
    }
  ]
}
```

---

#### Get Artifact
```
GET /projects/{key}/artifacts/{path}
```

**Response:**
```json
{
  "path": "artifacts/project_charter.md",
  "content": "# Project Charter\n\n...",
  "modified": "2026-01-09T20:00:00Z"
}
```

---

## Authentication Guide

**Current Status:** No authentication required (v1.0.0)

**Future Considerations:**

If you need to add authentication:

1. **API Key Header**:
   ```
   Authorization: Bearer YOUR_API_KEY
   ```

2. **JWT Tokens**:
   - Login endpoint: `POST /auth/login`
   - Token refresh: `POST /auth/refresh`
   - Protected endpoints check token

3. **OAuth2**:
   - Use FastAPI's OAuth2 security
   - Support for multiple providers

**Implementation Examples:**

```python
# Python with API Key
import httpx

client = httpx.Client(
    base_url="http://localhost:8000",
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
```

```javascript
// JavaScript with API Key
const response = await fetch('http://localhost:8000/projects', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});
```

---

## Building a Custom Client

### Step-by-Step Guide

#### 1. Choose Your Technology Stack

**Options:**
- Python (httpx, requests)
- JavaScript/TypeScript (fetch, axios)
- Go (net/http)
- Rust (reqwest)
- Any language with HTTP support

#### 2. Set Up Your Project

**Python Example:**
```bash
mkdir my-client
cd my-client
python -m venv .venv
source .venv/bin/activate
pip install httpx click rich  # or your preferred libraries
```

**JavaScript Example:**
```bash
mkdir my-client
cd my-client
npm init -y
npm install axios commander chalk
```

#### 3. Create API Client Class

**Python Example:**
```python
# api_client.py
import httpx

class AIAgentClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.client = httpx.Client(base_url=base_url)
    
    def health_check(self):
        response = self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    def create_project(self, key, name):
        response = self.client.post("/projects", json={
            "key": key,
            "name": name
        })
        response.raise_for_status()
        return response.json()
    
    def list_projects(self):
        response = self.client.get("/projects")
        response.raise_for_status()
        return response.json()
    
    def get_project_state(self, key):
        response = self.client.get(f"/projects/{key}/state")
        response.raise_for_status()
        return response.json()
    
    def propose_command(self, key, command, **params):
        response = self.client.post(
            f"/projects/{key}/commands/propose",
            json={"command": command, **params}
        )
        response.raise_for_status()
        return response.json()
    
    def apply_proposal(self, key, proposal_id):
        response = self.client.post(
            f"/projects/{key}/commands/apply",
            json={"proposal_id": proposal_id}
        )
        response.raise_for_status()
        return response.json()
    
    def list_artifacts(self, key):
        response = self.client.get(f"/projects/{key}/artifacts")
        response.raise_for_status()
        return response.json()
    
    def get_artifact(self, key, path):
        response = self.client.get(f"/projects/{key}/artifacts/{path}")
        response.raise_for_status()
        return response.json()
```

#### 4. Implement CLI or GUI

**CLI with Click (Python):**
```python
# cli.py
import click
from api_client import AIAgentClient

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = AIAgentClient()

@cli.command()
@click.pass_obj
def health(client):
    """Check API health"""
    result = client.health_check()
    click.echo(f"Status: {result['status']}")

@cli.command()
@click.option('--key', required=True)
@click.option('--name', required=True)
@click.pass_obj
def create_project(client, key, name):
    """Create a new project"""
    result = client.create_project(key, name)
    click.echo(f"Created project: {result['key']}")

if __name__ == '__main__':
    cli()
```

#### 5. Add Error Handling

```python
import httpx

try:
    result = client.create_project("PROJ001", "Test")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        print("Project not found")
    elif e.response.status_code == 400:
        print(f"Bad request: {e.response.json()}")
    else:
        print(f"Error: {e}")
except httpx.RequestError as e:
    print(f"Connection error: {e}")
```

#### 6. Test Your Client

```python
# test_client.py
from api_client import AIAgentClient

client = AIAgentClient()

# Test health check
health = client.health_check()
assert health['status'] == 'healthy'

# Test project creation
project = client.create_project("TEST001", "Test Project")
assert project['key'] == "TEST001"

# Test project list
projects = client.list_projects()
assert any(p['key'] == "TEST001" for p in projects['projects'])
```

---

## Example Implementations

### Full Python CLI Client

See [apps/tui/](../../apps/tui/) for a complete implementation.

### Full Python Interactive Client

See [client/](../../client/) for a complete implementation with both CLI and TUI modes.

### JavaScript/TypeScript Client Starter

```typescript
// ai-agent-client.ts
interface Project {
  key: string;
  name: string;
  created_at: string;
}

interface Proposal {
  proposal_id: string;
  message: string;
  files: any[];
  diff: string;
}

class AIAgentClient {
  constructor(private baseUrl: string = 'http://localhost:8000') {}

  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async createProject(key: string, name: string): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, name })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async listProjects(): Promise<{ projects: Project[] }> {
    const response = await fetch(`${this.baseUrl}/projects`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async proposeCommand(
    key: string,
    command: string,
    params?: any
  ): Promise<Proposal> {
    const response = await fetch(
      `${this.baseUrl}/projects/${key}/commands/propose`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, ...params })
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async applyProposal(key: string, proposalId: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/projects/${key}/commands/apply`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proposal_id: proposalId })
      }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

export default AIAgentClient;
```

---

## Best Practices

### 1. Error Handling

Always handle HTTP errors and network failures:

```python
try:
    result = client.create_project("PROJ001", "Test")
except httpx.HTTPStatusError as e:
    # Handle specific HTTP errors
    print(f"HTTP {e.response.status_code}: {e.response.text}")
except httpx.RequestError as e:
    # Handle connection errors
    print(f"Connection error: {e}")
```

### 2. Timeouts

Set appropriate timeouts for API calls:

```python
client = httpx.Client(
    base_url="http://localhost:8000",
    timeout=30.0  # 30 seconds
)
```

### 3. Retries

Implement retry logic for transient failures:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def create_project_with_retry(client, key, name):
    return client.create_project(key, name)
```

### 4. Configuration

Use environment variables or config files:

```python
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
```

### 5. Logging

Add logging for debugging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Creating project {key}")
result = client.create_project(key, name)
logger.info(f"Project created: {result}")
```

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to API

**Solutions:**
1. Verify API is running: `curl http://localhost:8000/health`
2. Check firewall settings
3. Verify correct host/port
4. For Docker: Use `http://api:8000` (internal network)

### Authentication Errors

**Problem:** HTTP 401 or 403 errors

**Solutions:**
1. Check API key is set correctly
2. Verify token hasn't expired
3. Ensure proper authentication headers

### Timeout Errors

**Problem:** Requests timing out

**Solutions:**
1. Increase timeout value
2. Check network connectivity
3. Verify API is responding

### Invalid Requests

**Problem:** HTTP 400 errors

**Solutions:**
1. Verify request payload format
2. Check required fields are provided
3. Validate parameter types and values

---

## Contributing

We welcome contributions for new clients!

**To add a new client:**

1. Create client in separate directory or repository
2. Document setup and usage
3. Include examples and tests
4. Update this documentation
5. Submit pull request (if in main repo)

**Guidelines:**

- Use the REST API only (no shared code)
- Include comprehensive error handling
- Add clear documentation
- Provide usage examples
- Test all API operations

---

## Resources

### Documentation
- [Main README](../../README.md)
- [Quick Start Guide](../../QUICKSTART.md)
- [Development Guide](../development.md)
- [API Documentation](http://localhost:8000/docs) (when API is running)

### Client Implementations
- [TUI Client](../../apps/tui/README.md)
- [Advanced Client](../../client/README.md)
- [WebUI](https://github.com/blecx/AI-Agent-Framework-Client)

### API Specifications
- OpenAPI/Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Mobile Browser Compatibility

### Compatibility Matrix

| Browser | Desktop | Tablet (iPad/Android) | Phone | Notes |
|---------|---------|----------------------|-------|-------|
| Chrome | ✅ Full Support | ⚠️ Limited | ❌ Not Recommended | Touch gestures work, but UI not optimized |
| Firefox | ✅ Full Support | ⚠️ Limited | ❌ Not Recommended | Responsive design partial |
| Safari (iOS) | ✅ Full Support | ⚠️ Limited | ❌ Not Recommended | Works but viewport scaling issues |
| Edge | ✅ Full Support | ⚠️ Limited | ❌ Not Recommended | Similar to Chrome |

### Mobile-Specific Notes

**✅ What Works on Tablets:**
- Viewing project lists and artifacts
- Reading diff views (landscape orientation recommended)
- Monitoring command status
- Basic navigation and project selection

**⚠️ Tablet Limitations:**
- Touch interactions not optimized (designed for mouse/trackpad)
- Small UI elements may be difficult to tap accurately
- Text input fields may have focus issues
- Code diffs hard to read in portrait mode
- No pinch-to-zoom support in code viewers

**❌ Not Supported on Phones:**
- Screen too small for diff viewer and code artifacts
- UI components not responsive below 768px width
- Command proposal interface not usable
- File browser requires minimum 900px width

### Recommended Setup

**For Production Use:**
- Desktop browser (Chrome, Firefox, Edge, Safari)
- Minimum screen resolution: 1280x720
- Mouse and keyboard for optimal interaction

**For Monitoring Only:**
- Tablet in landscape mode (iPad, Android 10"+)
- Minimum screen width: 768px
- Read-only operations only

**Not Recommended:**
- Smartphones (any size)
- Portrait tablet mode
- Touch-only interaction for complex workflows

### Known Mobile Issues

1. **Touch Scrolling:** Code diff areas may not scroll properly with touch
2. **Modal Dialogs:** Proposal modals may overflow on small screens
3. **Text Selection:** Difficult to select/copy code on touch devices
4. **Keyboard:** Virtual keyboards may obscure input fields
5. **Performance:** Large diffs may cause lag on mobile devices

### Workarounds for Mobile Users

If you must access from mobile:

1. **Use Landscape Mode:** Always rotate tablet to landscape
2. **Zoom Out:** Use browser zoom (pinch or Ctrl+/-) to fit content
3. **Read-Only:** Avoid creating projects or applying commands
4. **TUI Alternative:** Use SSH + TUI client for mobile terminal access
5. **Remote Desktop:** Consider remote desktop to a full desktop environment

### Mobile Development Plans

Mobile optimization is not currently planned. The web UI is designed for:
- Desktop development workflows
- Professional project management
- Code review and diff viewing
- Complex multi-step interactions

For mobile access, we recommend:
- **SSH + TUI:** Command-line access via mobile terminal app (Termux, iSH)
- **Remote Desktop:** VNC/RDP to desktop environment
- **WebUI (Future):** Enhanced client may add responsive design

---

## Support

For issues or questions:
- Check the [main README](../../README.md)
- Review [API documentation](http://localhost:8000/docs)
- Open an issue on GitHub
- Check existing client implementations for examples

---

**Last Updated:** 2026-01-09  
**Version:** 1.0.0  
**Maintained By:** Development Team
