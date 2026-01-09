# Client Architecture Overview

**AI-Agent-Framework Multi-Client Architecture**

This document explains the design decisions behind the multi-client architecture and provides guidance on choosing the right client for your use case.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Client Components](#client-components)
3. [Why TUI is in Main Repository](#why-tui-is-in-main-repository)
4. [Why WebUI is in Separate Repository](#why-webui-is-in-separate-repository)
5. [API Communication](#api-communication)
6. [Authentication & Configuration](#authentication--configuration)
7. [Feature Comparison](#feature-comparison)
8. [Use Case Guide](#use-case-guide)

---

## Architecture Overview

The AI-Agent-Framework follows an **API-first architecture** where all functionality is exposed through REST API endpoints. Multiple client applications can consume these endpoints, each optimized for different use cases.

### Design Principles

1. **API-First**: All features available via REST API
2. **Client Independence**: Clients are independent consumers of the API
3. **Use Case Optimization**: Each client optimized for specific workflows
4. **Separation of Concerns**: Clear boundaries between API and presentation layers
5. **Technology Freedom**: Clients can use different technology stacks

### Component Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Client Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐    │
│  │   TUI    │  │ Built-in │  │   WebUI Client    │    │
│  │ (apps/   │  │  Web UI  │  │ (Separate Repo)   │    │
│  │  tui/)   │  │(apps/web)│  │  Enhanced UI      │    │
│  └──────────┘  └──────────┘  └───────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                    HTTP/REST API
                          │
┌─────────────────────────────────────────────────────────┐
│                   API Layer                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │           FastAPI Backend (apps/api/)            │  │
│  │  • Project Management  • LLM Integration         │  │
│  │  • Git Operations      • Template Processing     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                    Git Operations
                          │
┌─────────────────────────────────────────────────────────┐
│                  Storage Layer                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │    projectDocs/ (Separate Git Repository)       │  │
│  │    • Project documents  • Audit logs             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Client Components

### 1. TUI Client (apps/tui/)

**Technology**: Python CLI with Click framework  
**Location**: Main repository  
**Purpose**: Command-line automation and scripting

**Key Features**:
- ✅ All API operations (create, list, propose, apply, artifacts)
- ✅ Scriptable commands with clear output
- ✅ Environment variable configuration
- ✅ Docker and local Python support
- ✅ Exit codes for automation
- ✅ Colored output and progress indicators

**Strengths**:
- Fast execution and minimal overhead
- Perfect for CI/CD integration
- Works over SSH without graphics
- Easy to script and automate
- Lightweight dependencies

**Limitations**:
- Text-based output only
- No interactive visualization
- Limited UI polish
- Command-line knowledge required

### 2. Built-in Web UI (apps/web/)

**Technology**: React/Vite  
**Location**: Main repository  
**Purpose**: Basic visual interface

**Key Features**:
- ✅ Project creation and management
- ✅ Command execution with propose/apply workflow
- ✅ Artifact browsing and viewing
- ✅ Diff viewer for changes
- ✅ Real-time status updates

**Strengths**:
- Included in main repository
- Simple setup alongside API
- Visual interface for basic needs
- No additional configuration

**Limitations**:
- Basic feature set only
- Minimal visualizations
- Single-user focused
- Limited advanced features

### 3. WebUI Client (Separate Repository)

**Technology**: Modern web stack (see separate repository)  
**Location**: [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)  
**Purpose**: Advanced interactive project management

**Key Features**:
- ✅ Enhanced UI/UX with modern design
- ✅ Advanced visualizations and dashboards
- ✅ Team collaboration features
- ✅ Real-time updates and notifications
- ✅ Responsive design (desktop/tablet/mobile)
- ✅ Rich diff comparison tools
- ✅ Project insights and analytics

**Strengths**:
- Professional UI/UX design
- Rich interactive features
- Multi-user workflows
- Advanced visualizations
- Frequent feature updates

**Limitations**:
- Requires separate setup
- More complex deployment
- Additional configuration needed

---

## Why TUI is in Main Repository

The TUI client resides in the main repository (`apps/tui/`) for several strategic reasons:

### 1. Tight Integration for Testing

- **Development Validation**: Used during API development to immediately test new endpoints
- **Integration Tests**: Serves as integration test harness for API functionality
- **Fast Feedback**: Developers can quickly validate changes without UI complexity

### 2. Automation & CI/CD

- **Build Verification**: Essential for automated testing in CI/CD pipelines
- **Deployment Validation**: Verifies API health and functionality post-deployment
- **Regression Testing**: Automated tests can use TUI for end-to-end validation

### 3. Versioning Alignment

- **API Compatibility**: TUI version always matches API version
- **Breaking Changes**: TUI updates synchronously with API changes
- **Single Release**: Deployed together, ensuring compatibility

### 4. Minimal Dependencies

- **Lightweight**: Small dependency footprint (Click, httpx, Rich)
- **Fast Build**: Doesn't slow down Docker builds significantly
- **Simple Maintenance**: Easy to maintain alongside API code

### 5. Developer Workflow

- **Quick Testing**: `docker compose run tui health` for instant API validation
- **Debug Tool**: Developers use TUI for manual testing and debugging
- **Examples**: TUI code serves as API usage examples

### 6. Essential Tool

- **Core Functionality**: Considered essential for development and deployment
- **Not Optional**: Required for automated testing and validation
- **Infrastructure**: Part of development infrastructure, not just a client

---

## Why WebUI is in Separate Repository

The WebUI client is maintained independently at [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client) for important architectural reasons:

### 1. Independent Versioning

- **Release Cadence**: WebUI can release updates more frequently than API
- **Feature Velocity**: New UI features without waiting for API releases
- **Stability**: API remains stable while UI evolves rapidly
- **Semantic Versioning**: Independent version numbers (e.g., API 1.2 + WebUI 2.5)

### 2. Deployment Flexibility

- **Separate Scaling**: Scale WebUI independently from API
- **CDN Distribution**: Serve static WebUI from CDN
- **Multiple Versions**: Run different WebUI versions against same API
- **Geographic Distribution**: Deploy WebUI closer to users

### 3. Team Structure

- **Frontend Team**: Independent frontend development team
- **Backend Team**: Backend team focuses on API
- **Parallel Development**: Teams work without blocking each other
- **Specialized Skills**: Frontend experts optimize UI without API knowledge

### 4. Technology Stack Freedom

- **Modern Frameworks**: Use latest frontend frameworks without affecting API
- **Build Tools**: Independent build pipeline and tooling
- **Dependencies**: Large frontend dependencies don't bloat API container
- **Experimentation**: Test new technologies without risk to core system

### 5. Repository Size Management

- **Reduced Complexity**: Main repo stays focused on API
- **Build Speed**: Faster builds without large frontend assets
- **Version Control**: UI assets don't clutter API repository
- **Cleaner History**: Separate git history for UI and API changes

### 6. Client Choice Philosophy

- **Multiple Options**: Users choose between built-in Web UI or enhanced WebUI
- **Progressive Enhancement**: Start with built-in, upgrade to WebUI when needed
- **Opt-in Complexity**: Simple use cases don't need WebUI setup
- **Ecosystem Growth**: Encourages community clients and alternatives

---

## API Communication

All clients communicate with the API server using standard HTTP/REST protocols.

### Connection Configuration

Each client configures its API connection differently:

**TUI Client**:
```bash
# Environment variable
export API_BASE_URL=http://localhost:8000

# Or in apps/tui/.env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

**Built-in Web UI**:
```javascript
// Configured in vite.config.js proxy
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

**WebUI Client**:
```bash
# See WebUI repository for configuration
# Typically uses environment variables or config files
API_ENDPOINT=http://localhost:8000
```

### API Endpoints Used by Clients

| Endpoint | TUI | Built-in Web | WebUI | Purpose |
|----------|-----|--------------|-------|---------|
| `GET /health` | ✅ | ✅ | ✅ | Health check |
| `POST /projects` | ✅ | ✅ | ✅ | Create project |
| `GET /projects` | ✅ | ✅ | ✅ | List projects |
| `GET /projects/{key}/state` | ✅ | ✅ | ✅ | Get project state |
| `POST /projects/{key}/commands/propose` | ✅ | ✅ | ✅ | Propose command |
| `POST /projects/{key}/commands/apply` | ✅ | ✅ | ✅ | Apply proposal |
| `GET /projects/{key}/artifacts` | ✅ | ✅ | ✅ | List artifacts |
| `GET /projects/{key}/artifacts/{path}` | ✅ | ✅ | ✅ | Get artifact |

### Request/Response Format

All API communication uses JSON:

**Request Example**:
```json
POST /projects
{
  "key": "PROJ001",
  "name": "Website Redesign"
}
```

**Response Example**:
```json
{
  "key": "PROJ001",
  "name": "Website Redesign",
  "created_at": "2026-01-09T12:00:00Z"
}
```

### Error Handling

Clients handle API errors consistently:

| Status Code | Meaning | Client Action |
|-------------|---------|---------------|
| 200-299 | Success | Process response |
| 400 | Bad Request | Display validation error |
| 404 | Not Found | Show not found message |
| 500 | Server Error | Display error, suggest retry |
| 503 | Service Unavailable | Check API status |

---

## Authentication & Configuration

### Current State (v1.0)

**No authentication required** - The current version (1.0) does not implement authentication. All API endpoints are publicly accessible to any client that can reach the API server.

**Security Considerations**:
- API should be deployed behind firewall or VPN
- Use network-level security (Docker networks, internal networks)
- Consider this for development/internal use only

### Future Authentication (Planned)

Future versions will support:

1. **API Key Authentication**
   - Simple API key header
   - Per-client keys
   - Key rotation support

2. **OAuth 2.0**
   - Standard OAuth flow
   - Integration with identity providers
   - Token-based authentication

3. **JWT Tokens**
   - Stateless authentication
   - Claims-based authorization
   - Refresh token support

### Configuration Management

Each client manages configuration independently:

**TUI**: Environment variables and `.env` files  
**Built-in Web UI**: Vite proxy configuration  
**WebUI**: Application configuration (see separate repo)

---

## Feature Comparison

Detailed feature comparison across all clients:

| Feature | TUI | Built-in Web | WebUI Client | Notes |
|---------|-----|--------------|--------------|-------|
| **Project Management** |
| Create projects | ✅ | ✅ | ✅ | All clients support |
| List projects | ✅ | ✅ | ✅ | All clients support |
| Delete projects | ❌ | ❌ | ✅ | WebUI only |
| Project search | ❌ | ❌ | ✅ | WebUI only |
| **Command Execution** |
| Assess gaps | ✅ | ✅ | ✅ | All clients support |
| Generate artifact | ✅ | ✅ | ✅ | All clients support |
| Generate plan | ✅ | ✅ | ✅ | All clients support |
| Custom commands | ⚪ Manual | ❌ | ✅ | TUI: manual endpoint calls |
| **Proposal Review** |
| View proposals | ✅ Text | ✅ Modal | ✅ Enhanced | Different UX |
| Unified diff | ✅ Text | ✅ Basic | ✅ Syntax highlight | WebUI: best |
| Side-by-side diff | ❌ | ❌ | ✅ | WebUI only |
| Inline comments | ❌ | ❌ | ✅ | WebUI only |
| **Artifact Management** |
| List artifacts | ✅ | ✅ | ✅ | All clients support |
| View artifacts | ✅ Text | ✅ Preview | ✅ Rich preview | Different rendering |
| Download artifacts | ⚪ Manual | ❌ | ✅ | TUI: output redirect |
| Search artifacts | ❌ | ❌ | ✅ | WebUI only |
| **Visualization** |
| Gantt charts | ❌ | ⚪ Mermaid | ✅ Interactive | WebUI: best |
| Dashboards | ❌ | ❌ | ✅ | WebUI only |
| Project metrics | ❌ | ❌ | ✅ | WebUI only |
| Progress tracking | ❌ | ❌ | ✅ | WebUI only |
| **Collaboration** |
| Multi-user | N/A | ⚪ Basic | ✅ Full | WebUI: designed for teams |
| Real-time updates | ❌ | ⚪ Polling | ✅ WebSocket | WebUI: best |
| User management | N/A | N/A | ✅ | WebUI only (future) |
| Audit log viewing | ⚪ Manual | ❌ | ✅ | TUI: file access |
| **Automation** |
| Scriptable | ✅ Best | ❌ | ⚪ API | TUI: purpose-built |
| CI/CD integration | ✅ Best | ❌ | ❌ | TUI only |
| Batch operations | ✅ | ❌ | ⚪ | TUI: best |
| Exit codes | ✅ | N/A | N/A | TUI only |
| **Deployment** |
| Docker support | ✅ | ✅ | ✅ | All support Docker |
| Local development | ✅ | ✅ | ✅ | All support local |
| Cloud deployment | ⚪ | ✅ | ✅ Best | WebUI: optimized |
| CDN distribution | N/A | ⚪ | ✅ | WebUI: static assets |

**Legend**:
- ✅ Fully supported
- ⚪ Partially supported or basic implementation
- ❌ Not supported
- N/A Not applicable

---

## Use Case Guide

Choose the right client based on your specific needs:

### Use TUI Client For:

**✅ Best Choice When:**
- Automating project management tasks
- Integrating with CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions)
- Writing shell scripts for batch operations
- Working over SSH without graphical access
- Quick testing and validation of API functionality
- Running in Docker containers without UI
- Embedding in automation frameworks

**Example Scenarios**:
```bash
# CI/CD pipeline
docker compose run tui projects create --key BUILD-$(date +%Y%m%d) --name "Daily Build"
docker compose run tui commands propose --project BUILD-$(date +%Y%m%d) --command assess_gaps

# Batch processing
for project in PROJ001 PROJ002 PROJ003; do
  docker compose run tui commands propose --project $project --command assess_gaps
done

# Health monitoring
while true; do
  docker compose run tui health || alert_ops
  sleep 300
done
```

### Use Built-in Web UI For:

**✅ Best Choice When:**
- Getting started quickly without additional setup
- Simple visual interface is sufficient
- Single-user workflows
- Basic project management needs
- Learning the system
- Development and testing

**Example Scenarios**:
- Developer testing new features locally
- Quick demo to stakeholders
- Personal projects with basic needs
- Prototyping workflows before scaling

### Use WebUI Client For:

**✅ Best Choice When:**
- Managing multiple projects with teams
- Need rich interactive visualizations
- Non-technical users require user-friendly interface
- Advanced collaboration features needed
- Professional UI/UX is important
- Building project portfolios
- Enterprise deployment with many users

**Example Scenarios**:
- PMO managing portfolio of projects
- Team collaboration on large projects
- Executive dashboards and reporting
- Client presentations with rich visuals
- Multi-team coordination

---

## Getting Started

### Quick Start - TUI

```bash
# Check API health
docker compose run tui health

# Create project and run workflow
docker compose run tui projects create --key TEST001 --name "Test Project"
docker compose run tui commands propose --project TEST001 --command assess_gaps
```

See [apps/tui/README.md](../../apps/tui/README.md) for complete documentation.

### Quick Start - Built-in Web UI

```bash
# Start the system
docker compose up

# Open browser
open http://localhost:8080
```

See [QUICKSTART.md](../../QUICKSTART.md) for complete setup guide.

### Quick Start - WebUI Client

Visit the [AI-Agent-Framework-Client repository](https://github.com/blecx/AI-Agent-Framework-Client) for setup instructions.

---

## Related Documentation

- **[Main README](../../README.md)**: Project overview and architecture
- **[QUICKSTART](../../QUICKSTART.md)**: Setup and getting started guide
- **[TUI README](../../apps/tui/README.md)**: TUI client documentation
- **[ADR-0004](../adr/0004-separate-client-application.md)**: Architecture decision for separate clients
- **[WebUI Repository](https://github.com/blecx/AI-Agent-Framework-Client)**: Separate WebUI client

---

## Contributing

When contributing to client development:

1. **API Changes**: Update all affected clients
2. **New Features**: Consider which clients should support the feature
3. **Documentation**: Update this overview when adding client capabilities
4. **Testing**: Test changes across all relevant clients
5. **Compatibility**: Maintain backward compatibility where possible

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Status**: Active
