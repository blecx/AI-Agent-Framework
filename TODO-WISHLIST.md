# Future Enhancements & Wishlist

## 1. Enrich the "WebUI Designer" (blecs-ux-authority) Skill
- **Action:** Perform internet research on modern frontend meta-prompts (e.g., Anthropic's Claude 3.5 Sonnet UI coding guides and vercel/v0 prompt leaks).
- **Goal:** Upgrade the extracted UX skill to include state-of-the-art standards for React/Vite, Tailwind responsive design, and accessibility patterns.

## 2. Elevate the "Tutorial Writer" System Prompt
- **Action:** Pull in Microsoft's official technical writing guidelines and instructional design prompts.
- **Goal:** Optimize the tutorial bot to not just document, but use interactive learning prompt strategies. The current state has scattered files (`tutorial.md`, `tutorial-audit-strict.md`, `tutorial-default-prompt.md`) that need to be unified into a cohesive "Skill Package".

~~## 3. Handle Auxiliary Modules (`.github/prompts/modules/`)~~ (COMPLETED)
- **Status:** Extracted entirely into dynamic `.copilot/skills/`

~~## 4. Adopt Formal "Spec Kit" XML/Markdown Structures~~ (COMPLETED)
- **Status:** Automated script wrapped all skills strictly in valid XML descriptors.

~~## 5. Convert Relative Module Links to Skills~~ (COMPLETED)
- **Status:** Link graph fixed natively to point directly to `SKILL.md` boundaries.

~~## 6. Automate Regression Suite for Agent Settings~~ (COMPLETED)
- **Status:** Hooked into Pytest suite natively via `tests/unit/test_agent_prompts_architecture.py`.

## 7. Refine "maestro-operator.md" Bridging Logic (Agent <-> Terminal loop)
- **Action:** The newly created Maestro Operator triggers python scripts but could be more resilient to runtime traceback outputs.
- **Goal:** Write an instruction rule explicitly parsing any python exception traces and feeding them back structurally.
