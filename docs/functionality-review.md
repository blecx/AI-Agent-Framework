# Functional Architecture & Capability Review
**Context:** AI-Agent-Framework Core & APIs
**Date:** March 3, 2026
**Scope:** Capturing all system-level logic, backend architectural shifts, and technical debt cleanups separated from the visual Design UI review.

## Executive Summary
This document ensures no historical context or functional decisions are lost during the system transitions. Recently, the project underwent significant pruning of legacy operations (removing monolithic tutorials, test fixes, and Maestro framework decoupling). Moving forward, the backend and system logic must evolve strictly around the **ISO 21500 standard**, **Offline-First Git persistence**, **Multimodal Data Ingestion**, and **Agentic Auto-execution**.

---

## 1. System Decoupling & Documentation Strategy
**Functional Shift:** We have actively moved away from general "AI framework" scaffolding to a tightly scoped **ProjectBuilder** application targeting ISO 21500 project management.
*   **Maestro Tooling Extraction:** The core backend has been separated from generic autonomous agent logic (Maestro tooling). The host API is entirely focused on providing structured PM logic, while agent-specific tooling (`tests/tooling`, generic evaluation scripts) is isolated.
*   **Documentation Purge:** Legacy documentation (`gui-basics`, `tui-basics`, `advanced` examples, and old planner files) have been entirely deleted. The functional onboarding strategy must strictly be a **Unified ISO-21500 Tutorial Workflow**. Users only learn the project management path; generic framework tutorials are deprecated.

## 2. Offline-First & Decentralized Git Persistence Engine
**Functional Requirement:** The tool is designed for offline-first work using decentralized Git.
*   **Git as a Database:** The functional logic must handle local disconnected operations completely independently of network status. 
*   **Merge & Conflict Handling:** The backend API must gracefully expose `.git` states (untracked, modified, merge conflicts) via the API so the frontend can orchestrate syncs.
*   **Sync Logic:** Standard database CRUD operations must be mapped explicitly to Git Commits, ensuring a complete audit trail without a traditional SQL database.

## 3. ISO 21500 Readiness Gating & Measurement
**Functional Requirement:** A state-machine that actually calculates "Readiness."
*   **Compliance Engine:** The backend requires a dedicated engine or evaluator that weighs existing artifacts against strict ISO 21500 checkpoints (Setup, Planning, Execution, Closure gates).
*   **Metrics & Blockers:** The API must return quantitative scores (e.g., `85% Ready`) and dynamically calculate exact blocking conditions (e.g., "Missing Stakeholder Registry") instead of leaving validation strictly to human reading.

## 4. The Dual-Workflow State Machine (ProjectBuilder)
**Functional Requirement:** Handling multiple creation profiles.
*   **State Persistence:** The `ProjectBuilder` API must handle two completely distinct state-trees:
    1.  **Guided AI Route:** A fast-tracked configuration with highly opinionated template completions.
    2.  **Blank Canvas (Scratch) Route:** An unstructured, purely human-led setup.
*   **Draft Resumption:** Both workflows must functionally save partial state to local Git incrementally. If a user closes the app during a setup wizard, the system must reconstruct their exact position in the workflow upon restart.

## 5. Artifact Rich Media Ingestion & Storage
**Functional Requirement:** Extending artifacts beyond Markdown and JSON strings.
*   **Binary File Storage:** The API needs capabilities to intake multipart form data (Images, Flowchart outputs, Videos, PDFs) dragged entirely from the frontend.
*   **Git LFS or Asset Linking:** The system must structure how these rich assets are stored within the `projectDocs` repository and rendered back predictably in the Artifact Editor markdown blocks without bloat.

## 6. AI Agent Hooks & Multimodal Extensibility (Future)
**Functional Requirement:** Specific API and endpoint scaffolding to facilitate future AI pipelines.
*   **Autonomous Agent CRUD:** The API must expose secured endpoints ("Hooks") that allow designated AI Agents to create, evaluate, modify, and review artifacts *on behalf* of the human user.
*   **Muted Auto-Answers:** The backend must support streaming GenAI endpoints (SSE or WebSockets) for real-time artifact completion overlay inside the Client editor.
*   **Voice Capability:** The layout must prepare endpoints to accept binary Audio inputs (e.g., `POST /api/v1/voice-command`), convert them via offline/local models (or remote Whisper), and translate them into direct Project Commands or Markdown entries in an artifact.

---
**Next Immediate Action:** 
This functional review serves as the backend companion to `design-review.md`. The engineering team must ensure the API route structures support these operations (specifically the Git Offline syncing state and Media Upload logic) before the UX components in the `frontend` Phase 4 and 5 are merged.