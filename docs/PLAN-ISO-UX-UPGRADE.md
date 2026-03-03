# Master Execution Plan: ISO 21500 UX Upgrade & Functional Unification
**Date**: March 3, 2026
**Objective**: Combine the findings of `design-review.md` and `functionality-review.md` into a sequential development roadmap. Ensure backend functionality is explicitly delivered prior to frontend UI changes, guaranteeing zero regressions and functional continuity.

## Core Directives
1. **Pacing Rules**: When spanning Full-Stack implementations, the Backend Engine/API (BE) Issue must be merged and tested *before* the Client UI (UX) implementation begins. 
2. **Domain-Driven**: Follow the Domain-Driven Design (DDD) guidelines inside `.github/copilot-instructions.md`.
3. **No Legacy Bloat**: Maintain strict focus on the offline-first, Git-synced, ISO-21500 PM workflows.

---

## Phase 1: Foundational Architecture & UI Primitives
*This phase is strictly Client-Side (UX) because it lays the necessary design tokens before we rebuild complex components.*

**Issue 1: Tailwind Infrastructure Setup (UX)**
*   **Goal**: Install Tailwind CSS, PostCSS, and Autoprefixer within the `../AI-Agent-Framework-Client/` application.
*   **Tasks**: 
    *   Initialize `tailwind.config.js` mapping design system tokens (colors, variables).
    *   Adjust `index.css` / `App.css` to import tailwind directives.
    *   Verify Dev server compiles without warnings. 

**Issue 2: Component Directory Reconstruction & Base Primitives (UX)**
*   **Goal**: De-flatten `client/src/components` and strip `.css` files.
*   **Tasks**:
    *   Create `src/components/ui/` and build standard headless primitives using Tailwind (Button, Input, Card).
    *   Reorganize domains into `src/features/` (e.g., `artifacts`, `builder`, `raid`).
    *   Delete the 30+ native `.css` files and convert classes mapping layout logic strictly to standard Tailwind tags.

---

## Phase 2: Offline-First Git Engine
*Ensuring the UI has a real-time understanding of the disconnected Git database state.*

**Issue 3: Git Sync State API (BE)**
*   **Goal**: Expose the hidden `.git` state of `projectDocs` to the frontend.
*   **Tasks**: 
    *   Create endpoint `GET /api/v1/sync/state` returning unsynced commits, untracked changes, and merge conflicts.
    *   Update `GitManager` service to map all standard CRUD operations definitively to `git commit` triggers.

**Issue 4: Global Header Sync Indicator (UX)**
*   **Goal**: The user must know if they are Offline, Synced, or Unsynced.
*   **Tasks**: 
    *   Update `AppNavigation/Header` to include a dynamic Sync indicator consuming the new API.
    *   Centralize `SyncPanel` and `ConflictResolver` into a Slide-Out drawer accessible globally from the header.

---

## Phase 3: ISO 21500 Readiness Gating Engine
*Transitioning project progress from manual interpretation to programmatic certainty.*

**Issue 5: Readiness Calculation API (BE)**
*   **Goal**: Create a backend evaluation engine that grades a project's compliance against ISO 21500 gates.
*   **Tasks**:
    *   Build `ReadinessEngine` checking artifact presence and completeness ratios.
    *   Create endpoint `GET /api/v1/projects/{id}/readiness` returning quantitative scores (e.g., `Setup: 90%`) and blocking factors.

**Issue 6: Readiness Dashboard UI (UX)**
*   **Goal**: Turn "Readiness" into the hero focus of the Project View.
*   **Tasks**:
    *   Transform the tabular `ReadinessBuilder.tsx` into a Dashboard with circular progress rings and barrier checklists using Tailwind/Recharts.
    *   Prominently float the ISO Compliance % on the main Project lists.

---

## Phase 4: Dual-Workflow Builder Integration
*Branching the creation wizard definitively.*

**Issue 7: Persistent Project Builder State Cache (BE)**
*   **Goal**: Allow users to close the app mid-wizard and resume flawlessly.
*   **Tasks**:
    *   Introduce temporary state caching (via local JSON/Git staging) for un-finalized project structures (`Draft` object).
    *   Return distinct schemas: Guided vs Scratch workflows.

**Issue 8: Branching Project Stepper (UX)**
*   **Goal**: Visually communicate the timeline.
*   **Tasks**:
    *   Refactor `GuidedBuilder.tsx` to structurally branch tracks.
    *   Implement a sidebar generic Stepper showing linear progress which re-hydrates based on the API draft state from Issue 7.

---

## Phase 5: Rich Media & Artifact Editor Enhancement
*Expanding artifact payloads beyond raw strings.*

**Issue 9: Binary Asset Upload Routing (BE)**
*   **Goal**: Facilitate media handling mimicking Git LFS behavior in `projectDocs`.
*   **Tasks**:
    *   Build `POST /api/v1/artifacts/{id}/media` to intake multipart forms.
    *   Return deterministic relative image links referencing local `projectDocs` media folder.

**Issue 10: Drag-and-Drop Artifact Workspace (UX)**
*   **Goal**: Build a modern workspace editor.
*   **Tasks**:
    *   Wrap `ArtifactEditor.tsx` in a `react-dropzone` wrapper pointing to the Issue 9 API.
    *   Add a "Full-Screen Focus" toggle button leveraging fixed Tailwind positioning.

---

## Phase 6: AI / Voice Hooks (Scaffolding)
*Future-proofing the client structure natively.*

**Issue 11: Multimodal Ingestion APIs (BE)**
*   **Goal**: Provide endpoints ready for agent workflows.
*   **Tasks**:
    *   Implement `/api/v1/agents/execute` generic wrapper for background logic.
    *   Implement `/api/v1/voice/transcribe` mock/handler for future Whisper hookups.

**Issue 12: Generative Overlay Scaffold (UX)**
*   **Goal**: Render UI areas for AI assistance.
*   **Tasks**:
    *   Add dormant Microphone toggles on wide text inputs.
    *   Reserve fixed-positioned `div` layers for streaming auto-answer completion ghost-text.