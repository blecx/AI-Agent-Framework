# How-To Guide: Storing and Restoring Chat Context in Repository

**Last Updated:** 2026-01-09  
**Applies To:** AI-Agent-Framework and similar AI-assisted development projects  
**Audience:** Developers, Project Managers, AI Agents

---

## Overview

This guide explains best practices for storing conversational context (chat transcripts with AI assistants) in your code repository to enable context restoration for humans and AI agents while maintaining security and compliance.

## Table of Contents

1. [Why Store Chat Context?](#why-store-chat-context)
2. [Recommended Approach](#recommended-approach)
3. [Folder Structure](#folder-structure)
4. [What to Store](#what-to-store)
5. [What NOT to Store](#what-not-to-store)
6. [Context Restoration for Humans](#context-restoration-for-humans)
7. [Context Restoration for AI Agents](#context-restoration-for-ai-agents)
8. [Linking Strategy](#linking-strategy)
9. [Compliance Guidance](#compliance-guidance)
10. [Template and Examples](#template-and-examples)

---

## Why Store Chat Context?

**Benefits:**

1. **Knowledge Preservation:** Captures reasoning behind decisions that may not be obvious from code alone
2. **Team Continuity:** New team members understand design rationale and trade-offs
3. **AI Agent Assistance:** Enables context-aware AI assistance for future development
4. **Audit Trail:** Documents decision-making process for compliance
5. **Learning Resource:** Shows problem-solving approaches and best practices

**When to Store:**
- ✅ Architectural discussions
- ✅ Design decisions and trade-offs
- ✅ Requirement clarifications
- ✅ Implementation planning
- ✅ Problem-solving approaches

**When NOT to Store:**
- ❌ Debugging sessions with sensitive data
- ❌ Discussions containing secrets or credentials
- ❌ Personal conversations
- ❌ Information under NDA

---

## Recommended Approach

### Three-Tier Documentation Strategy

**Tier 1: Curated Specifications (Primary Source of Truth)**
- Extract key requirements into formal documents
- Structured, searchable, maintainable
- Location: `docs/spec/`
- Example: `docs/spec/mvp-iso21500-agent.md`

**Tier 2: Architecture Decision Records (Decision Context)**
- Document architectural decisions with context
- Follow ADR template (Context/Decision/Consequences)
- Location: `docs/adr/`
- Example: `docs/adr/0001-docs-repo-mounted-git.md`

**Tier 3: Full Chat Transcripts (Historical Appendix)**
- Store verbatim conversations (redacted)
- Provides complete context and reasoning trail
- Location: `docs/chat/`
- Example: `docs/chat/2026-01-09-blecx-copilot-transcript.md`

**Why This Works:**
- **Quick Reference:** Most users read specs and ADRs
- **Deep Dive:** Transcripts available for detailed research
- **Redundancy:** Key information in multiple formats
- **Flexibility:** Different levels of detail for different needs

---

## Folder Structure

```
project-root/
├── docs/
│   ├── README.md                           # Documentation index
│   ├── spec/                               # Formal specifications
│   │   ├── mvp-iso21500-agent.md
│   │   └── feature-requirements.md
│   ├── adr/                                # Architecture Decision Records
│   │   ├── README.md                       # ADR index
│   │   ├── 0001-decision-title.md
│   │   ├── 0002-decision-title.md
│   │   └── template.md                     # ADR template
│   ├── chat/                               # Chat transcripts
│   │   ├── README.md                       # Transcript index
│   │   ├── 2026-01-09-initial-design.md
│   │   └── 2026-01-15-feature-planning.md
│   └── howto/                              # How-to guides
│       ├── chat-context-in-repo.md         # This document
│       └── backup-restore.md
├── src/                                    # Source code
└── README.md                               # Project README
```

**Naming Conventions:**

**Specifications:**
- `{feature-name}.md`
- Example: `mvp-iso21500-agent.md`

**ADRs:**
- `{number}-{short-title}.md`
- Example: `0001-docs-repo-mounted-git.md`
- Number sequentially starting from 0001

**Chat Transcripts:**
- `{YYYY-MM-DD}-{topic-slug}.md`
- Example: `2026-01-09-blecx-copilot-transcript.md`
- Date indicates when conversation occurred

**How-To Guides:**
- `{topic-slug}.md`
- Example: `chat-context-in-repo.md`

---

## What to Store

### Curated Specifications

**Include:**
- Requirements and acceptance criteria
- System architecture overview
- Component descriptions
- API specifications
- Configuration details
- Deployment instructions
- Compliance requirements
- Future enhancements

**Format:**
```markdown
# [Feature Name] Specification

**Version:** 1.0.0
**Date:** YYYY-MM-DD
**Status:** Draft|Implemented|Deprecated

## Overview
[Brief description]

## Requirements
[Functional and non-functional requirements]

## Architecture
[System design and components]

## References
- [Related ADRs]
- [Chat transcripts]
```

### Architecture Decision Records (ADRs)

**Include:**
- Context: Why this decision was needed
- Decision: What was decided
- Alternatives: What else was considered
- Consequences: Trade-offs and implications
- Compliance notes: Regulatory considerations

**Format (Standard ADR Template):**
```markdown
# ADR-{NUMBER}: {Title}

**Date:** YYYY-MM-DD
**Status:** Proposed|Accepted|Deprecated|Superseded
**Deciders:** [Names or roles]
**Related:** [Links to specs, chats, PRs]

## Context
[Problem statement and background]

## Decision
[What was decided and implementation details]

## Consequences

### Positive
[Benefits and advantages]

### Negative
[Drawbacks and trade-offs]

### Risks and Mitigations
[Risk table]

## Alternatives Considered
[Other options and why they were rejected]

## Compliance Notes
[EU AI Act, ISO 27001, GDPR, etc.]

## References
[Links to related documentation]
```

### Chat Transcripts

**Include:**
- Date and participants
- Security notice (DO NOT COMMIT SECRETS)
- Full conversation (redacted for sensitive data)
- Section headers for navigation
- Cross-references to specs and ADRs
- Metadata (session info, outcomes)

**Format:**
```markdown
# Chat Transcript: [Title]

**Date:** YYYY-MM-DD
**Participants:** [Names or roles]
**Topic:** [Brief description]

---

## ⚠️ Security Notice
DO NOT COMMIT SECRETS, API KEYS, OR SENSITIVE DATA TO THIS TRANSCRIPT.
Review and redact any sensitive information before committing.

---

## Session Information
- Session Start: [timestamp]
- Session End: [timestamp]
- Outcomes: [bullet list]

---

## Conversation

### Part 1: [Section Title]

**User [HH:MM]:**
> Question or statement

**AI [HH:MM]:**
> Response

[Continue conversation...]

---

## Session Summary
[Key decisions, outcomes, next steps]

---

## Related Documentation
[Links to specs, ADRs, PRs]
```

---

## What NOT to Store

### Security Risks - NEVER Include:

❌ **Secrets and Credentials:**
- API keys
- Passwords
- Private tokens
- SSH keys
- Database connection strings
- Encryption keys

❌ **Personal Identifiable Information (PII):**
- Full names (use roles instead: "Developer", "PM")
- Email addresses
- Phone numbers
- Physical addresses
- User IDs
- IP addresses

❌ **Sensitive Business Information:**
- Proprietary algorithms (unless necessary)
- Customer data
- Financial information
- Information under NDA
- Competitive intelligence

❌ **Debugging Details:**
- Full stack traces with paths
- Environment-specific configurations
- Internal hostnames and IPs
- Detailed error messages with sensitive context

### Redaction Guidelines

**Before Committing:**
1. Search for patterns: `api_key`, `password`, `token`, `secret`
2. Replace names with roles: "User" → "Developer", "John" → "Team Lead"
3. Replace hostnames: `server-prod-123.internal` → `<production-server>`
4. Replace API keys: `sk-abc123...` → `<redacted-api-key>`
5. Remove customer names: "ACME Corp" → "Customer A"

**Redaction Example:**
```markdown
❌ BAD:
**User [10:00]:**
> The API key is sk-abc123xyz. Connect to api.acme.com using john@acme.com.

✅ GOOD:
**User [10:00]:**
> The API key is <redacted>. Connect to <api-endpoint> using <user-credentials>.
```

---

## Context Restoration for Humans

### How Humans Should Restore Context

**Step 1: Start with Documentation Index**
```bash
# Read the docs index
cat docs/README.md
```

**Step 2: Read Specifications**
```bash
# Understand what was built
cat docs/spec/mvp-iso21500-agent.md
```

**Step 3: Review Architecture Decisions**
```bash
# Understand why it was built this way
cat docs/adr/*.md
```

**Step 4: Scan Chat Transcripts (Optional)**
```bash
# For detailed reasoning or specific questions
cat docs/chat/2026-01-09-*.md
```

**Step 5: Cross-Reference with Code**
```bash
# See implementation
cat src/main.py
git log --oneline
```

### Timeline for Context Restoration

| Time Available | Recommended Reading |
|----------------|---------------------|
| 5 minutes | README.md + docs/README.md |
| 15 minutes | + docs/spec/*.md |
| 30 minutes | + docs/adr/*.md |
| 1 hour | + docs/chat/*.md (scan) |
| 2+ hours | + docs/chat/*.md (detailed) + code |

### Quick Reference Commands

```bash
# Find all documentation
find docs/ -name "*.md" -type f

# Search documentation for specific topic
grep -r "LLM integration" docs/

# List ADRs chronologically
ls -1 docs/adr/*.md

# View latest chat transcript
ls -t docs/chat/*.md | head -1 | xargs cat
```

---

## Context Restoration for AI Agents

### How AI Agents Should Use Context

**Context Loader Pattern:**

```python
class ContextLoader:
    """Loads project context for AI agent"""
    
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.context = {}
    
    def load_full_context(self) -> dict:
        """Load all documentation for context"""
        return {
            "specifications": self._load_specs(),
            "decisions": self._load_adrs(),
            "discussions": self._load_transcripts(),
            "howtos": self._load_howtos()
        }
    
    def _load_specs(self) -> List[dict]:
        """Load specification documents"""
        specs = []
        for spec_file in (self.docs_path / "spec").glob("*.md"):
            specs.append({
                "file": spec_file.name,
                "content": spec_file.read_text(),
                "type": "specification"
            })
        return specs
    
    def _load_adrs(self) -> List[dict]:
        """Load Architecture Decision Records"""
        adrs = []
        for adr_file in sorted((self.docs_path / "adr").glob("*.md")):
            adrs.append({
                "file": adr_file.name,
                "content": adr_file.read_text(),
                "type": "decision_record"
            })
        return adrs
    
    def _load_transcripts(self) -> List[dict]:
        """Load chat transcripts"""
        transcripts = []
        for transcript in (self.docs_path / "chat").glob("*.md"):
            transcripts.append({
                "file": transcript.name,
                "content": transcript.read_text(),
                "type": "discussion"
            })
        return transcripts
    
    def search_context(self, query: str) -> List[dict]:
        """Search all context for relevant information"""
        # Implementation: Use semantic search, keyword matching, etc.
        pass
```

**Usage by AI Agent:**

```python
# When AI agent starts working on project
context_loader = ContextLoader("docs/")
context = context_loader.load_full_context()

# AI agent now knows:
# - What was built (specs)
# - Why it was built that way (ADRs)
# - How decisions were made (transcripts)
# - How to do common tasks (howtos)

# When user asks a question
user_query = "Why did we choose a separate git repo for documents?"
relevant_context = context_loader.search_context(user_query)

# AI response includes context from ADR-0001
```

**Indexing Strategy:**

1. **Load Phase:**
   - Read all markdown files in docs/
   - Parse structure (headers, sections)
   - Extract metadata (dates, authors, status)

2. **Index Phase:**
   - Create keyword index
   - Build semantic embeddings (optional)
   - Map cross-references

3. **Query Phase:**
   - Search by keyword or semantic similarity
   - Return relevant sections
   - Include cross-referenced documents

**AI Agent Context Prompt:**

```
You are working on the AI-Agent-Framework project.

Project Context:
- MVP Specification: [content from docs/spec/mvp-iso21500-agent.md]
- Key Decisions:
  - ADR-0001: Separate git repo for documents
  - ADR-0002: LLM HTTP adapter with JSON config
  - ADR-0003: Propose/apply workflow
- Recent Discussions: [relevant sections from chat transcripts]

Use this context to inform your responses and code changes.
```

---

## Working with Multi-Repository Projects

When your project uses multiple repositories (e.g., API in one repo, WebUI client in another), managing context across repositories requires special attention.

### Cross-Repository Context Challenges

**Common Scenarios:**
1. **Separate Client Repositories**: WebUI client in different repo than API
2. **Microservices Architecture**: Different services in different repos
3. **Shared Libraries**: Common code in separate repo
4. **Documentation Sites**: Docs in separate repo from code

**Example: AI-Agent-Framework**
- **Core API**: `blecx/AI-Agent-Framework` (this repository)
- **WebUI Client**: `blecx/AI-Agent-Framework-Client` (separate repository)
- **Relationship**: Client consumes API via REST endpoints

### Documenting Cross-Repository Architecture

**In the Core Repository (API):**
```markdown
## Related Repositories

- **[AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)**: 
  WebUI client for interactive project management
  - **Relationship**: Consumes this API via REST endpoints
  - **Communication**: HTTP/REST (no shared code)
  - **Documentation**: See client repo for setup and usage

## Architecture

The system uses a multi-repository architecture:
- This repo contains the core API and TUI/CLI clients
- WebUI client is in a separate repository for independent deployment
- All clients communicate via REST API only
```

**In the Client Repository (WebUI):**
```markdown
## Core API Repository

This WebUI client requires the AI-Agent-Framework API:
- **API Repository**: [blecx/AI-Agent-Framework](https://github.com/blecx/AI-Agent-Framework)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Setup**: Follow the API setup guide first

## Configuration

Configure the API endpoint in your `.env` file:
\`\`\`env
VITE_API_BASE_URL=http://localhost:8000
\`\`\`
```

### Context Restoration Across Repositories

**For Humans:**

When working across multiple repos, follow this sequence:

1. **Start with the core/API repository**:
   ```bash
   # Read core architecture
   cat core-repo/README.md
   cat core-repo/docs/README.md
   cat core-repo/docs/adr/0004-separate-client-application.md
   ```

2. **Review the relationship documentation**:
   - Look for "Related Repositories" sections
   - Find architecture diagrams showing component relationships
   - Review ADRs about multi-repo decisions

3. **Switch to the client repository**:
   ```bash
   # Read client docs
   cat client-repo/README.md
   # Look for "Core API Repository" or "Backend Setup" sections
   ```

4. **Understand the integration points**:
   - API endpoints consumed by the client
   - Authentication/authorization mechanisms
   - Configuration requirements
   - Deployment dependencies

**For AI Agents:**

When AI agents work across multiple repositories, provide context from both:

```python
class MultiRepoContextLoader:
    """Load context from multiple related repositories"""
    
    def __init__(self, primary_repo: str, related_repos: List[str]):
        self.primary_repo = Path(primary_repo)
        self.related_repos = [Path(r) for r in related_repos]
    
    def load_cross_repo_context(self) -> dict:
        """Load context from all related repositories"""
        return {
            "primary": self._load_repo_context(self.primary_repo),
            "related": [
                self._load_repo_context(repo) 
                for repo in self.related_repos
            ],
            "relationships": self._extract_relationships()
        }
    
    def _extract_relationships(self) -> dict:
        """Extract cross-repository relationships"""
        # Look for "Related Repositories" sections in README
        # Parse architecture diagrams
        # Find references to other repos in ADRs
        # Identify API endpoints and integration points
        pass
```

**AI Agent Prompt with Cross-Repo Context:**

```
You are working on a multi-repository project:

Primary Repository: blecx/AI-Agent-Framework
- Purpose: Core API for project management
- Technology: FastAPI (Python)
- Documentation: [content from docs/]

Related Repository: blecx/AI-Agent-Framework-Client
- Purpose: WebUI client for interactive use
- Technology: React/Vite
- Relationship: Consumes primary repo's API via REST
- Documentation: [content from client repo README]

Key Integration Points:
- API Base URL: http://localhost:8000
- API Endpoints: /projects, /commands, /artifacts
- Authentication: [describe auth mechanism]
- No shared code - pure REST API communication

When making changes:
1. Consider impact on both repositories
2. Ensure API changes are backward compatible
3. Update documentation in both repos if needed
4. Test client after API changes
```

### Storing Cross-Repository Transcripts

**When to Store in Which Repository:**

**Store in Core/API Repository when:**
- Discussion is primarily about API design
- Changes affect the API contract
- Architectural decisions impact all clients
- Core business logic discussions

**Store in Client Repository when:**
- Discussion is primarily about UI/UX
- Changes are client-specific
- Only affects that particular client

**Store in Both (with cross-references) when:**
- Major architectural changes affecting both
- Integration points are being modified
- Breaking changes to API

**Cross-Repository Transcript Example:**

In Core API Repository (`docs/chat/2026-01-15-api-breaking-change.md`):
```markdown
# Chat Transcript: API Breaking Change Discussion

**Affected Repositories:**
- ✅ This repository (API)
- ⚠️ [AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client) - Requires updates

**Related Issues:**
- API: #123
- Client: blecx/AI-Agent-Framework-Client#45

**Migration Guide:**
See [API Breaking Changes Guide](../howto/api-v2-migration.md)
```

In Client Repository (`docs/chat/2026-01-15-client-api-update.md`):
```markdown
# Chat Transcript: Client Update for API v2

**Related API Changes:**
- API Repository: [blecx/AI-Agent-Framework](https://github.com/blecx/AI-Agent-Framework)
- API Chat: [2026-01-15-api-breaking-change.md](https://github.com/blecx/AI-Agent-Framework/blob/main/docs/chat/2026-01-15-api-breaking-change.md)
- API PR: blecx/AI-Agent-Framework#123

**Changes Required in This Client:**
[List client-specific changes]
```

### Best Practices for Multi-Repo Documentation

**1. Maintain Clear Links:**
- Always link to the other repository's documentation
- Use full GitHub URLs (not relative paths)
- Include repository name in links: `[AI-Agent-Framework](https://github.com/...)`

**2. Document the Relationship:**
- Explain why repositories are separate
- Describe communication mechanisms
- Show architecture diagrams with both repos

**3. Keep ADRs in Core Repository:**
- Store architectural decisions that affect multiple repos in the core/API repo
- Reference them from client repos

**4. Sync Breaking Changes:**
- Document breaking changes in both repos
- Link PRs across repositories
- Update integration tests

**5. Version Compatibility:**
- Document which client versions work with which API versions
- Maintain a compatibility matrix
- Tag releases in sync when needed

### Example: AI-Agent-Framework Multi-Repo Setup

**Core Repository Structure:**
```
AI-Agent-Framework/
├── README.md                        # Links to client repos
├── docs/
│   ├── README.md                    # Multi-repo architecture
│   ├── adr/
│   │   └── 0004-separate-client.md  # Why separate repos
│   └── howto/
│       └── client-integration.md    # How clients integrate
└── apps/api/                        # Core API code
```

**Client Repository Structure:**
```
AI-Agent-Framework-Client/
├── README.md                        # Links back to API repo
├── docs/
│   ├── setup.md                     # API setup prerequisites
│   └── api-integration.md           # How this client uses the API
└── src/                             # Client code
```

**Documentation Cross-References:**

API Repo → Client Repo:
- README mentions client in "Client Applications" section
- Links to client repo for WebUI setup
- ADR-0004 documents the separation decision

Client Repo → API Repo:
- README links to API repo for backend setup
- Configuration docs reference API endpoints
- Troubleshooting guide links to API docs

---

## Linking Strategy

### Cross-Reference Best Practices

**1. ADR → Other Documents:**
```markdown
**Related:** 
- [MVP Spec](../spec/mvp-iso21500-agent.md#section)
- [Chat Transcript](../chat/2026-01-09-transcript.md#part-2)
- [PR #42](https://github.com/user/repo/pull/42)
```

**2. Spec → ADRs:**
```markdown
## Architecture

The system uses a propose/apply workflow. 
See [ADR-0003](../adr/0003-propose-apply-before-commit.md) for rationale.
```

**3. Chat → Formal Docs:**
```markdown
**AI [10:00]:**
> We'll use separate git repositories for code and documents.
> *(Formalized in [ADR-0001](../adr/0001-docs-repo-mounted-git.md))*
```

**4. PR → Documentation:**
```markdown
## Pull Request: Implement Propose/Apply Workflow

Implements the two-step review workflow for AI-generated changes.

**References:**
- Spec: [MVP Section 3](../docs/spec/mvp-iso21500-agent.md#section-3)
- ADR: [ADR-0003](../docs/adr/0003-propose-apply-before-commit.md)
- Discussion: [Chat 2026-01-09](../docs/chat/2026-01-09-transcript.md#part-2)
```

**5. Git Commits → Docs:**
```
feat: add propose/apply workflow

Implements two-step review process for AI changes.
- Propose endpoint generates diffs
- Apply endpoint commits after review

Ref: ADR-0003, PR #42
```

### Documentation Index Template

Create `docs/README.md` as central hub:

```markdown
# Documentation Index

## Quick Links
- [Project README](../README.md)
- [Quick Start Guide](../QUICKSTART.md)

## Specifications
- [MVP Specification](spec/mvp-iso21500-agent.md)

## Architecture Decision Records
- [ADR-0001: Separate Docs Repository](adr/0001-docs-repo-mounted-git.md)
- [ADR-0002: LLM HTTP Adapter](adr/0002-llm-http-adapter-json-config.md)
- [ADR-0003: Propose/Apply Workflow](adr/0003-propose-apply-before-commit.md)

## Chat Transcripts
- [2026-01-09: Initial Development](chat/2026-01-09-blecx-copilot-transcript.md)

## How-To Guides
- [Chat Context Storage](howto/chat-context-in-repo.md)
- [Backup and Restore](howto/backup-restore.md)

## Cross-Reference Map

### Feature: Propose/Apply Workflow
- **Spec:** [Section 3](spec/mvp-iso21500-agent.md#section-3)
- **ADR:** [ADR-0003](adr/0003-propose-apply-before-commit.md)
- **Discussion:** [Chat Part 2](chat/2026-01-09-blecx-copilot-transcript.md#part-2)
- **PR:** [#42](https://github.com/user/repo/pull/42)
- **Code:** `src/services/command_service.py`

### Feature: LLM Integration
- **Spec:** [Section 2](spec/mvp-iso21500-agent.md#section-2)
- **ADR:** [ADR-0002](adr/0002-llm-http-adapter-json-config.md)
- **Discussion:** [Chat Part 3](chat/2026-01-09-blecx-copilot-transcript.md#part-3)
- **Config:** `configs/llm.default.json`
- **Code:** `src/services/llm_service.py`
```

---

## Compliance Guidance

### EU AI Act Compliance

**Article 12 - Record Keeping:**

✅ **What to Document:**
- Date and time of AI usage
- Purpose of AI usage (e.g., "design discussion")
- Decisions made with AI assistance
- Human oversight actions

✅ **How Transcripts Help:**
- Show human-AI interaction patterns
- Demonstrate human-in-the-loop decision-making
- Provide audit trail for AI usage
- Document oversight and review

**Article 13 - Transparency:**

✅ **What to Document:**
- When AI was used in development
- What AI contributed vs. human decisions
- Limitations of AI assistance
- Review and approval processes

**Article 14 - Human Oversight:**

✅ **What to Document:**
- Human review of AI suggestions
- Points where humans intervened
- Decisions to accept or reject AI output
- Rationale for final decisions

### ISO 27001 - Information Security

**A.18.1.3 - Protection of Records:**

**Document Classification:**
- **Public:** README, general how-tos
- **Internal:** Specs, ADRs, transcripts (redacted)
- **Confidential:** Transcripts with business details
- **Secret:** Never stored in repo

**Retention Policy:**
```markdown
| Document Type | Retention | Rationale |
|---------------|-----------|-----------|
| Specifications | Project lifetime + 7 years | Compliance |
| ADRs | Indefinite | Historical record |
| Chat Transcripts | Project lifetime | Context preservation |
| How-To Guides | Until superseded | Operational |
```

**Access Control:**
- Repository access controls apply
- Sensitive transcripts in private repos only
- Review permissions regularly

### GDPR - Data Protection

**Principle 1 - Lawfulness, Fairness, Transparency:**

✅ **Before Storing Transcripts:**
- Obtain consent if identifiable persons mentioned
- Explain how transcripts will be used
- Provide access to stored transcripts

**Principle 2 - Purpose Limitation:**

✅ **Store Only For:**
- Project development and maintenance
- Knowledge transfer to team members
- Compliance and audit requirements

❌ **NOT For:**
- Performance evaluation of individuals
- Marketing or promotional purposes
- Unrelated projects without consent

**Principle 3 - Data Minimization:**

✅ **Minimize Data:**
- Redact names (use roles instead)
- Remove email addresses
- Remove unnecessary personal details
- Focus on technical content

**Principle 5 - Storage Limitation:**

✅ **Retention:**
- Define retention period (e.g., project lifetime + 3 years)
- Document in policy
- Archive or delete old transcripts

**Article 17 - Right to Erasure:**

✅ **Be Prepared To:**
- Remove references to specific individuals
- Rewrite sections to anonymize
- Delete entire transcripts if required

### Practical Compliance Checklist

**Before Committing Any Transcript:**

- [ ] ⚠️ Security notice at the top
- [ ] ❌ No API keys, passwords, or secrets
- [ ] ❌ No unredacted email addresses
- [ ] ❌ No full names (use roles: "Developer", "PM")
- [ ] ❌ No customer names or identifiable business data
- [ ] ❌ No IP addresses or internal hostnames
- [ ] ✅ Dated with clear participants
- [ ] ✅ Purpose documented (why this conversation is stored)
- [ ] ✅ Cross-references to related documents
- [ ] ✅ Classification noted (Public/Internal/Confidential)
- [ ] ✅ Retention period documented

---

## Template and Examples

### Chat Transcript Template

Save as `docs/chat/TEMPLATE.md`:

```markdown
# Chat Transcript: [Brief Title]

**Date:** YYYY-MM-DD  
**Participants:** [Role1 (e.g., Developer), Role2 (e.g., AI Assistant)]  
**Topic:** [One-line description]  
**Classification:** [Public|Internal|Confidential]  
**Retention:** [Project lifetime|5 years|Indefinite]

---

## ⚠️ Security Notice

**DO NOT COMMIT SECRETS, API KEYS, CREDENTIALS, OR SENSITIVE PERSONAL DATA.**

Review and redact any sensitive information before committing to version control.

---

## Session Information

- **Session Start:** YYYY-MM-DD HH:MM:SS UTC
- **Session End:** YYYY-MM-DD HH:MM:SS UTC
- **Project:** [Project Name]
- **Repository:** [owner/repo]
- **Branch:** [branch-name]

---

## Conversation

### Part 1: [Section Title]

**[Role1] [HH:MM]:**
> [Message content]

**[Role2] [HH:MM]:**
> [Response content]

[Continue conversation...]

### Part 2: [Section Title]

[Continue organizing by topic...]

---

## Session Summary

**Duration:** [X hours]  

**Outcomes:**
- ✅ [Outcome 1]
- ✅ [Outcome 2]
- [ ] [Pending item]

**Key Decisions:**
1. [Decision 1] - See [ADR-000X]
2. [Decision 2] - See [ADR-000Y]

**Next Steps:**
- [ ] [Action item 1]
- [ ] [Action item 2]

---

## Document Metadata

**Transcript ID:** [unique-identifier]  
**Created:** YYYY-MM-DD HH:MM:SS UTC  
**Format:** Markdown  
**Classification:** [Public|Internal|Confidential]  
**Retention:** [Retention period]  
**Review Status:** [Redacted|Reviewed|Draft]

---

## Related Documentation

- [Specification Name](../spec/spec-name.md)
- [ADR-XXXX: Decision Title](../adr/XXXX-decision-title.md)
- [Related PR #XX](https://github.com/owner/repo/pull/XX)
```

### ADR Template

Save as `docs/adr/template.md`:

```markdown
# ADR-{NUMBER}: {Title}

**Date:** YYYY-MM-DD  
**Status:** Proposed|Accepted|Deprecated|Superseded  
**Deciders:** [Name or Role], [Name or Role]  
**Related:** [Links to specs, chats, PRs]

## Context

[Describe the problem or opportunity]

[Explain constraints and requirements]

[List options considered]

## Decision

[State the decision clearly]

[Explain implementation details]

## Consequences

### Positive
[List benefits and advantages]

### Negative
[List drawbacks and trade-offs]

### Risks and Mitigations
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
|      |        |             |            |

## Alternatives Considered

[List other options and why they were rejected]

## Compliance Notes

[EU AI Act, ISO 27001, GDPR, or other regulatory considerations]

## Implementation Notes

[Code examples, configuration details, etc.]

## References

[Links to related documentation, standards, discussions]

## Review History

| Date | Reviewer | Decision |
|------|----------|----------|
|      |          |          |

---

**Previous:** [ADR-XXXX: Previous Decision]  
**Next:** [ADR-XXXX: Next Decision]
```

---

## Maintenance and Updates

### Regular Review Schedule

**Monthly:**
- Review new transcripts for security issues
- Update cross-references if documents moved
- Archive obsolete discussions

**Quarterly:**
- Review retention compliance
- Update documentation index
- Check for broken links

**Yearly:**
- Comprehensive documentation audit
- Update compliance guidance
- Archive completed project docs

### When to Update Documentation

**Always Update When:**
- Significant architectural changes
- New compliance requirements
- Security vulnerabilities discovered
- Team changes (update redactions if names used)

**Update Process:**
1. Create new version with date
2. Update cross-references
3. Mark old version as superseded
4. Update documentation index

---

## Tools and Automation

### Useful Commands

**Find all documentation:**
```bash
find docs/ -name "*.md" | sort
```

**Check for potential secrets:**
```bash
grep -r -i "api.key\|password\|secret\|token" docs/
```

**Validate links:**
```bash
# Using markdown-link-check
markdown-link-check docs/**/*.md
```

**Generate documentation index:**
```bash
# Simple script to list all docs
for dir in docs/*/; do
  echo "## $(basename $dir)"
  find "$dir" -name "*.md" -exec basename {} \; | sort
done
```

### Automation Opportunities

**Pre-commit Hooks:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for secrets in docs/
if grep -r -i "sk-[a-zA-Z0-9]\{20,\}" docs/; then
  echo "Error: Potential API key found in docs/"
  exit 1
fi

# Check for email addresses
if grep -r -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" docs/; then
  echo "Warning: Email address found in docs/"
  echo "Please review and redact if needed."
fi
```

**CI/CD Checks:**
```yaml
# .github/workflows/docs-check.yml
name: Documentation Check

on: [pull_request]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for secrets
        run: |
          ! grep -r -i "api.key\|password\|secret" docs/
      - name: Validate links
        run: |
          npm install -g markdown-link-check
          find docs/ -name "*.md" -exec markdown-link-check {} \;
```

---

## Summary

**Key Takeaways:**

1. **Use Three-Tier Strategy:** Specs → ADRs → Transcripts
2. **Always Redact:** Remove secrets, PII, and sensitive data
3. **Cross-Reference:** Link documents for traceability
4. **Enable AI Context:** Structure for machine readability
5. **Comply with Regulations:** Follow EU AI Act, ISO 27001, GDPR
6. **Regular Reviews:** Audit documentation regularly
7. **Automate Checks:** Use pre-commit hooks and CI/CD

**Remember:**
- Documentation is for both humans and AI agents
- Security and compliance first
- Structure enables discoverability
- Context preservation increases project maintainability

---

## Further Reading

- [EU AI Act - Article 12 (Record Keeping)](https://artificialintelligenceact.eu/article/12/)
- [ISO 27001 Documentation Requirements](https://www.iso.org/standard/54534.html)
- [GDPR - Data Protection by Design](https://gdpr-info.eu/art-25-gdpr/)
- [Architecture Decision Records](https://adr.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Document Version:** 1.0  
**Last Reviewed:** 2026-01-09  
**Next Review:** 2026-04-09  
**Owner:** Development Team  
**Classification:** Internal
