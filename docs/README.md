# Documentation Index

**AI-Agent-Framework Documentation Hub**

Welcome to the comprehensive documentation for the ISO 21500 Project Management AI Agent system. This index provides quick access to all project documentation organized by type and topic.

---

## Multi-Repository Architecture

The AI-Agent-Framework is designed with a multi-repository architecture to enable independent development and deployment of clients:

### Core Repository (this repository)
- **API Server**: FastAPI backend providing REST endpoints for all project management operations
- **TUI/CLI Client**: Python-based text interface for automation and scripting
- **Documentation**: Complete system documentation, ADRs, and specifications

### Client Repositories

**[AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)** - WebUI (Graphical Interface)
- React/Vite-based web application
- Modern graphical interface for interactive project management
- Visual diff viewer and artifact browser
- Deployed independently from the API
- Connects to the API via REST endpoints

### Why Separate Repositories?

**Benefits:**
1. **Independent Deployment**: Deploy and update clients without touching the API
2. **Technology Flexibility**: Different clients can use different tech stacks
3. **API-First Design**: Ensures all functionality is available via REST API
4. **Team Independence**: Frontend and backend teams can work independently
5. **Multiple Clients**: Enables different clients for different use cases (WebUI for interactive use, TUI/CLI for automation)
6. **Clear Boundaries**: Separation of concerns between API and presentation layers

**Relationship Between Components:**
- **API** (this repo): Core business logic, data storage, LLM integration
- **WebUI** (separate repo): Visual, interactive client for end users
- **TUI/CLI** (this repo): Text-based client for automation and DevOps workflows
- **projectDocs/**: Separate git repository for project documents (managed by API)

**Communication:**
All clients communicate with the API exclusively via REST endpoints. This ensures:
- Consistency across clients
- Validation that all functionality is API-accessible
- Easy integration of custom clients
- Simplified testing and API documentation

**Future Architecture:**
See [ADR-0004: Separate Client Application](adr/0004-separate-client-application.md) for detailed rationale and future considerations.

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
- 🌐 [WebUI Client](https://github.com/blecx/AI-Agent-Framework-Client) - Graphical interface (separate repo)
- 🔧 [TUI/CLI Client Documentation](../client/README.md) - Text-based automation client
- 🏗️ [Architecture Decisions](adr/)
- 💬 [Development Discussions](chat/)
- 📝 [How-To Guides](howto/)

---

## System Architecture

The AI Agent Framework uses a multi-repository architecture with separate client applications:

### Component Overview

| Component | Purpose | Location | Required |
|-----------|---------|----------|----------|
| **API** | FastAPI backend - Core logic and REST endpoints | This repo - Port 8000 | ✅ Yes |
| **WebUI** | React/Vite frontend - Graphical interface | [Separate repo](https://github.com/blecx/AI-Agent-Framework-Client) | ⚪ Optional |
| **TUI/CLI** | Python text client - Automation tool | This repo - `client/` | ⚪ Optional |
| **projectDocs/** | Git repository for project documents | Auto-created by API | ✅ Yes (auto) |

### Architecture Diagram

```
┌────────────────────────┐
│  WebUI (React/Vite)    │  ← Visual Interface (Separate Repository)
│  AI-Agent-Framework-   │     Interactive Management
│  Client Repository     │
└──────────┬─────────────┘
           │
           │  HTTP/REST
           │
           ▼
┌─────────────────┐         ┌──────────────────┐
│   API Server    │◄────────│  TUI/CLI Client  │  ← Text Interface (Automation)
│    FastAPI      │         │  (This repo)     │     Scripting & CI/CD
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

**WebUI Client (Separate Repository)**
- **Repository**: [AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)
- **Technology**: React/Vite with modern JavaScript
- **Purpose**: Interactive visual interface for end users
- **Deployment**: Independent from API (can be hosted separately)
- **Communication**: REST API only (no shared code)
- **Best for**: Team collaboration, visual project management

**TUI/CLI Client (This Repository)**
- **Location**: `client/` and `apps/tui/` directories
- **Technology**: Python with Click and Textual frameworks
- **Purpose**: Automation, scripting, CI/CD integration
- **Deployment**: Docker container or local Python
- **Communication**: REST API only (no shared code)
- **Best for**: DevOps workflows, automation pipelines

**Key Design Principles:**
- **API-First**: All clients use REST API exclusively
- **No Shared Code**: Clients are completely independent
- **Validates API Completeness**: Ensures all functionality is API-accessible
- **Multiple Options**: Users choose the interface that fits their workflow

#### When to Use Each Interface

**Use WebUI (Graphical Interface) when:**
- Interactive project management needed
- Visual diff review and proposal preview
- Browsing and exploring artifacts
- Non-technical users or team collaboration
- Rich visual experience desired
- **Setup**: [AI-Agent-Framework-Client repository](https://github.com/blecx/AI-Agent-Framework-Client)

**Use TUI/CLI Client when:**
- Automation and scripting needed
- CI/CD pipeline integration
- Batch processing multiple projects
- Command-line workflows
- API testing and validation
- Headless/server environments (no GUI available)
- **Setup**: Included in this repository - see [client/README.md](../client/README.md)

**Use Direct API when:**
- Custom integrations required
- Building your own client
- Language-specific implementations
- Advanced automation needs
- **Documentation**: http://localhost:8000/docs

For detailed client documentation:
- WebUI: [AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)
- TUI/CLI: [client/README.md](../client/README.md)

---

## Documentation Structure

```
docs/
├── README.md                          # This file
├── development.md                     # Local development guide
├── spec/                              # Formal specifications
├── adr/                               # Architecture Decision Records
├── chat/                              # Development transcripts
└── howto/                             # Procedural guides
```

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
- [MVP Specification](spec/mvp-iso21500-agent.md)
- [ADR-0001: Separate Docs Repository](adr/0001-docs-repo-mounted-git.md)
- [ADR-0002: LLM HTTP Adapter](adr/0002-llm-http-adapter-json-config.md)
- [ADR-0003: Propose/Apply Workflow](adr/0003-propose-apply-before-commit.md)

### Security & Compliance
- [MVP Spec - Security Section](spec/mvp-iso21500-agent.md#compliance--security)
- [ADR-0001 - Compliance Notes](adr/0001-docs-repo-mounted-git.md#compliance-notes)
- [ADR-0002 - Compliance Notes](adr/0002-llm-http-adapter-json-config.md#compliance-notes)
- [ADR-0003 - Compliance Notes](adr/0003-propose-apply-before-commit.md#compliance-notes)
- [How-To: Chat Context - Compliance](howto/chat-context-in-repo.md#compliance-guidance)

### Configuration & Setup
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
