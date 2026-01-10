# Documentation Index

**AI-Agent-Framework Documentation Hub**

Welcome to the comprehensive documentation for the ISO 21500 Project Management AI Agent system. This index provides quick access to all project documentation organized by type and topic.

---

## Quick Start

**New to the project?** Start here:

1. **[Project README](../README.md)** - Overview, architecture, and features
2. **[Quick Start Guide](../QUICKSTART.md)** - Step-by-step setup instructions
3. **[Development Guide](development.md)** - Complete local development guide
4. **[MVP Specification](spec/mvp-iso21500-agent.md)** - Detailed system specification

**Quick Links:**
- 🚀 [Setup Guide](../QUICKSTART.md)
- 💻 [Development Guide](development.md)
- 📖 [API Documentation](http://localhost:8000/docs) (when running)
- 🎮 [Client Documentation](clients/README.md) - All client interfaces
  - 🔧 [TUI Client](../apps/tui/README.md) - Command-line automation
  - 🖥️ [Advanced Client](../client/README.md) - CLI + Interactive TUI
  - 🌐 [WebUI Client](https://github.com/blecx/AI-Agent-Framework-Client) - Separate repository
- 🏗️ [Architecture Decisions](adr/)
- 💬 [Development Discussions](chat/)
- 📝 [How-To Guides](howto/)

---

## System Architecture

The AI Agent Framework uses a three-container architecture for maximum flexibility:

### Container Overview

| Container | Purpose | Port | Required |
|-----------|---------|------|----------|
| **api** | FastAPI backend - Core logic and API endpoints | 8000 | ✅ Yes |
| **web** | React/Vite frontend - Visual user interface | 8080 | ✅ Yes |
| **client** | Python CLI - API consumer and automation tool | N/A | ⚪ Optional |

### Architecture Diagram

```
┌─────────────────┐
│    Web UI       │  ← Visual Interface (Interactive)
│  React/Vite     │
│   (Port 8080)   │
└────────┬────────┘
         │
         │  HTTP/REST
         │
         ▼
┌─────────────────┐         ┌──────────────────┐
│   API Server    │◄────────│  Python Client   │  ← CLI Interface (Automation)
│    FastAPI      │         │  (Optional)      │
│   (Port 8000)   │         └──────────────────┘
└────────┬────────┘
         │
         │  Git Operations
         │
         ▼
┌─────────────────┐
│  projectDocs/   │  ← Separate Git Repository
│  (Git Repo)     │     (Project Documents)
└─────────────────┘
```

### Client Architecture

The AI-Agent Framework provides **multiple client interfaces** to support different workflows:

#### Available Clients

1. **Web UI (Included)** - `apps/web/`
   - React/Vite frontend included in this repository
   - Port: 8080
   - Integrated with Docker setup

2. **TUI Client** - `apps/tui/`
   - Simple command-line interface for automation
   - Scriptable and CI/CD-friendly
   - Included in this repository

3. **Advanced Client** - `client/`
   - Python-based client with CLI + Interactive TUI modes
   - Uses Textual for rich terminal interface
   - Included in this repository
   - Optional component

4. **WebUI (Separate Repository)** - [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)
   - Enhanced web interface with additional features
   - Independent updates and customization
   - Alternative to the included web UI

#### Client Separation Strategy

**Why multiple clients?**

- **API-First Design**: All clients consume the same REST API, validating the API-first architecture
- **Flexibility**: Choose the interface that fits your workflow
- **Independence**: Each client can evolve without affecting others
- **Specialization**: Each client optimized for specific use cases

**Why a separate WebUI repository?**

- **Independent Development**: WebUI can evolve on its own release cycle
- **Customization**: Users can fork and customize without affecting the core framework
- **Lighter Core**: Keeps the main repository focused on the API/backend
- **Multiple Options**: Users can choose between the included web UI or the enhanced WebUI

#### Client Comparison

| Client | Location | Interface Type | Best For | Required |
|--------|----------|----------------|----------|----------|
| **Web UI** | `apps/web/` | Graphical (Browser) | Quick setup, basic features | ✅ Included |
| **TUI** | `apps/tui/` | Command-line | CI/CD, scripting, automation | ⚪ Optional |
| **Advanced Client** | `client/` | CLI + Interactive Terminal | Terminal workflows, API testing | ⚪ Optional |
| **WebUI** | Separate repo | Graphical (Browser) | Enhanced features, team use | ⚪ Optional |

#### When to Use Each Interface

**Use Web UI (`apps/web/`) when:**
- Need quick setup with Docker
- Want basic project management features
- Prefer integrated deployment
- Starting with the framework

**Use TUI (`apps/tui/`) when:**
- Writing automation scripts
- Running in CI/CD pipelines
- Need simple, fast command-line operations
- Working in minimal environments

**Use Advanced Client (`client/`) when:**
- Working in terminal/SSH sessions but want visual navigation
- Need interactive feedback in terminal
- Debugging or testing the API
- Want both CLI scripting and interactive TUI modes

**Use WebUI (separate repo) when:**
- Need enhanced features beyond basic web UI
- Want customizable interface
- Need independent update cycle
- Working with teams requiring rich collaboration features

**Use Direct API when:**
- Building custom integrations
- Creating your own client in another language
- Advanced automation needs not covered by existing clients

#### API Integration Guide for Client Developers

**Building a New Client:**

All clients communicate via the REST API. To build a new client:

1. **API Endpoint Reference**: See `http://localhost:8000/docs` (OpenAPI/Swagger)

2. **Core Endpoints**:
   - `GET /health` - API health check
   - `POST /projects` - Create project
   - `GET /projects` - List projects
   - `GET /projects/{key}/state` - Get project state
   - `POST /projects/{key}/commands/propose` - Propose command
   - `POST /projects/{key}/commands/apply` - Apply proposal
   - `GET /projects/{key}/artifacts` - List artifacts
   - `GET /projects/{key}/artifacts/{path}` - Get artifact content

3. **Authentication**: Currently no authentication (add if needed for your use case)

4. **Example Request/Response**: See [client implementation examples](#example-implementations)

5. **Best Practices**:
   - Always check API health before operations
   - Handle proposal IDs from propose/apply workflow
   - Parse error responses gracefully
   - Use timeouts for long-running operations

For detailed client implementation examples:
- **TUI Client**: [apps/tui/README.md](../apps/tui/README.md)
- **Advanced Client**: [client/README.md](../client/README.md)
- **WebUI**: [blecx/AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)

#### Example Implementations

**Python (using httpx):**
```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

# Health check
response = client.get("/health")
print(response.json())

# Create project
response = client.post("/projects", json={
    "key": "PROJ001",
    "name": "My Project"
})
project = response.json()

# Propose command
response = client.post(f"/projects/{project['key']}/commands/propose", json={
    "command": "assess_gaps"
})
proposal = response.json()

# Apply proposal
response = client.post(f"/projects/{project['key']}/commands/apply", json={
    "proposal_id": proposal["proposal_id"]
})
result = response.json()
```

**JavaScript/TypeScript (using fetch):**
```javascript
const API_BASE = 'http://localhost:8000';

// Health check
const health = await fetch(`${API_BASE}/health`);
const healthData = await health.json();

// Create project
const project = await fetch(`${API_BASE}/projects`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: 'PROJ001', name: 'My Project' })
});
const projectData = await project.json();

// Propose command
const proposal = await fetch(`${API_BASE}/projects/PROJ001/commands/propose`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ command: 'assess_gaps' })
});
const proposalData = await proposal.json();
```

For complete API documentation, run the API server and visit: `http://localhost:8000/docs`

---

## Documentation Structure

```
docs/
├── README.md                          # This file
├── development.md                     # Local development guide
├── architecture/                      # System architecture documentation
├── deployment/                        # Deployment guides
├── api/                               # API and client integration guides
├── spec/                              # Formal specifications
├── adr/                               # Architecture Decision Records
├── chat/                              # Development transcripts
└── howto/                             # Procedural guides
```

---

## Architecture Documentation

Comprehensive system architecture and design documentation.

| Document | Description | Last Updated |
|----------|-------------|--------------|
| [Architecture Overview](architecture/overview.md) | Complete system architecture including components, communication patterns, deployment architecture, and data flow | 2026-01-10 |

**Topics Covered:**
- Component diagram and architecture layers
- Repository structure (main repo + future client repo)
- REST API communication patterns
- Deployment architecture (Docker Compose, Kubernetes, cloud platforms)
- Security architecture and audit logging
- Technology stack and scalability considerations
- Extension points for adding new clients and commands

---

## Deployment & Integration

Guides for deploying and integrating with the AI-Agent-Framework.

| Document | Description | Last Updated |
|----------|-------------|--------------|
| [Multi-Component Deployment Guide](deployment/multi-component-guide.md) | Complete deployment guide covering local development, Docker Compose, Kubernetes, and cloud platforms | 2026-01-10 |
| [Client Integration Guide](api/client-integration-guide.md) | API reference and examples for building custom clients in Python, JavaScript, and Go | 2026-01-10 |

**Deployment Topics:**
- Local development setup (with and without Docker)
- Production deployment options (Docker Compose, Kubernetes, cloud)
- Networking configuration and CORS
- Environment variables and secrets management
- Health checks, monitoring, logging
- Backup and recovery strategies

**Integration Topics:**
- Complete API endpoint reference with curl examples
- Authentication flow (current and future)
- Request/response formats and error handling
- Propose/apply workflow implementation
- Client implementation examples (Python, JavaScript, Go)
- Best practices and troubleshooting

---

## Specifications

Formal requirements and system specifications.

| Document | Description | Status |
|----------|-------------|--------|
| [MVP ISO 21500 Agent](spec/mvp-iso21500-agent.md) | Complete MVP specification including architecture, features, compliance, and technical details | ✅ Implemented |

**Topics Covered:**
- System architecture (FastAPI + React/Vite + Docker)
- Core features (propose/apply, LLM adapter, git storage)
- Compliance (EU AI Act, ISO 27001, GDPR)
- Deployment and configuration
- Future enhancements

---

## Architecture Decision Records (ADRs)

Key architectural decisions with context, rationale, and consequences.

| ADR | Title | Date | Status |
|-----|-------|------|--------|
| [ADR-0001](adr/0001-docs-repo-mounted-git.md) | Separate Project Documents Git Repository Mounted at /projectDocs | 2026-01-09 | ✅ Accepted |
| [ADR-0002](adr/0002-llm-http-adapter-json-config.md) | LLM HTTP Adapter Configured by JSON with LM Studio Defaults | 2026-01-09 | ✅ Accepted |
| [ADR-0003](adr/0003-propose-apply-before-commit.md) | Propose/Apply Workflow with Review-Before-Commit | 2026-01-09 | ✅ Accepted |
| [ADR-0004](adr/0004-separate-client-application.md) | Separate Client Application for API Consumption | 2026-01-09 | ✅ Accepted |

**ADR Topics:**
- Why separate git repository for project documents?
- Why HTTP adapter instead of LLM SDK?
- Why two-step propose/apply workflow?
- Why separate client application container?

**ADR Template:** [template.md](adr/template.md)

---

## Chat Transcripts

Verbatim conversations documenting design discussions and decision-making processes.

| Transcript | Topic | Date | Participants |
|------------|-------|------|--------------|
| [2026-01-09 Initial Development](chat/2026-01-09-blecx-copilot-transcript.md) | Complete system design and implementation | 2026-01-09 | blecx, GitHub Copilot |

**Transcript Topics:**
- Project requirements and architecture
- Propose/apply workflow design
- LLM integration strategy
- Separate git repository rationale
- Audit logging approach
- Template system design
- Docker configuration
- Security and compliance
- Testing strategy
- Documentation planning

**Transcript Template:** [TEMPLATE.md](chat/TEMPLATE.md) *(to be created)*

---

## Development Guides

Comprehensive guides for developing and maintaining the project.

| Guide | Description | Last Updated |
|-------|-------------|--------------|
| [Development Guide](development.md) | Complete local development guide including setup, workflow, testing, and troubleshooting | 2026-01-09 |

**Topics Covered:**
- Development environment setup with `.venv`
- Project structure and organization
- Running the application locally
- Development workflow and hot reload
- Adding dependencies (Python and JavaScript)
- Testing strategies
- Docker integration
- IDE configuration
- Troubleshooting common issues

---

## Client Documentation

Comprehensive guides for all available client interfaces and API integration.

| Guide | Description | Last Updated |
|-------|-------------|--------------|
| [Client Overview](clients/README.md) | Complete guide to all client interfaces, API reference, and building custom clients | 2026-01-09 |
| [TUI Client](../apps/tui/README.md) | Command-line interface for automation and scripting | 2026-01-09 |
| [Advanced Client](../client/README.md) | CLI + Interactive TUI with rich terminal features | 2026-01-09 |
| [WebUI Client](https://github.com/blecx/AI-Agent-Framework-Client) | Enhanced web interface (separate repository) | External |

**Topics Covered:**
- Available clients and comparison
- Client separation strategy
- When to use each client
- API endpoint reference
- Authentication guide (for future implementations)
- Building custom clients (step-by-step)
- Example implementations (Python, JavaScript/TypeScript)
- Best practices and troubleshooting

---

## How-To Guides

Step-by-step procedural guides for common tasks.

| Guide | Description | Last Updated |
|-------|-------------|--------------|
| [Chat Context Storage](howto/chat-context-in-repo.md) | Best practices for storing and restoring conversational context in repositories | 2026-01-09 |

**Topics Covered:**
- Why store chat context?
- Three-tier documentation strategy
- Folder structure and naming conventions
- What to store and what NOT to store
- Context restoration for humans and AI agents
- Linking strategy between documents
- Compliance guidance (EU AI Act, ISO 27001, GDPR)
- Templates and examples

---

## Cross-Reference Map

Find all documentation related to a specific feature or decision.

### Feature: Propose/Apply Workflow

**Overview:** Two-step workflow where users review AI-generated changes before committing to git.

**Documentation:**
- **Specification:** [MVP Spec - Propose/Apply Workflow](spec/mvp-iso21500-agent.md#3-proposeapply-workflow-review-before-commit)
- **Architecture Decision:** [ADR-0003: Propose/Apply Workflow](adr/0003-propose-apply-before-commit.md)
- **Discussion:** [Chat Transcript - Part 2](chat/2026-01-09-blecx-copilot-transcript.md#part-2-architecture-deep-dive)
- **Code Implementation:** 
  - `apps/api/services/command_service.py` - Propose/apply logic
  - `apps/api/routers/commands.py` - API endpoints
  - `apps/web/src/components/ProposalModal.jsx` - UI component

**Related PRs:** *(to be added as implemented)*

---

### Feature: LLM Integration

**Overview:** OpenAI-compatible HTTP adapter configured via JSON with graceful fallback to templates.

**Documentation:**
- **Specification:** [MVP Spec - LLM HTTP Adapter](spec/mvp-iso21500-agent.md#2-llm-http-adapter-with-json-configuration)
- **Architecture Decision:** [ADR-0002: LLM HTTP Adapter](adr/0002-llm-http-adapter-json-config.md)
- **Discussion:** [Chat Transcript - Part 2](chat/2026-01-09-blecx-copilot-transcript.md#part-2-architecture-deep-dive)
- **Configuration:** `configs/llm.default.json`
- **Code Implementation:**
  - `apps/api/services/llm_service.py` - LLM service
  - `templates/prompts/iso21500/` - Prompt templates
  - `templates/output/iso21500/` - Fallback templates

**Related PRs:** *(to be added as implemented)*

---

### Feature: Separate Project Documents Repository

**Overview:** Project documents stored in separate git repository mounted at /projectDocs, never committed to code repository.

**Documentation:**
- **Specification:** [MVP Spec - Project Documents Storage](spec/mvp-iso21500-agent.md#1-separate-project-documents-git-repository)
- **Architecture Decision:** [ADR-0001: Separate Docs Repository](adr/0001-docs-repo-mounted-git.md)
- **Discussion:** [Chat Transcript - Part 2](chat/2026-01-09-blecx-copilot-transcript.md#part-2-architecture-deep-dive)
- **Configuration:** 
  - `docker-compose.yml` - Volume mount configuration
  - `.gitignore` - Excludes projectDocs/
- **Code Implementation:**
  - `apps/api/services/git_manager.py` - Git operations

**Related PRs:** *(to be added as implemented)*

---

### Feature: Audit Logging

**Overview:** NDJSON audit logs storing hashes by default (privacy by design) with optional full content logging.

**Documentation:**
- **Specification:** [MVP Spec - Audit Logging](spec/mvp-iso21500-agent.md#5-audit-logging)
- **Compliance:** [ADR-0003 - Compliance Notes](adr/0003-propose-apply-before-commit.md#compliance-notes)
- **Discussion:** [Chat Transcript - Part 3](chat/2026-01-09-blecx-copilot-transcript.md#part-3-implementation-details)
- **Log Location:** `projectDocs/{PROJECT_KEY}/events/events.ndjson`
- **Code Implementation:** `apps/api/services/command_service.py`

**Related PRs:** *(to be added as implemented)*

---

### Feature: Docker Deployment

**Overview:** Two-container setup (FastAPI + React/Vite) orchestrated with Docker Compose.

**Documentation:**
- **Specification:** [MVP Spec - Docker Configuration](spec/mvp-iso21500-agent.md#docker-configuration)
- **Setup Guide:** [Quick Start - Docker](../QUICKSTART.md#4-start-the-services)
- **Discussion:** [Chat Transcript - Part 4](chat/2026-01-09-blecx-copilot-transcript.md#part-4-docker-and-deployment)
- **Configuration:**
  - `docker-compose.yml` - Orchestration
  - `docker/api/Dockerfile` - Backend image
  - `docker/web/Dockerfile` - Frontend image
  - `docker/web/nginx.conf` - Web server config

**Related PRs:** *(to be added as implemented)*

---

## Topic Index

Find documentation by topic.

### Architecture & Design
- [Architecture Overview](architecture/overview.md) - Complete system architecture
- [MVP Specification](spec/mvp-iso21500-agent.md)
- [ADR-0001: Separate Docs Repository](adr/0001-docs-repo-mounted-git.md)
- [ADR-0002: LLM HTTP Adapter](adr/0002-llm-http-adapter-json-config.md)
- [ADR-0003: Propose/Apply Workflow](adr/0003-propose-apply-before-commit.md)
- [ADR-0004: Client Separation Strategy](adr/0004-separate-client-application.md)

### Deployment & Operations
- [Multi-Component Deployment Guide](deployment/multi-component-guide.md)
- [Quick Start Guide](../QUICKSTART.md)
- [README - Setup](../README.md#setup)

### API & Integration
- [Client Integration Guide](api/client-integration-guide.md) - Build your own client
- [API Auto-Generated Docs](http://localhost:8000/docs) (when running)
- [Client README](../client/README.md) - Standalone CLI client

### Security & Compliance
- [MVP Spec - Security Section](spec/mvp-iso21500-agent.md#compliance--security)
- [ADR-0001 - Compliance Notes](adr/0001-docs-repo-mounted-git.md#compliance-notes)
- [ADR-0002 - Compliance Notes](adr/0002-llm-http-adapter-json-config.md#compliance-notes)
- [ADR-0003 - Compliance Notes](adr/0003-propose-apply-before-commit.md#compliance-notes)
- [How-To: Chat Context - Compliance](howto/chat-context-in-repo.md#compliance-guidance)

### Configuration & Setup
- [Deployment Guide - Environment Variables](deployment/multi-component-guide.md#environment-variables)
- [Deployment Guide - Secrets Management](deployment/multi-component-guide.md#secrets-management)
- [Quick Start Guide](../QUICKSTART.md)
- [README - Setup](../README.md#setup)
- [MVP Spec - LLM Configuration](spec/mvp-iso21500-agent.md#llm-configuration)
- [ADR-0002: LLM Configuration](adr/0002-llm-http-adapter-json-config.md)

### Development & Workflow
- [Development Guide](development.md)
- [README - Development](../README.md#development)
- [QUICKSTART - Local Development](../QUICKSTART.md#local-development-without-docker)
- [ADR-0003: Propose/Apply Workflow](adr/0003-propose-apply-before-commit.md)
- [Chat Transcript: Full Development Discussion](chat/2026-01-09-blecx-copilot-transcript.md)

### Documentation Best Practices
- [How-To: Chat Context Storage](howto/chat-context-in-repo.md)
- [ADR Template](adr/template.md) *(to be created)*

### ISO 21500 & Project Management
- [README - ISO 21500 Artifacts](../README.md#iso-21500-artifacts)
- [MVP Spec - ISO 21500 Commands](spec/mvp-iso21500-agent.md#6-iso-21500-commands)

---

## Document Templates

Standard templates for creating new documentation.

| Template | Purpose | Location |
|----------|---------|----------|
| ADR Template | Architecture Decision Records | [adr/template.md](adr/template.md) *(to be created)* |
| Chat Transcript Template | Development discussions | [chat/TEMPLATE.md](chat/TEMPLATE.md) *(to be created)* |
| Specification Template | Feature specifications | *(to be created)* |

---

## Contributing to Documentation

### When to Add Documentation

**Always Document:**
- New features or significant changes
- Architectural decisions
- Breaking changes
- Security considerations
- Compliance requirements

**Best Practices:**
- Update related documents when making changes
- Cross-reference between documents
- Keep formatting consistent
- Review for sensitive data before committing
- Update this index when adding new documents

### Documentation Guidelines

1. **Specifications:** Formal requirements and system design
2. **ADRs:** Architectural decisions with context and consequences
3. **Chat Transcripts:** Development discussions (redacted)
4. **How-Tos:** Step-by-step procedural guides

### Review Checklist

Before committing documentation:

- [ ] No secrets, API keys, or credentials
- [ ] No unredacted personal identifiable information
- [ ] Proper cross-references to related documents
- [ ] Clear section headers for navigation
- [ ] Dated and attributed properly
- [ ] Classification and retention noted
- [ ] Compliance considerations addressed
- [ ] Updated documentation index

See [How-To: Chat Context Storage](howto/chat-context-in-repo.md) for detailed guidance.

---

## External Resources

### Related Standards & Regulations
- [ISO 21500 - Project Management](https://www.iso.org/standard/50003.html)
- [EU AI Act](https://artificialintelligenceact.eu/)
- [ISO 27001 - Information Security](https://www.iso.org/standard/54534.html)
- [GDPR - Data Protection](https://gdpr-info.eu/)

### Technologies & Tools
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [LM Studio](https://lmstudio.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

### Development Resources
- [Architecture Decision Records](https://adr.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Git Documentation](https://git-scm.com/doc)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-09 | Initial documentation structure | GitHub Copilot |

---

## Feedback & Support

**Issues or Questions?**
- Check existing documentation first
- Review related ADRs for design rationale
- Consult chat transcripts for detailed discussions
- Open an issue on GitHub if needed

**Documentation Improvements:**
- Submit pull requests with documentation updates
- Reference this index for structure and formatting
- Follow templates for consistency

---

**Last Updated:** 2026-01-09  
**Maintained By:** Development Team  
**Classification:** Internal  
**Status:** Active
