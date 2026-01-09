# ADR-0004: Separate Client Application for API Consumption

**Date:** 2026-01-09  
**Status:** Accepted  
**Deciders:** blecx, GitHub Copilot  
**Related:** [MVP Spec](../spec/mvp-iso21500-agent.md), [Client README](../../client/README.md)

## Context

The AI-Agent-Framework provides a REST API for project management with ISO 21500 standards. We need to decide how to provide command-line access and demonstrate API usage patterns to users who want to:

1. **Automate workflows** without manual GUI interaction
2. **Integrate with CI/CD** pipelines and scripts
3. **Validate API completeness** by ensuring all functionality is available via REST
4. **Provide usage examples** for developers building their own clients
5. **Enable batch operations** across multiple projects
6. **Support headless environments** (servers, containers) without web UI

### Problem Statement

How should we provide command-line access to the AI Agent API, and should it be part of the main application or separate?

**Options Considered:**

**Option 1: Add CLI commands to the API server**
- ❌ Couples CLI with server code
- ❌ Increases API container size
- ❌ Makes it harder to demonstrate pure API consumption
- ❌ CLI dependencies pollute server environment
- ✅ Simple deployment (everything in one container)
- ✅ No network overhead

**Option 2: Create Python scripts in repo root**
- ❌ Not packaged or distributable
- ❌ No clear separation from application code
- ❌ Difficult to use independently
- ❌ No Docker packaging
- ✅ Easy to create and modify
- ✅ Low overhead

