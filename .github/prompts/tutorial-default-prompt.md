# Tutorial Agent — Team Default Prompt

Use this exact prompt when you want the custom `tutorial` agent to generate a complete, high-quality tutorial.

```text
Use subagent: tutorial

Create a [UX or TUI]-only tutorial for: [FLOW/FEATURE].
Output must be Markdown only.

Result description (required):
- Return a Markdown package with these sections in this order:
  1) Tutorial
  2) Feature Gap List
  3) Duplicate Content Audit
  4) Asset Regeneration

Include:
1) Screenshot-backed steps for major transitions (required).
2) Schema picture(s) from draw.io (required: source `.drawio` + exported `.svg` path).
3) Workflow picture(s) that visualize step flow (required).
4) A Feature Gap List (repro, expected vs actual, impact, suggested issue title).
5) A Duplicate Content Audit (identify overlap, choose canonical section, link instead of duplicate text).
6) A self-contained learning path for this track (no dependency on the other track).

Also include prerequisites, verification checklist, troubleshooting, and asset regeneration steps.
```
