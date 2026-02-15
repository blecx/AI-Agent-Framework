# Tutorial Agent — Strict Audit Mode Prompt

Use this prompt when you want a **quality audit only** (no net-new tutorial authoring except factual corrections).

```text
Use subagent: tutorial

Run STRICT AUDIT MODE on existing tutorials only.

Scope:
- Track: [UX | TUI]
- Paths: [TARGET MARKDOWN FILES OR FOLDERS]

Hard requirements:
1) Output must be Markdown only.
2) Do not create new tutorial flows unless correcting factual errors.
3) Detect logical breaks, missing transitions, and functional mismatches.
4) Detect duplicate content and propose canonical sections + links.
5) Enforce visual coverage:
   - Screenshots (required for major transitions)
   - Schema picture(s) (required: draw.io source + SVG path)
   - Workflow picture(s) (required for end-to-end flow)

Result format (Markdown package):
1) Audit Summary
2) Defect List (severity + evidence)
3) Feature Gap List (developer handoff; repro, expected vs actual, impact, suggested issue title)
4) Duplicate Content Audit (overlap matrix + canonicalization decisions)
5) Visual Coverage Report (what exists, what is missing)
6) Prioritized Fix Plan

Quality constraints:
- No hallucinated behavior
- Evidence-backed findings only
- Keep UX/TUI fully separated
```