**Option 3: Separate client application in own Docker container**
- ✅ Clean separation of concerns
- ✅ Validates API-first architecture
- ✅ Demonstrates pure API consumption
- ✅ Can be used independently
- ✅ Easy to distribute and deploy
- ✅ Own dependencies and environment
- ✅ Optional component (doesn't affect core system)
- ⚪ Slightly more complex deployment
- ⚪ Network overhead (negligible in Docker network)

## Decision

We will implement **Option 3: Separate client application in own Docker container**.

### Implementation

1. **Client Structure:**
   ```
   client/
   ├── src/
   │   ├── __init__.py
   │   ├── __main__.py
   │   └── client.py        # Main CLI implementation
   ├── Dockerfile            # Separate Docker image
   ├── requirements.txt      # Client-specific dependencies
   ├── .env.example          # Configuration template
   └── README.md            # Client documentation
   ```

2. **Technology Stack:**
   - **Python 3.12** for consistency with API
   - **Click** for CLI framework (simple, well-documented)
   - **httpx** for HTTP client (modern, async-capable)
   - **python-dotenv** for environment configuration

3. **Docker Integration:**
   - Add `client` service to `docker-compose.yml`
   - Default command shows help
   - Run specific commands with: `docker compose run client <command>`
   - Uses Docker network to communicate with API

4. **API Coverage:**
   - All major API endpoints implemented
   - Projects: create, list, get state
   - Commands: propose, apply
   - Artifacts: list, get content
   - Health check and status

## Rationale

### Why Separate Container?

1. **API-First Validation:**
   - Proves all functionality is available via REST API
   - No hidden dependencies on internal code
   - Forces proper API design
   - Demonstrates best practices for API consumers

2. **Composability:**
   - Client can be used independently
   - Can connect to any API instance (local, remote, production)
   - Easy to distribute separately
   - Optional component that doesn't affect core system

3. **Separation of Concerns:**
   - Client code completely separate from server code
   - Different dependency trees
   - Can evolve independently
   - Clear boundaries and responsibilities

4. **Use Case Enablement:**
   - **Automation:** Scripts and batch operations
   - **CI/CD:** Integration in automated pipelines
   - **Testing:** API testing and validation
   - **Examples:** Reference implementation for other clients
   - **Education:** Shows how to consume the API

5. **User Choice:**
   - Web UI for interactive use
   - CLI for automation and scripting
   - Direct API for custom integrations
   - Users choose the interface that fits their workflow

### Why Not Include in API Container?

Including the CLI in the API container would:
- Pollute the API server with CLI dependencies
- Make it unclear what's server code vs client code
- Increase container size unnecessarily
- Couple two separate concerns
- Make it harder to demonstrate pure API usage
- Reduce flexibility in deployment

The small overhead of a separate container is worth the benefits of clean separation.

## Consequences

### Positive

1. **✅ Clean Architecture:**
   - Clear separation between API provider and consumer
   - Easy to understand and maintain
   - Good example for developers

2. **✅ API Validation:**
   - Ensures API completeness
   - Finds gaps in API design early
   - Forces good API practices

3. **✅ Flexibility:**
   - Use web UI or CLI as needed
   - Easy to add more clients (Go, JavaScript, etc.)
   - Can connect to different API instances

4. **✅ Automation Ready:**
   - Scripts and CI/CD integration
   - Batch operations
   - Headless environments

5. **✅ Documentation by Example:**
   - Shows how to consume the API
   - Reference implementation
   - Best practices demonstration

6. **✅ Optional Component:**
   - Not required for core functionality
   - Users can choose to use it or not
   - Doesn't add complexity to main system

### Negative

1. **⚠️ Deployment Complexity:**
   - One more container to manage
   - Slightly more complex docker-compose.yml
   - **Mitigation:** Container is optional, well-documented

2. **⚠️ Network Overhead:**
   - HTTP calls over Docker network instead of internal calls
   - **Mitigation:** Negligible in practice, Docker networks are fast

3. **⚠️ Maintenance:**
   - Two codebases to maintain (API + client)
   - Keep client in sync with API changes
   - **Mitigation:** API versioning, comprehensive tests, clear documentation

### Neutral

1. **⚪ Learning Curve:**
   - Users need to learn CLI commands
   - But provides more flexibility than GUI-only
   - Comprehensive help and documentation provided

## Alternatives Considered but Rejected

### Why Not Combined Container?

Combining API and client would:
- Violate single responsibility principle
- Make it unclear what's server vs client
- Pollute dependencies
- Reduce architectural clarity
- Miss opportunity to validate API-first design

### Why Not Multiple Programming Languages?

We considered clients in different languages (Go, JavaScript, etc.) but:
- Python keeps it consistent with the API
- Single language reduces maintenance burden
- Focus on functionality, not language diversity
- Other languages can be added later if needed

### Why Not Web UI Only?

Web UI alone would:
- Not support automation and scripting
- Not work in headless environments
- Not demonstrate API consumption patterns
- Limit use cases significantly
- Not enable CI/CD integration

## Use Cases

### Use CLI Client When:
- Automating project management tasks
- Integrating with CI/CD pipelines
- Batch processing multiple projects
- Working in headless environments
- Testing API functionality
- Scripting workflows

### Use Web UI When:
- Interactive project management
- Visual diff review
- Exploring and browsing artifacts
- Non-technical users
- Rich visual experience needed

### Use Direct API When:
- Building custom integrations
- Using different programming languages
- Advanced automation needs
- Embedding in other applications

## Compliance Notes

### EU AI Act
- **Transparency:** Clear separation shows which component does what
- **Documentation:** Separate README documents each component
- **Optional Use:** Users can choose their interface

### ISO 27001
- **Access Control:** Same authentication/authorization as web UI
- **Audit Trail:** All operations logged server-side
- **Separation of Duties:** Client consumes API, doesn't modify server

### GDPR
- **Data Minimization:** Client doesn't store data, only queries API
- **Privacy by Design:** No local caching of sensitive data
- **Transparency:** Clear documentation of data flows

## Future Considerations

1. **Authentication:** Add API key or OAuth support when needed
2. **Additional Clients:** Go, JavaScript, Rust implementations
3. **Interactive Mode:** REPL-style interactive client
4. **Configuration Profiles:** Support multiple API environments
5. **Output Formats:** JSON, YAML, table formats
6. **Shell Completion:** Bash/Zsh completion scripts
7. **Plugin System:** Allow custom commands

## References

- [Client README](../../client/README.md) - Detailed client documentation
- [Main README - Architecture](../../README.md#architecture) - Three-container architecture
- [QUICKSTART - Client Usage](../../QUICKSTART.md#6-optional-try-the-cli-client) - Getting started with client
- [API Documentation](http://localhost:8000/docs) - FastAPI auto-generated docs

## Related Decisions

- **ADR-0001:** Separate project documents repository - Same principle of separation
- **ADR-0002:** HTTP-based LLM adapter - API-first design philosophy
- **ADR-0003:** Propose/apply workflow - Used by both web UI and client

## Changes to This ADR

- **2026-01-09:** Initial version - Separate client application decision

---

**Classification:** Internal  
**Retention:** Indefinite (architectural decision)  
**Last Reviewed:** 2026-01-09
