# Tutorials

This tutorial set reflects the **current** command surface as of 2026-02-16.

## What is available today

### TUI command groups

- `projects`: `create`, `list`, `get`
- `commands`: `propose`, `apply`
- `artifacts`: `list`, `get`
- `config`
- `health`

### TUI propose choices

- `assess_gaps`
- `generate_artifact` (requires `--artifact-name` and `--artifact-type`)
- `generate_plan`

### Web UI

- Command cards: `assess_gaps`, `generate_artifact`, `generate_plan`
- Project tabs: **Commands** and **Artifacts**

### API (REST)

- RAID: `/projects/{project_key}/raid` and `/api/v1/projects/{project_key}/raid`
- Workflow state: `GET/PATCH /projects/{project_key}/workflow/state` and `/api/v1/projects/{project_key}/workflow/state`
- Allowed transitions: `/projects/{project_key}/workflow/allowed-transitions` and `/api/v1/projects/{project_key}/workflow/allowed-transitions`

## Start here

1. [Setup Guide](shared/00-setup-guide.md)
2. [TUI Quick Start](tui-basics/01-quick-start.md)
3. [GUI Commands and Proposals](gui-basics/03-commands-and-proposals.md)
4. [Documentation Quality Backlog](DOCUMENTATION-QUALITY-BACKLOG.md)

## Advanced API tutorials

1. [Templates API](advanced/04-templates-api.md)
2. [Blueprints API](advanced/05-blueprints-api.md)

## Visual learning assets (screenshots + diagrams)

- Guide: [Visual Learning Guide](visual-learning-guide.md)
- Screenshot script: `docs/tutorials/scripts/capture-workflow-screenshots.sh`
- Diagram export script: `docs/tutorials/scripts/export-drawio.sh`
- Combined generation script: `docs/tutorials/scripts/generate-visual-assets.sh`

Assets location:

- screenshots: `docs/tutorials/assets/screenshots/workflow/`
- diagram sources: `docs/tutorials/assets/diagrams/src/`
- diagram exports: `docs/tutorials/assets/diagrams/generated/`

## Notes

- Docker web UI URL: `http://localhost:8080`
- Local dev web UI URL: `http://localhost:5173`
- Legacy API routes remain, while `/api/v1/*` routes are available and preferred for new integrations.

---

**Last Updated:** 2026-02-16
