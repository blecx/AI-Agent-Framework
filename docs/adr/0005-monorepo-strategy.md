# ADR-0005: Monorepo Strategy for All Client Interfaces

**Date:** 2026-01-10  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [ADR-0004](0004-separate-client-application.md), [Architecture Overview](../architecture/overview.md)

## Context

The AI-Agent-Framework provides multiple client interfaces:
- **API** (`apps/api/`) - FastAPI backend with business logic
- **TUI** (`apps/tui/`) - Command-line interface for automation
- **WebUI** (`apps/web/`) - React-based web interface for interactive use

We need to decide whether to keep all components in a single repository (monorepo) or split them into separate repositories.

### Problem Statement

Should the TUI and WebUI clients be maintained in the same repository as the API, or should they be split into separate repositories for independent development and release cycles?

**Specific Considerations:**
1. **Development workflow:** How often do changes require updates across multiple components?
2. **Release coordination:** Do clients and API need synchronized releases?
3. **Team structure:** Are different teams responsible for different components?
4. **Code sharing:** Is there shared code between components?
5. **Testing:** How are integration tests performed?
6. **Deployment:** How are components deployed (together vs separately)?

## Options Considered

### Option 1: Monorepo (Current - All in `blecx/AI-Agent-Framework`)

**Structure:**
```
blecx/AI-Agent-Framework/
├── apps/
│   ├── api/       # FastAPI backend
│   ├── tui/       # Python CLI client
│   └── web/       # React web client
├── docs/          # Shared documentation
├── templates/     # Shared templates
└── docker-compose.yml  # Orchestration
```

**Advantages:**
- ✅ **Atomic changes:** Update API and clients in a single commit
- ✅ **Simplified testing:** Integration tests work across all components
- ✅ **Easy coordination:** API changes immediately visible to client developers
- ✅ **Shared resources:** Templates, configs, docs in one place
- ✅ **Single clone:** Developers get everything with one `git clone`
- ✅ **Consistent versioning:** One version number for the entire system
- ✅ **Easier onboarding:** New developers see the full system structure

**Disadvantages:**
- ⚠️ **Larger repository:** More files to clone and manage
- ⚠️ **Coupled releases:** Breaking API changes require coordinated client updates
- ⚠️ **Mixed technologies:** Python, JavaScript, Docker all in one repo
- ⚠️ **Access control:** Cannot grant repo access to only frontend or backend team

---

### Option 2: Split Repositories with WebUI Separate

**Structure:**
```
blecx/AI-Agent-Framework/          # Main repo
├── apps/
│   ├── api/       # FastAPI backend
│   └── tui/       # Python CLI (stays with API)
└── ...

blecx/AI-Agent-Framework-Client/   # Separate repo
├── src/           # React application
├── public/
└── ...
```

**Advantages:**
- ✅ **Independent frontend releases:** Deploy WebUI without backend changes
- ✅ **Technology separation:** Frontend team works in JS-only repo
- ✅ **Smaller repos:** Each repo is more focused
- ✅ **Different release cycles:** Web UI can iterate faster

**Disadvantages:**
- ❌ **Synchronization overhead:** API changes require PRs in two repos
- ❌ **API version management:** Clients must specify compatible API versions
- ❌ **Testing complexity:** Integration tests span multiple repositories
- ❌ **Documentation split:** Architecture docs split across repos
- ❌ **Local development:** Requires cloning multiple repos
- ❌ **Coordination burden:** Breaking changes need careful coordination

---

### Option 3: All Clients in Separate Repos

**Structure:**
```
blecx/AI-Agent-Framework/          # API only
blecx/AI-Agent-Framework-TUI/      # TUI client
blecx/AI-Agent-Framework-Client/   # Web client
```

**Advantages:**
- ✅ **Maximum separation:** Each component completely independent
- ✅ **Technology-specific repos:** Each repo has only one tech stack
- ✅ **Independent releases:** All components release independently

**Disadvantages:**
- ❌ **High coordination cost:** Changes require multiple PRs
- ❌ **Complex testing:** Integration tests very difficult
- ❌ **Scattered documentation:** Docs split across three repos
- ❌ **Developer overhead:** Clone and manage three repos
- ❌ **Version matrix:** Complex compatibility matrix between components

---

## Decision

**We will use Option 1: Monorepo** - Keep all components (API, TUI, WebUI) in the same repository `blecx/AI-Agent-Framework`.

### Rationale

1. **Tight Integration:** The API, TUI, and WebUI are tightly integrated. API changes often require immediate client updates. Keeping them together ensures consistency.

2. **Development Velocity:** Most changes touch both API and clients. A monorepo enables atomic commits that update all affected components, avoiding the "update repo A, wait for CI, then update repo B" workflow.

3. **Testing Simplicity:** Integration tests can easily test API + TUI + WebUI together without complex multi-repo CI configuration.

4. **Shared Resources:** Templates (`templates/`), documentation (`docs/`), and Docker configuration (`docker-compose.yml`) are naturally shared across all components.

5. **Team Size:** For a small to medium-sized team, the coordination overhead of multiple repos outweighs the benefits of separation.

6. **Technology Diversity is Manageable:** While the repo contains Python and JavaScript, the clear `apps/` directory structure provides natural boundaries.

7. **Docker Isolation:** Each component has its own Dockerfile and can be built/deployed independently even within a monorepo.

8. **Consistent Versioning:** The entire system has a single version number, simplifying compatibility communication.

### Implementation

