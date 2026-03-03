# Architecture & UX Design Review: AI-Agent-Framework-Client
**Target Context:** AI-Agent-Framework-Client (`client/src/components`)
**Date:** March 3, 2026
**Framework Context:** React, Vite, Offline-First (Git), ISO 21500 Compliance

## Executive Summary
This document serves as the foundational blueprint for restructuring the frontend UX/UI. The primary decision is to completely switch the styling architecture to the **Tailwind UI system**, stripping away the legacy `.css` files. 

However, beyond just styling, the user experience must correctly reflect the core product pillars: 
1. **Decentralized Offline-First Design:** Leveraging Git as a core persistence layer. 
2. **ISO 21500 Readiness:** Presenting clear, measurable compliance tracking.
3. **Advanced Artifact Editing:** Upgrading inputs to include rich media (images/videos) and drag-and-drop.
4. **Agentic & Multimodal Scaffolding:** Preparing the UI for AI-driven generation, voice inputs, and auto-answers.
5. **Dual-Workflow Project Building:** Accommodating both guided template creation and unstructured scratch building.

---

## Part 1: Domain-Specific Findings & Friction Points

### 1. The Styling Decision: Tailwind System Transition
**Status:** The current architecture pairs almost every `.tsx` file with a raw `.css` file (e.g., `ArtifactEditor.css`, `ProjectView.css`).
*   **The Problem:** This violates scalable design-system principles. Responsive breakpoints (mobile vs desktop), dark mode, layout grids, and accessibility color contrast are inconsistently managed. Custom UI like Modals and Toasts are hard to maintain.
*   **The Solution:** Strip out all raw CSS in favor of **Tailwind CSS**. Integrate a robust headless primitive library (like Radix UI / shadcn) combined with Tailwind to standardize `Button`, `Input`, `Dialog`, and layout shells.

### 2. Decentralized Git Persistence (Offline-First UX)
**Status:** Git is the underlying state-engine, allowing for robust offline work and syncing, but the UI treats the application like a standard cloud web app.
*   **The Problem:** Users are not visually aware when they are completely offline, when they have local "commits" (unsynced changes), or when there are merge conflicts. The existing `SyncPanel.tsx` is pushed to the side rather than being a cornerstone of the header/navigation experience.
*   **The Solution:**
    *   Implement a **Global Sync & State Indicator** in the main navigation (e.g., "☁️ Synced", "⚠️ 3 Unsynced Changes", "🔌 Offline Mode").
    *   Design a clear "Pull/Push to Main" interaction paradigm that feels native, acknowledging that *offline-first* is the default capability.

### 3. ISO 21500 Readiness Measurement 
**Status:** `ReadinessBuilder.tsx` and `ReadinessChecks.tsx` exist, but fail to visually communicate the overarching progress of a project's compliance.
*   **The Problem:** Measuring the "readiness" of a project against the ISO 21500 standard is the app's *most important capability*, yet it lacks a commanding dashboard, visual metrics, or clear progress trackers (radar charts, completion rings).
*   **The Solution:** 
    *   Elevate "Readiness" from a mere data table tab to a **Progress Dashboard**.
    *   Provide visual scores (e.g., `75% Setup Ready`, `Audit Gate Pending`) that persist at the top of the `ProjectView`.
    *   Highlight specifically which artifacts or steps are blocking full ISO 21500 compliance.

### 4. ProjectBuilder (Dual-Workflows)
**Status:** `GuidedBuilder.tsx` forces users down a linear, single-path wizard.
*   **The Problem:** The ProjectBuilder needs to support at least two main overarching workflows (e.g., "Guided AI Template Route" vs. "Manual Scratch Route"). The current wizard does not visually branch, nor does it allow saving a drafted state to resume later.
*   **The Solution:**
    *   Introduce a clear visual **Branching Stepper** upon creating a new project. 
    *   Visually represent the user's path context in a sticky sidebar (so they know *which* workflow they are executing).

### 5. Artifact Editor & Rich Media UX
**Status:** `ArtifactEditor.tsx` acts like a basic text data-entry form. 
*   **The Problem:** Real-world project management requires rich media (flowcharts, PDFs, images, recorded video updates). The editor currently lacks modern capability (drag & drop, markdown embedding, full-screen focus mode).
*   **The Solution:**
    *   Implement a **Drag & Drop Zone** capturing file inputs directly on the interface.
    *   Add native support for rich inline media rendering (Images, Videos).
    *   Add a **Workspace Toggle** to let the editor snap to full-screen to eliminate side-bar and navigation distractions.

