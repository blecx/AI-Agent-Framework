# Future Enhancements & Wishlist (Phase 5+)

## 1. Enrich the "WebUI Designer" (blecs-ux-authority) Skill
- **Action:** Perform internet research on modern frontend meta-prompts (e.g., Anthropic's Claude 3.5 Sonnet UI coding guides and vercel/v0 prompt leaks).
- **Goal:** Upgrade the extracted UX skill to include state-of-the-art standards for React/Vite, Tailwind responsive design, and accessibility patterns.

## 2. Elevate the "Tutorial Writer" System Prompt
- **Action:** Pull in Microsoft's official technical writing guidelines and instructional design prompts.
- **Goal:** Optimize the tutorial bot to not just document, but use interactive learning prompt strategies. The current state has scattered files (`tutorial.md`, `tutorial-audit-strict.md`, `tutorial-default-prompt.md`) that need to be unified into a cohesive "Skill Package".

## 3. Handle Auxiliary Modules (`.github/prompts/modules/`)
- **Action:** We mapped the core agents, but there is a `modules/` directory containing things like `ux/delegation-policy.md`.
- **Goal:** These should be refactored into "Sub-Skills" or core instructions inside `.copilot/` so they are dynamically loaded rather than statically referenced by file path.

## 4. Adopt Formal "Spec Kit" XML/Markdown Structures
- **Action:** Research the very latest GitHub Copilot Custom Agent schemas (e.g., proper use of `<instructions>`, `<tools>`, and `<skill>` tags in `.md` files).
- **Goal:** Refactor the merged `.md` files so that they parse natively with the highest token efficiency in VS Code.

## 5. Convert Relative Module Links to Skills
- **Context:** During Phase 1 migration, we discovered that relative links like `../modules/tutorial-review-workflow.md` are brittle when directory structures change.
- **Action:** Convert `.github/prompts/modules/*` into `.copilot/skills/*` structure.
- **Goal:** Improve robustness. Subagents should trigger standard skills by semantic referencing ("Use the tutorial-review-workflow skill") instead of maintaining literal markdown filepath links.

## 6. Automate Regression Suite for Agent Settings
- **Context:** Renaming agents breaks `settings.json` and internal script expectations silently unless caught by `.venv/bin/python scripts/check_subagent_autoapprove.py` and `.venv/bin/python scripts/check_prompt_quality.py`.
- **Action:** Introduce an automated pre-commit hook or explicit `.github/workflows` test runner that runs both checking scripts.
- **Goal:** Provide "Continuous Integration" for Copilot Agent settings, preventing developer tools configurations from drifting out of alignment.

## 7. Migration of Sub-Agent Workflows
- **Context:** The Phase 4 cleanup proves `.github/prompts/` is successfully removed.
- **Action:** Future projects using this repo should look into `tests/unit/test_maestro.py` to ensure their test environments are resilient to prompt restructurings in the future.