**Directory Structure:**
```
AI-Agent-Framework/
├── apps/
│   ├── api/              # Python FastAPI backend
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── ...
│   ├── tui/              # Python CLI client
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── ...
│   └── web/              # React web client
│       ├── src/
│       ├── package.json
│       └── ...
├── docker/               # Dockerfiles for each component
│   ├── api/
│   ├── web/
│   └── Dockerfile.tui
├── templates/            # Shared Jinja2 templates
├── configs/              # Shared configuration files
├── docs/                 # Comprehensive documentation
│   ├── architecture/
│   ├── deployment/
│   └── api/
└── docker-compose.yml    # Multi-container orchestration
```

**Build Independence:**
Each component can still be built and deployed independently:
```bash
# Build only API
docker build -f docker/api/Dockerfile apps/api -t iso21500-api

# Build only Web
docker build -f docker/web/Dockerfile . -t iso21500-web

# Build only TUI
docker build -f docker/Dockerfile.tui . -t iso21500-tui
```

**Deployment Flexibility:**
Components can be deployed separately even though they're in the same repo:
```bash
# Deploy only API
docker compose up api

# Deploy API + Web (no TUI)
docker compose up api web

# Deploy all components
docker compose up
```

## Consequences

### Positive

1. **✅ Faster Development:**
   - Atomic commits across API and clients
   - No waiting for CI in multiple repos
   - Easier to maintain consistency

2. **✅ Simpler Testing:**
   - Integration tests in one place
   - Single CI/CD pipeline
   - Easy to test full workflows

3. **✅ Better Documentation:**
   - All architecture docs in one place
   - Single source of truth
   - Cross-references work naturally

4. **✅ Easier Onboarding:**
   - New developers clone once
   - See full system architecture
   - Understand dependencies immediately

5. **✅ Shared Tooling:**
   - Common linting/formatting configs
   - Shared scripts and utilities
   - Single issue tracker

### Negative

1. **⚠️ Repository Size:**
   - Larger repo to clone (~190MB currently)
   - More files in working directory
   - **Mitigation:** Still manageable size, Git handles it efficiently

2. **⚠️ Technology Mixing:**
   - Python and JavaScript in same repo
   - Different build tools (pip, npm)
   - **Mitigation:** Clear directory structure separates concerns

3. **⚠️ CI/CD Complexity:**
   - Single pipeline must handle multiple tech stacks
   - Need conditional builds (only build changed components)
   - **Mitigation:** Use path filters in CI config

4. **⚠️ Access Control:**
   - Cannot grant frontend-only access
   - All contributors see all code
   - **Mitigation:** For this project, full visibility is acceptable

### Neutral

1. **⚪ Coupled Releases:**
   - All components released together
   - Version numbers stay in sync
   - Can be seen as pro or con depending on perspective

## Alternatives Considered but Rejected

### Why Not Separate WebUI Repository?

Separating only the WebUI while keeping TUI with the API would create inconsistency. If separation is needed, it should be all-or-nothing. The overhead of managing two repos for three components is the worst of both worlds.

### Why Not Three Separate Repos?

Maximum separation sounds appealing but:
- The integration is too tight - most changes affect multiple components
- Testing becomes extremely difficult
- Documentation becomes scattered
- Development velocity drops significantly
- The coordination overhead is not justified for this project size

### Why Not Microservices with Separate Repos?

While microservices often use separate repos, this project doesn't need that level of independence. The API, TUI, and WebUI are not independent services - they're different interfaces to the same underlying system.

## Migration Path

If the project grows significantly, migration to separate repos is possible:

1. **Extract WebUI First:** Most likely candidate for extraction due to different tech stack
2. **Use Git Subtree or Filter-Branch:** Preserve commit history
3. **Establish API Versioning:** Implement semantic versioning with stability guarantees
4. **Create Integration Tests in Separate Repo:** Cross-repo integration testing
5. **Automate Cross-Repo Updates:** Bots to create PRs when API changes

**Trigger Points for Migration:**
- Team grows beyond 10-15 developers
- Frontend and backend teams become fully independent
- Need for very different release cycles (e.g., daily frontend vs monthly backend)
- Repository size becomes unwieldy (>1GB)

## Compliance Notes

### ISO 27001 (Information Security)
- **Access Control:** All developers with repo access can see all components
- **Change Management:** Single version control system for all changes
- **Audit Trail:** Git history captures all changes across components

### GDPR (Data Protection)
- **Data Minimization:** No personal data in repository
- **Privacy by Design:** Separation strategy doesn't affect data handling

### EU AI Act
- **Transparency:** Monorepo makes it easy to see how all components interact
- **Documentation:** Comprehensive docs in one place

## Related Decisions

- **ADR-0004:** Separate client application (container level, not repo level)
- **ADR-0001:** Separate project documents repository (different concern - data vs code)

## References

- [Monorepo vs Polyrepo Debate](https://earthly.dev/blog/monorepo-vs-polyrepo/)
- [Google's Monorepo Experience](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext)
- [Architecture Overview](../architecture/overview.md)
- [Deployment Guide](../deployment/README.md)

## Future Considerations

1. **Monorepo Tools:** If repo grows, consider tools like Nx, Turborepo, or Lerna
2. **Partial Clones:** Git supports sparse checkouts for cloning only specific directories
3. **Code Ownership:** Use CODEOWNERS file to define component ownership
4. **CI Optimization:** Implement path-based triggers to only build changed components

## Changes to This ADR

- **2026-01-10:** Initial version - Monorepo strategy decision

---

**Classification:** Internal  
**Retention:** Indefinite (architectural decision)  
**Last Reviewed:** 2026-01-10
