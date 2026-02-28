# MCP Tool Arbitration Hard Rules

These rules resolve ambiguous situations where multiple MCP servers could solve
one task. They are hard rules for agent prompts and runtime behavior.

## Rule 1: Specialization wins

When tools overlap, choose the most specialized MCP server for the job.

## Rule 2: Repository state/history -> Git MCP

Use `git` MCP for:

- `status`, `diff`, `log`, `show`
- `blame`
- branch queries/operations

Do not use `filesystem` or generic shell paths for git-history reasoning.

## Rule 3: Code discovery -> Search MCP

Use `search` MCP first for codebase discovery and text matching.
Only use direct file reads when the target path is already known.

## Rule 4: File CRUD -> Filesystem MCP

Use `filesystem` MCP for deterministic file operations within workspace scope.
Do not use it for search-like exploration when `search` MCP can answer faster.

## Rule 5: Container lifecycle -> Docker/Compose MCP

Use `dockerCompose` MCP for stack up/down, logs, ps, and health checks.
Do not route container lifecycle work through generic shell tools first.

## Rule 6: Lint/build/test -> Test Runner MCP

Use `testRunner` MCP profiles for deterministic validation runs before any
fallback execution paths.

## Rule 7: Script orchestration -> Bash Gateway MCP

Use `bashGateway` MCP only when:

- the task is an allowlisted script workflow, or
- there is no dedicated MCP capability for that action.

## Rule 8: External docs grounding

Use Context7 when online for external APIs/frameworks.
When offline, use `offlineDocs` MCP first for indexed local docs.
Use `search` MCP only as fallback when required content is not indexed.

## Rule 9: Local docs Q&A -> Offline Docs MCP

For repository documentation Q&A and grounding (docs/tutorials/readmes/templates),
prefer `offlineDocs` MCP for index/search/read operations.
Use `filesystem` reads only for exact-path excerpts after the document is known.

Offline Docs index maintenance is change-driven: refresh after `docs/` or
`templates/` updates, not as a boot-time requirement.

## Rule 10: Tie-breaker

If uncertainty remains, enforce precedence by task class:

- Git/history/state: `git` > `bashGateway` > terminal
- Code discovery: `search` > `filesystem` read > terminal
- Local docs grounding/Q&A: `offlineDocs` > `search` > `filesystem` read
- File CRUD: `filesystem` > `bashGateway` > terminal
- Compose/containers: `dockerCompose` > `bashGateway` > terminal
- Lint/build/test: `testRunner` > `bashGateway` > terminal

No lower-tier tool may be chosen when a higher-tier, capable tool is available.