### 6. AI Agent & Multimodal Extensibility Hooks
**Status:** The current architecture offers no obvious entry points for next-generation automated agents and voice/audio I/O.
*   **The Problem:** Eventually, agents will create/modify artifacts and the system will accept voice commands. The UI layout is too rigid to accommodate floating AI tools without a major rewrite.
*   **The Solution:**
    *   **Agent Hooks:** Introduce an "AI Assist" contextual floating menu (`Command-K` palette or floating action button) inside the `ArtifactEditor` and ProjectBuilder. 
    *   **Multimodal Scaffolding:** Add reserved UI slots (e.g., a microphone toggle on inputs) structurally ready to accept Web Audio APIs. Leave architectural room for a generative "Auto-Answer" streaming text block.

### 7. Layout & God Components
**Status:** `ProjectView.tsx` orchestrates far too many domains (RAID, Readiness, Audit, Propose, Apply, Artifacts, Commands). 
*   **The Problem:** Because all components live in a flat `client/src/components/` folder, finding and scaling domain-specific code is difficult. 
*   **The Solution:** Standardize domains. Move `components/raid`, `components/artifacts`, `components/projects` into isolated features folders (`src/features/`).

---

## Part 2: Phased Implementation & Architecture Plan

This phased roadmap re-architects the folder structure and introduces new capabilities without breaking the existing backend contracts.

### Phase 1: Tailwind Foundation & Structure (The "Reset")
1. **Tooling Setup:** Install Tailwind CSS, PostCSS.
2. **Directory Restructure:** 
   * Create `src/components/ui/` (stateless standard components: Button, Modal, Card).
   * Create `src/features/` to house specific domains (e.g., `/features/artifacts`, `/features/builder`, `/features/compliance`).
3. **Purge CSS:** Systematically delete the 30+ `.css` files and convert all existing layouts to Tailwind utility classes.

### Phase 2: Offline-First Git UI Layers
1. **Global Header Updates:** Build a persistent top-navigation element tracking "Git Sync State" (Offline, Synced, Unsynced Actions).
2. **Conflict & Merge Views:** Centralize `SyncPanel` and `ConflictResolver` into an easily accessible Slide-Out Drawer (instead of burying it in a tab).

### Phase 3: ProjectBuilder Redesign (Dual-Workflow)
1. **Workflow Selector Screen:** Update the first step of `GuidedBuilder` to visually present the user with the two distinct tracks.
2. **Persistent Stepper:** Build a Tailwind step-tracker component that adapts to the chosen workflow dynamically. 

### Phase 4: Artifact Editor Overhaul & Media Support
1. **Dropzone Integration:** Wrap the Artifact Editor with `react-dropzone` (or similar) to handle media uploads.
2. **Full-Screen Canvas:** Implement a "focus mode" that expands the editor via absolute/fixed positioning over the rest of the layout.
3. **Media Renderer:** Extend the markdown/text viewer to safely render images/videos linked as artifacts.

### Phase 5: ISO 21500 Dashboarding
1. **Readiness Visuals:** Build circular progress bars and radar charts in `ReadinessChecks.tsx` representing exact percentages of project setup, planning, execution, and closing gates.
2. **Prominent Status:** Display the aggregate ISO compliance score natively on the Project list cards.

### Phase 6: Agentic Scaffolding & Multimodal Hooks
1. **Generative Overlay:** Within the `ArtifactEditor`, prepare an absolutely positioned "AI Suggestions" panel or inline ghost-text component.
2. **Voice Prompts:** Add muted but fully styled microphone/audio-waveform buttons next to text-heavy inputs, preparing the `<form>` layer to eventually dispatch audio arrays to the backend APIs.
3. **Agent Action Logs:** In the `<AuditViewer />`, ensure the layout distinguishes between "Human Action" and "AI Agent Action" with specific icons/colors.

---
**Next Immediate Action:** 
The team should execute **Phase 1** natively on a new branch. This enables the complete removal of the raw CSS files, setting up the required Tailwind foundation necessary to build the advanced widgets (Phase 2-6) seamlessly.