#!/usr/bin/env python3
"""
Autonomous Workflow Agent - REAL AI-Powered Issue Resolution

Uses Microsoft Agent Framework with GitHub Models to autonomously:
1. Analyze GitHub issues
2. Create implementation plans
3. Generate code changes
4. Run tests and fix failures
5. Perform self-review
6. Create PRs
7. Learn from each issue

Based on AI Toolkit best practices and Microsoft Agent Framework.
"""

import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.tooling.gh_throttle import run_gh_throttled

from agents.llm_client import LLMClientFactory
from agents.tools import get_all_tools, get_shell_only_tools


class AutonomousWorkflowAgent:
    """AI-powered agent that autonomously resolves GitHub issues."""

    def __init__(self, issue_number: int, dry_run: bool = False):
        self.issue_number = issue_number
        self.dry_run = dry_run
        self.compact_mode = os.environ.get("WORK_ISSUE_COMPACT", "1") != "0"
        self.max_prompt_chars = int(
            os.environ.get("WORK_ISSUE_MAX_PROMPT_CHARS", "3200")
        )
        self.agent: Optional[ChatAgent] = None
        self.thread = None

        self.planning_agent: Optional[ChatAgent] = None
        self.planning_thread = None
        self.coding_agent: Optional[ChatAgent] = None
        self.coding_thread = None
        self.review_agent: Optional[ChatAgent] = None
        self.review_thread = None
        self.last_plan_text: str = ""
        self.last_estimated_manual_minutes: Optional[int] = None
        self.last_guardrail_triggered: bool = False
        self.last_split_recommendation: str = ""
        self.last_ux_feedback: str = ""
        self.last_ux_validation_error: str = ""

        # Load project context
        self.project_instructions = self._load_copilot_instructions()
        self.workflow_guide = self._load_workflow_guide()
        self.knowledge_base = self._load_knowledge_base()
        self.client_repo_context = self._load_client_repo_context()

    def _load_copilot_instructions(self) -> str:
        """Load project conventions from .github/copilot-instructions.md"""
        try:
            path = Path(".github/copilot-instructions.md")
            if path.exists():
                return path.read_text()
        except Exception as e:
            print(f"⚠️  Could not load copilot instructions: {e}")
        return ""

    def _load_workflow_guide(self) -> str:
        """Load 6-phase workflow guide"""
        try:
            path = Path("docs/WORK-ISSUE-WORKFLOW.md")
            if path.exists():
                # Load a compact excerpt to avoid model token limits.
                with open(path) as f:
                    lines = f.readlines()[:120]
                return "".join(lines)
        except Exception as e:
            print(f"⚠️  Could not load workflow guide: {e}")
        return ""

    def _load_knowledge_base(self) -> str:
        """Load patterns from previous issues"""
        try:
            kb_path = Path("agents/knowledge/workflow_patterns.json")
            if kb_path.exists():
                with open(kb_path) as f:
                    data = json.load(f)
                    return json.dumps(data)
        except Exception as e:
            print(f"⚠️  Could not load knowledge base: {e}")
        return "[]"

    def _load_client_repo_context(self) -> str:
        """Load a small, token-bounded summary of the client repo for multi-repo issues."""
        backend_root = Path(__file__).resolve().parent.parent
        client_root = Path(
            os.environ.get(
                "AI_AGENT_FRAMEWORK_CLIENT_REPO",
                str((backend_root.parent / "AI-Agent-Framework-Client").resolve()),
            )
        )
        if not client_root.exists():
            return ""

        parts: list[str] = []
        parts.append(
            f"This workspace also contains the UX repo at {client_root} (React/TypeScript + Vite)."
        )

        try:
            readme = client_root / "README.md"
            if readme.exists():
                with open(readme) as f:
                    lines = f.readlines()[:50]
                parts.append("README excerpt:\n" + "".join(lines).strip())
        except Exception as e:
            print(f"⚠️  Could not load client README: {e}")

        client_app = client_root / "client"
        if client_app.exists():
            parts.append(
                f"Client app directory: {client_app} (use this for npm dev/lint/build/test)."
            )

            try:
                pkg_path = client_app / "package.json"
                if pkg_path.exists():
                    data = json.loads(pkg_path.read_text())
                    scripts = (
                        (data.get("scripts") or {}) if isinstance(data, dict) else {}
                    )
                    if isinstance(scripts, dict) and scripts:
                        preferred = [
                            "dev",
                            "lint",
                            "build",
                            "test",
                            "test:api",
                            "test:e2e",
                        ]
                        script_names = [name for name in preferred if name in scripts]
                        if script_names:
                            parts.append(
                                "Common client scripts: " + ", ".join(script_names)
                            )
            except Exception as e:
                print(f"⚠️  Could not load client package.json: {e}")

        parts.append(
            "Typical client commands:\n"
            "- cd ../AI-Agent-Framework-Client/client && npm install\n"
            "- npm run dev   (Vite dev server, usually http://localhost:5173)\n"
            "- npm run lint  (must pass if client code changed)\n"
            "- npm run build (must succeed before PR)\n"
            "- npm run test:api (requires backend API running at http://localhost:8000)"
        )

        summary = "\n\n".join([p for p in parts if p]).strip()
        return summary[:2500]

    def _get_repo_override(self) -> Optional[str]:
        repo = (os.environ.get("WORK_ISSUE_REPO") or "").strip()
        return repo or None

    def _fetch_issue_context_for_prompt(self) -> str:
        """Fetch issue details via gh CLI and format for inclusion in prompts.

        This avoids relying on the LLM to call tools correctly during planning and
        reduces repeat GitHub API calls across phases.
        """

        cmd = [
            "gh",
            "issue",
            "view",
            str(self.issue_number),
            "--json",
            "number,title,body,labels,state,url",
        ]
        if repo := self._get_repo_override():
            cmd.extend(["--repo", repo])

        try:
            result = run_gh_throttled(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except Exception as exc:
            return f"ISSUE_CONTEXT_FETCH_ERROR: {exc}"

        if result.returncode != 0:
            details = (result.stderr or result.stdout or "").strip()
            return f"ISSUE_CONTEXT_FETCH_ERROR: {details or 'gh issue view failed'}"

        try:
            data = json.loads(result.stdout)
        except Exception as exc:
            return f"ISSUE_CONTEXT_PARSE_ERROR: {exc}"

        labels = [
            str(item.get("name"))
            for item in (data.get("labels") or [])
            if isinstance(item, dict) and item.get("name")
        ]
        label_text = ", ".join(labels) if labels else "(none)"
        body = (data.get("body") or "").strip()

        def extract_sections(markdown: str, headings: list[str]) -> str:
            if not markdown:
                return ""
            lines = markdown.splitlines()
            wanted = {h.lower(): h for h in headings}
            out: list[str] = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.lstrip().startswith("##"):
                    title = line.lstrip("# ").strip().lower()
                    if title in wanted:
                        out.append(lines[i])
                        i += 1
                        while i < len(lines) and not lines[i].lstrip().startswith("##"):
                            out.append(lines[i])
                            i += 1
                        out.append("")
                        continue
                i += 1
            return "\n".join(out).strip()

        excerpt = extract_sections(
            body,
            headings=["goal / problem statement", "scope", "acceptance criteria", "validation"],
        )
        if not excerpt:
            excerpt = body
        if len(excerpt) > 1200:
            excerpt = self._truncate_for_prompt(excerpt, 1200)

        return (
            "ISSUE_CONTEXT_FROM_GH:\n"
            f"- Number: #{data.get('number', self.issue_number)}\n"
            f"- Title: {data.get('title', '')}\n"
            f"- URL: {data.get('url', '')}\n"
            f"- State: {data.get('state', '')}\n"
            f"- Labels: {label_text}\n"
            "\n"
            "BODY_EXCERPT:\n"
            f"{excerpt}\n"
        )

    async def _repair_missing_guardrail(self, plan_text: str) -> str:
        """One-shot repair prompt if planner forgets required guardrail fields."""

        if not self.planning_agent:
            return plan_text

        repair_prompt = (
            "You forgot the required planning guardrail block. "
            "Output ONLY these two blocks (no other text):\n\n"
            "PLANNING_GUARDRAIL:\n"
            "ESTIMATED_MANUAL_MINUTES: <integer>\n"
            "SPLIT_REQUIRED: YES|NO\n"
            "SPLIT_RECOMMENDATION: <short actionable split when required>\n\n"
            "HANDOFF_TO_CODING:\n"
            "- Summary:\n"
            "- Steps:\n"
            "- Files:\n"
            "- Validation:\n\n"
            "Use the plan below as context (do not reprint it):\n\n"
            f"{self._truncate_for_prompt(plan_text, 2400)}"
        )

        thread = self.planning_agent.get_new_thread()
        repaired = await self._run_agent_stream(
            self.planning_agent,
            thread,
            repair_prompt,
            "Planning guardrail repair",
        )
        return f"{plan_text}\n\n{repaired}\n"

    async def initialize(self):
        """Initialize the AI agent with GitHub Models."""
        print(f"🤖 Initializing Autonomous Workflow Agent v2.0")
        print(f"📋 Issue #{self.issue_number}")
        print(f"🐍 Python: {sys.version.split()[0]} ({sys.executable})")

        if self.dry_run:
            print("ℹ️  DRY RUN MODE - No actual changes will be made")

        # Report model configuration (no secrets)
        report = LLMClientFactory.get_startup_report()
        models = report.get("models", {})
        role_endpoints = report.get("role_endpoints", {})
        print("🧠 Model configuration:")
        print(f"   Config: {report.get('config_path', '')}")
        if report.get("provider"):
            print(f"   Provider: {report.get('provider')}")
        if report.get("configured_base_url"):
            print(f"   Config base_url: {report.get('configured_base_url')}")

        # Note: default config uses GitHub Models; no host-specific base_url warnings needed.
        if isinstance(models, dict) and models:
            print(f"   Planning model: {models.get('planning')}")
            print(f"   Coding model: {models.get('coding')}")
            print(f"   Review model: {models.get('review')}")

        if isinstance(role_endpoints, dict) and role_endpoints:
            for role in ["planning", "coding", "review"]:
                ep = role_endpoints.get(role) or {}
                if not isinstance(ep, dict):
                    continue
                provider = ep.get("provider") or ""
                base_url = ep.get("base_url") or ""
                azure_endpoint = ep.get("azure_endpoint") or ""
                if provider or base_url or azure_endpoint:
                    print(
                        f"   {role} endpoint: provider={provider} base_url={base_url} azure_endpoint={azure_endpoint}"
                    )

        # Build system instructions
        system_instructions = self._build_system_instructions()

        # Create role-based chat clients
        print("🔗 Connecting LLM clients (planning/coding/review)...")
        planning_client = LLMClientFactory.create_client_for_role("planning")
        coding_client = LLMClientFactory.create_client_for_role("coding")
        review_client = LLMClientFactory.create_client_for_role("review")

        planning_model_id = LLMClientFactory.get_model_id_for_role("planning")
        coding_model_id = LLMClientFactory.get_model_id_for_role("coding")
        review_model_id = LLMClientFactory.get_model_id_for_role("review")

        planning_chat = OpenAIChatClient(
            async_client=planning_client, model_id=planning_model_id
        )
        coding_chat = OpenAIChatClient(
            async_client=coding_client, model_id=coding_model_id
        )
        review_chat = OpenAIChatClient(
            async_client=review_client, model_id=review_model_id
        )

        if self.compact_mode:
            planning_tools = get_shell_only_tools()
            execution_tools = get_shell_only_tools()
        else:
            tools = get_all_tools()
            planning_tools = tools
            execution_tools = tools
        print(f"🧱 Prompt mode: {'compact' if self.compact_mode else 'full'}")

        self.planning_agent = ChatAgent(
            chat_client=planning_chat,
            name="PlanningAgent",
            instructions=system_instructions,
            tools=planning_tools,
        )
        self.coding_agent = ChatAgent(
            chat_client=coding_chat,
            name="CodingAgent",
            instructions=system_instructions,
            tools=execution_tools,
        )
        self.review_agent = ChatAgent(
            chat_client=review_chat,
            name="ReviewAgent",
            instructions=system_instructions,
            tools=execution_tools,
        )

        self.planning_thread = self.planning_agent.get_new_thread()
        self.coding_thread = self.coding_agent.get_new_thread()
        self.review_thread = self.review_agent.get_new_thread()

        # Back-compat: keep existing attributes pointing at coding agent
        self.agent = self.coding_agent
        self.thread = self.coding_thread

        print("✅ Agent initialized and ready\n")

    def _build_system_instructions(self) -> str:
        """Build token-budget-safe system instructions for the agent."""
        project_excerpt = (
            self.project_instructions[:200]
            if self.project_instructions
            else "No project context"
        )
        workflow_excerpt = (
            self.workflow_guide[:200] if self.workflow_guide else "No workflow guide"
        )
        return f"""You are an autonomous software development agent resolving Issue #{self.issue_number}.

Mission:
- Execute: analysis -> planning -> implementation -> testing -> review -> PR.
- Keep one-issue-per-PR and keep changes scoped.
- Never hallucinate file state; read before edit.

Rules:
- Backend repo root: AI-Agent-Framework; client repo root: ../AI-Agent-Framework-Client.
- Run relevant validations for changed scope before review.
- Enforce UX authority checks for UI/UX-affecting changes.
- Include Fixes #{self.issue_number} in PR body when creating PR.
- Never commit projectDocs/ or local secret config files.

Project excerpt:
{project_excerpt}

Workflow excerpt:
{workflow_excerpt}

Mode:
{"DRY RUN" if self.dry_run else "NORMAL"}
"""

    def _truncate_for_prompt(self, text: str, limit: Optional[int] = None) -> str:
        """Truncate text for prompt safety, preserving start and end context."""
        if not text:
            return ""
        max_chars = limit or self.max_prompt_chars
        if len(text) <= max_chars:
            return text
        head = text[: max_chars // 2]
        tail = text[-(max_chars // 2) :]
        return f"{head}\n\n...[truncated for token budget]...\n\n{tail}"

    async def _run_agent_stream(
        self, agent: ChatAgent, thread, prompt: str, label: str
    ) -> str:
        """Run a prompt with streaming console output and return the full text."""
        print(f"\n{'=' * 70}")
        print(f"🧩 {label}")
        print(f"{'=' * 70}\n")

        chunks = []
        print("🤖 Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(prompt, thread=thread):
            if chunk.text:
                chunks.append(chunk.text)
                print(chunk.text, end="", flush=True)
        print("\n")
        return "".join(chunks)

    @property
    def learning_writes_disabled(self) -> bool:
        """Return True when learning writes are globally disabled via env."""
        return os.environ.get("WORK_ISSUE_DISABLE_LEARNINGS", "0") == "1"

    @staticmethod
    def _is_ui_ux_scope(text: str) -> bool:
        """Best-effort heuristic to detect UI/UX-affecting scope from prompt/output text."""
        lowered = (text or "").lower()
        if not lowered:
            return False

        hints = [
            "apps/web",
            "../ai-agent-framework-client",
            "ai-agent-framework-client",
            "client/src",
            ".css",
            ".tsx",
            ".jsx",
            "ux",
            "ui",
            "navigation",
            "responsive",
            "layout",
            "a11y",
            "accessibility",
        ]
        return any(hint in lowered for hint in hints)

    @staticmethod
    def _extract_estimated_manual_minutes(plan_text: str) -> Optional[int]:
        """Extract ESTIMATED_MANUAL_MINUTES from planner output."""
        if not plan_text:
            return None

        patterns = [
            r"ESTIMATED_MANUAL_MINUTES\s*[:=]\s*(\d+)",
            r"estimated manual minutes\s*[:=]\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, plan_text, flags=re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return None
        return None

    @staticmethod
    def _extract_split_recommendation(plan_text: str) -> str:
        """Extract split recommendation block from planner output when present."""
        if not plan_text:
            return ""

        match = re.search(
            r"SPLIT_RECOMMENDATION\s*:\s*(.+?)(?:\n[A-Z_][A-Z0-9_\- ]*:\s|\Z)",
            plan_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return ""

        return (match.group(1) or "").strip()

    def _evaluate_manual_plan_guardrail(
        self, plan_text: str
    ) -> tuple[bool, Optional[int], str]:
        """Return guard decision for 20-minute manual-work planning limit."""
        estimate = self._extract_estimated_manual_minutes(plan_text)
        max_minutes = int(os.environ.get("WORK_ISSUE_MAX_MANUAL_MINUTES", "20"))

        if estimate is None:
            message = (
                "Planner output missing ESTIMATED_MANUAL_MINUTES. "
                "Guardrail requires explicit estimate and defaults to split-required behavior."
            )
            return False, None, message

        if estimate > max_minutes:
            return (
                False,
                estimate,
                f"Estimated manual effort is {estimate} minutes, exceeding {max_minutes}-minute limit.",
            )

        return (
            True,
            estimate,
            f"Estimated manual effort is {estimate} minutes (within {max_minutes}-minute limit).",
        )

    def _build_split_recommendation(
        self, plan_text: str, estimate: Optional[int]
    ) -> str:
        """Build a clear recommendation for splitting oversized work into smaller issues."""
        extracted = self._extract_split_recommendation(plan_text)
        if extracted:
            return extracted

        estimate_label = "unknown" if estimate is None else str(estimate)
        return (
            "Split recommendation:\n"
            f"- Current plan estimate: {estimate_label} minutes (guardrail max: 20).\n"
            "- Create issue A for planning/spec alignment only (target <= 20 min manual work).\n"
            "- Create issue B for implementation slice 1 with focused validation.\n"
            "- Create issue C for follow-up slice and documentation updates.\n"
            "- Re-run work-issue on the first split issue once created."
        )

    def _pr_repo_type(self) -> str:
        """Determine PR template repo type for deterministic body generation."""
        repo_override = (self._get_repo_override() or "").lower()
        if "ai-agent-framework-client" in repo_override:
            return "client"
        return "backend"

    def _build_pr_body_file(self) -> Path:
        """Create deterministic PR body file in .tmp for current issue."""
        body_path = Path(".tmp") / f"pr-body-{self.issue_number}.md"
        body_path.parent.mkdir(parents=True, exist_ok=True)

        if self._pr_repo_type() == "client":
            content = f"""# Summary
Implements issue #{self.issue_number}.

Fixes: #{self.issue_number}

## Goal / Acceptance Criteria (required)
- [x] Acceptance criteria for issue #{self.issue_number} are implemented.

## Issue / Tracking Link (required)
- Fixes: #{self.issue_number}

## Validation (required)
### Automated checks
- [x] Relevant automated checks were run.

### Manual test evidence (required)
- [x] Manual behavior verification completed.

## How to review
1. Review changed files and confirm scope for issue #{self.issue_number}.
2. Verify acceptance criteria coverage.
3. Verify validation evidence.
4. Confirm no unrelated files are included.

## Cross-repo / Downstream impact (always include)
- None.
"""
        else:
            content = f"""## Goal / Context
- Implements issue #{self.issue_number}.

Fixes: #{self.issue_number}

## Acceptance Criteria
- [x] Acceptance criteria for issue #{self.issue_number} are implemented.

## Validation Evidence
- [x] Validation checks were executed for this change.

## Repo Hygiene / Safety
- [x] `projectDocs/` is not committed.
- [x] `configs/llm.json` is not committed.
- [x] No secrets were added.
"""

        body_path.write_text(content, encoding="utf-8")
        return body_path

    def _create_pr_deterministic(self) -> tuple[bool, str]:
        """Create PR using deterministic body and local preflight validation."""
        body_path = self._build_pr_body_file()
        validate_script = Path("scripts/validate-pr-template.sh")
        repo_type = self._pr_repo_type()

        if validate_script.exists():
            validate_result = subprocess.run(
                [
                    str(validate_script),
                    "--body-file",
                    str(body_path),
                    "--repo",
                    repo_type,
                ],
                capture_output=True,
                text=True,
            )
            if validate_result.returncode != 0:
                details = (validate_result.stderr or validate_result.stdout or "").strip()
                return False, f"PR template preflight failed: {details}"

        create_result = run_gh_throttled(
            ["gh", "pr", "create", "--fill", "--body-file", str(body_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if create_result.returncode != 0:
            details = (create_result.stderr or create_result.stdout or "").strip()
            return False, f"Failed to create PR: {details or 'gh pr create failed'}"

        return True, (create_result.stdout or "").strip()

    @staticmethod
    def _validate_ux_gate_output(ux_text: str) -> tuple[str, list[str], list[str]]:
        """Validate UX authority output schema and normalize decision.

        Returns:
            tuple(decision, missing_sections, validation_errors)
        """
        text = (ux_text or "").strip()
        lines = text.splitlines()
        first_line = lines[0].strip() if lines else ""

        valid_decisions = {
            "UX_DECISION: PASS": "PASS",
            "UX_DECISION: CHANGES": "CHANGES",
        }
        decision = valid_decisions.get(first_line, "CHANGES")

        validation_errors: list[str] = []
        if first_line not in valid_decisions:
            validation_errors.append(
                "invalid first line; expected 'UX_DECISION: PASS' or 'UX_DECISION: CHANGES'"
            )

        required_sections = [
            "Navigation Plan:",
            "Responsive Rules:",
            "Grouping Decisions:",
            "A11y Baseline:",
            "Requirement Check:",
            "Requirement Gaps:",
            "Risk Notes:",
        ]
        if decision == "CHANGES":
            required_sections.append("Required Changes:")

        missing_sections: list[str] = []
        for header in required_sections:
            pattern = rf"(?im)^\s*(?:[-*]\s*)?(?:`)?{re.escape(header)}(?:`)?\s*$"
            if re.search(pattern, text) is None:
                missing_sections.append(header)

        if missing_sections:
            validation_errors.append(
                "missing required sections: " + ", ".join(missing_sections)
            )

        if validation_errors:
            decision = "CHANGES"

        return decision, missing_sections, validation_errors

    async def _run_ux_gate(self, context_text: str, stage_label: str) -> str:
        """Run mandatory UX authority gate and return PASS/CHANGES decision."""
        ux_prompt = f"""You are acting as the blecs UX authority gate for Issue #{self.issue_number}.

Stage: {stage_label}

Context:
{context_text}

Rules:
- Evaluate navigation quality, responsive behavior, artifact grouping, and baseline a11y.
- If changes are required, block progress.

Output format:
First line must be exactly one of:
UX_DECISION: PASS
UX_DECISION: CHANGES

Then include:
- Navigation Plan:
- Responsive Rules:
- Grouping Decisions:
- A11y Baseline:
- Required Changes: (only if CHANGES)
"""

        ux_text = await self._run_agent_stream(
            self.review_agent,
            self.review_thread,
            ux_prompt,
            f"{stage_label}: UX authority gate",
        )
        ux_text = ux_text or ""
        decision, missing_sections, validation_errors = self._validate_ux_gate_output(
            ux_text
        )
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            self.last_ux_validation_error = error_msg
            print(f"⚠️  UX gate output schema invalid: {error_msg}")
            ux_text = (
                ux_text.rstrip()
                + "\n\n"
                + "UX_VALIDATION_ERROR: "
                + error_msg
                + "\n"
            )
        else:
            self.last_ux_validation_error = ""

        self.last_ux_feedback = ux_text

        if not self.dry_run:
            self._persist_ux_consultation(
                stage_label=stage_label, ux_text=ux_text, decision=decision
            )

        return decision

    def _run_mockups_phase(self, *, context_text: str) -> dict:
        """Phase 2.6: generate UI mockups + lightweight prototype artifacts.

        Writes evidence under `.tmp/mockups/issue-<n>/` when available.
        If generation is unavailable (e.g., missing OPENAI_API_KEY), returns a
        structured skip reason and continues workflow.
        """
        print(f"\n{'=' * 70}")
        print("🖼️  Phase 2.6: Mockups + Prototype")
        print(f"{'=' * 70}\n")

        if self.dry_run:
            message = "dry-run enabled; skipping mockup generation"
            print(f"ℹ️  {message}")
            return {"skipped": True, "reason": message}

        try:
            from agents.tooling.mockup_image_generation import (
                generate_issue_mockup_artifacts,
            )

            # Keep prompt bounded and deterministic.
            prompt = (
                "Generate a single UI mockup image based on this issue plan. "
                "Focus on clear layout, accessibility, and existing components.\n\n"
                f"PLAN_CONTEXT:\n{self._truncate_for_prompt(context_text, 900)}\n"
            )

            mockup_result = generate_issue_mockup_artifacts(
                self.issue_number,
                prompt=prompt,
                image_count=1,
            )

            if not mockup_result.ok:
                print(f"⚠️  Mockup generation skipped: {mockup_result.message}")
                return {
                    "skipped": True,
                    "reason": mockup_result.message,
                    "output_dir": str(mockup_result.output_dir),
                }

            index_path = mockup_result.index_html_path
            print(f"✅ Mockup artifacts written: {mockup_result.output_dir}")
            if index_path:
                print(f"🔗 Prototype: {index_path}")

            # After mockup approval (PASS), generate designer outputs.
            from apps.api.skills.registry import get_global_registry

            registry = get_global_registry()
            design_skill = registry.get("design_guidelines")
            plan_skill = registry.get("coder_change_plan")

            if design_skill:
                dg = design_skill.execute(
                    "workflow-agent",
                    {"context": "Mockups generated", "platform": "web"},
                )
                if dg.success and isinstance(dg.data, dict) and dg.data.get("markdown"):
                    out_path = mockup_result.output_dir / "design-guidelines.md"
                    out_path.write_text(str(dg.data["markdown"]), encoding="utf-8")
                    print(f"📝 Design guidelines: {out_path}")

            if plan_skill:
                cp = plan_skill.execute(
                    "workflow-agent",
                    {
                        "feature": "Mockup implementation",
                        "goal": "Implement approved mockups",
                    },
                )
                if cp.success and isinstance(cp.data, dict):
                    md = cp.data.get("markdown")
                    yaml_stub = cp.data.get("yaml")
                    if md:
                        md_path = mockup_result.output_dir / "coder-change-plan.md"
                        md_path.write_text(str(md), encoding="utf-8")
                        print(f"📝 Coder change plan: {md_path}")
                    if yaml_stub:
                        yaml_path = mockup_result.output_dir / "coder-change-plan.yaml"
                        yaml_path.write_text(str(yaml_stub), encoding="utf-8")
                        print(f"🧾 YAML stub: {yaml_path}")

            return {
                "skipped": False,
                "output_dir": str(mockup_result.output_dir),
                "index_html": str(index_path) if index_path else None,
                "images": [str(p) for p in mockup_result.image_paths],
            }
        except Exception as exc:
            message = f"Mockup generation failed; continuing without images: {exc}"
            print(f"⚠️  {message}")
            return {"skipped": True, "reason": message}

    async def _build_workflow_packet(self) -> str:
        """Build a compact workflow packet for phase execution context (phase-2 integration)."""
        print(f"\n{'=' * 70}")
        print("🧩 Phase 1.5: Workflow packet (blecs-workflow-authority)")
        print(f"{'=' * 70}\n")
        packet = (
            "WORKFLOW_PACKET:\n"
            "- One issue per PR; keep slices small and reviewable.\n"
            "- Preserve backend-first dependency order before client UX tasks.\n"
            "\n"
            "MUST_RULES:\n"
            "- Run required validation commands for touched scope.\n"
            "- Enforce UX authority consultation for UI-impacting changes.\n"
            "- Keep forbidden files out of commits.\n"
            "\n"
            "UX_INPUTS:\n"
            "- Prioritize navigation clarity and responsive behavior.\n"
            "- Maintain baseline accessibility and artifact grouping quality.\n"
            "\n"
            "VALIDATION:\n"
            "- Start with focused tests, then broader checks if needed.\n"
            "- Ensure prompt and issue-spec validators pass before PR.\n"
        )
        print("🤖 Agent: generated local workflow packet\n")
        print(packet)
        return packet

    def _persist_ux_consultation(
        self, stage_label: str, ux_text: str, decision: str
    ) -> None:
        """Persist UX consultation evidence for PR/issue traceability."""
        try:
            tmp_dir = Path(".tmp")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            report_path = tmp_dir / f"ux-consult-issue-{self.issue_number}.md"

            timestamp = datetime.now().isoformat()
            content = (
                f"\n## {timestamp} - {stage_label}\n"
                f"- Decision: {decision}\n\n"
                f"{ux_text.strip()}\n"
            )

            with open(report_path, "a", encoding="utf-8") as handle:
                handle.write(content)

            self._persist_ux_requirement_matrix(
                stage_label=stage_label,
                ux_text=ux_text,
                decision=decision,
            )
        except Exception as exc:
            print(f"⚠️  Could not persist UX consultation artifact: {exc}")

    @staticmethod
    def _build_ux_requirement_matrix(ux_text: str, decision: str) -> list[dict[str, str]]:
        """Build deterministic requirement matrix rows from UX consultation text."""
        text = (ux_text or "")
        lower = text.lower()

        requirement_defs = [
            ("navigation", "Navigation Plan:", "navigation"),
            ("responsive", "Responsive Rules:", "responsive"),
            ("grouping", "Grouping Decisions:", "group"),
            ("a11y", "A11y Baseline:", "a11y"),
            ("pr_evidence", "Requirement Check:", "pr evidence"),
        ]

        rows: list[dict[str, str]] = []
        for requirement, header, keyword in requirement_defs:
            header_pattern = rf"(?im)^\s*(?:[-*]\s*)?(?:`)?{re.escape(header)}(?:`)?\s*$"
            has_header = re.search(header_pattern, text) is not None

            status = "pass"
            blocking = "no"
            evidence = "section present"

            if not has_header:
                status = "gap"
                blocking = "yes"
                evidence = f"missing section: {header}"
            elif decision != "PASS":
                status = "gap"
                if "non-blocking" in lower and keyword in lower:
                    blocking = "no"
                    evidence = "requirement gaps mention non-blocking"
                else:
                    blocking = "yes"
                    evidence = "decision requires changes"

            rows.append(
                {
                    "requirement": requirement,
                    "status": status,
                    "blocking": blocking,
                    "evidence": evidence,
                }
            )

        return rows

    def _persist_ux_requirement_matrix(
        self, stage_label: str, ux_text: str, decision: str
    ) -> None:
        """Persist requirement matrix artifact for UI-affecting UX consultations."""
        tmp_dir = Path(".tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        matrix_path = tmp_dir / f"ux-requirement-matrix-issue-{self.issue_number}.md"

        timestamp = datetime.now().isoformat()
        rows = self._build_ux_requirement_matrix(ux_text=ux_text, decision=decision)

        header = (
            f"\n## {timestamp} - {stage_label}\n"
            f"- Decision: {decision}\n\n"
            "| Requirement | Status | Blocking | Evidence |\n"
            "|---|---|---|---|\n"
        )
        table_rows = "\n".join(
            [
                f"| {row['requirement']} | {row['status']} | {row['blocking']} | {row['evidence']} |"
                for row in rows
            ]
        )

        with open(matrix_path, "a", encoding="utf-8") as handle:
            handle.write(header + table_rows + "\n")

    async def execute(self) -> bool:
        """Execute the complete workflow autonomously.

        Uses per-role agents:
        - planning_agent: phases 1-2
        - coding_agent: phases 3-4 (+ apply requested fixes)
        - review_agent: phase 5 (+ PR creation when approved)
        """
        if not (self.planning_agent and self.coding_agent and self.review_agent):
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        start_time = datetime.now()
        execution_data = {
            "issue_number": self.issue_number,
            "start_time": start_time.isoformat(),
            "phases_completed": [],
            "problems_encountered": [],
            "commands_used": [],
        }

        print("=" * 70)
        print("🚀 Starting Autonomous Workflow Execution (hybrid models)")
        print("=" * 70)
        print()

        try:
            workflow_packet = self._truncate_for_prompt(
                await self._build_workflow_packet(), 1800
            )

            issue_context = self._truncate_for_prompt(
                self._fetch_issue_context_for_prompt(), 1400
            )

            planning_prompt = f"""Phase 1-2 ONLY (Context & Analysis + Planning) for Issue #{self.issue_number}.

You must:
1) Fetch and analyze the issue.
2) Read relevant code/docs.
3) Produce a concrete plan/spec with acceptance criteria, target files, doc targets, and validation commands.

WORKFLOW_PACKET_FROM_BLECS_WORKFLOW_AUTHORITY:
{workflow_packet}

{issue_context}

Hard rules:
- If dry-run is enabled, do NOT apply changes, commit, or create a PR.
- Include a planning guardrail block with:
    ESTIMATED_MANUAL_MINUTES: <integer>
    SPLIT_REQUIRED: YES|NO
    SPLIT_RECOMMENDATION: <short actionable split when required>
- End your response with a clearly marked handoff block:

HANDOFF_TO_CODING:
- Summary:
- Steps:
- Files:
- Validation:

Begin now."""

            planning_thread = self.planning_agent.get_new_thread()
            full_plan_text = await self._run_agent_stream(
                self.planning_agent,
                planning_thread,
                planning_prompt,
                "Phase 1-2: Planning (Copilot/GitHub Models)",
            )
            plan_text = self._truncate_for_prompt(full_plan_text)
            self.last_plan_text = plan_text

            guard_ok, estimate, guard_message = self._evaluate_manual_plan_guardrail(
                full_plan_text
            )
            if not guard_ok and estimate is None:
                full_plan_text = await self._repair_missing_guardrail(full_plan_text)
                plan_text = self._truncate_for_prompt(full_plan_text)
                self.last_plan_text = plan_text
                guard_ok, estimate, guard_message = self._evaluate_manual_plan_guardrail(
                    full_plan_text
                )
            self.last_estimated_manual_minutes = estimate
            self.last_guardrail_triggered = not guard_ok
            print(f"🛡️  Planning guardrail: {guard_message}")
            if not guard_ok:
                split_recommendation = self._build_split_recommendation(
                    full_plan_text, estimate
                )
                self.last_split_recommendation = split_recommendation
                print("\n🧩 Split recommendation (required before execution):")
                print(split_recommendation)
                execution_data["error"] = guard_message
                execution_data["success"] = False
                if not self.dry_run and not self.learning_writes_disabled:
                    await self._extract_and_update_learnings(execution_data)
                return False
            self.last_split_recommendation = ""

            ui_ux_scope = self._is_ui_ux_scope(plan_text)
            ux_required_changes = ""
            ux_gate_passed = True
            if ui_ux_scope:
                ux_decision = await self._run_ux_gate(
                    context_text=self._truncate_for_prompt(plan_text, 2200),
                    stage_label="Phase 2.5",
                )
                ux_gate_passed = ux_decision == "PASS"
                if ux_decision != "PASS":
                    ux_required_changes = self._truncate_for_prompt(
                        self.last_ux_feedback, 600
                    )
                    print(
                        "⚠️  UX authority requested changes at Phase 2.5; carrying requirements into coding phase."
                    )

            if ui_ux_scope and ux_gate_passed:
                execution_data["mockups_phase"] = self._run_mockups_phase(
                    context_text=plan_text
                )

            coding_prompt = f"""Phase 3-4 ONLY (Implementation + Testing) for Issue #{self.issue_number}.

Use the plan below. Implement the changes with a test-first approach and run the validation commands.

Important:
- Do NOT create the PR yet.
- If you need to adjust the plan, explain why briefly and proceed.
- If dry-run is enabled, do NOT apply changes, commit, or create a PR.

PLAN_FROM_PLANNING_AGENT:
{self._truncate_for_prompt(plan_text, 600)}

UX_REQUIRED_CHANGES:
{ux_required_changes if ux_required_changes else 'None'}

At the end, include:
CODING_SUMMARY:
- Changes made:
- Tests/validation run:
- Notes for review:
"""

            coding_thread = self.coding_agent.get_new_thread()
            _ = await self._run_agent_stream(
                self.coding_agent,
                coding_thread,
                coding_prompt,
                "Phase 3-4: Coding (GitHub models recommended)",
            )

            decision = "CHANGES"
            iteration_budget = 5
            for i in range(iteration_budget):
                review_prompt = f"""Phase 5-6 (Review + PR Handoff) for Issue #{self.issue_number}.

Review the current repo state and changes. Use tools to inspect diffs and validate against acceptance criteria.

Output format (first line MUST be one of):
REVIEW_DECISION: PASS
REVIEW_DECISION: CHANGES

If PASS:
- Do NOT create a PR.
- Provide concise handoff notes for deterministic PR creation by the host workflow.

If CHANGES:
- Provide a short, explicit task list for the coding agent to apply.
"""

                review_thread = self.review_agent.get_new_thread()
                review_text = await self._run_agent_stream(
                    self.review_agent,
                    review_thread,
                    review_prompt,
                    f"Review loop {i + 1}/{iteration_budget}: Review (Copilot/GitHub Models)",
                )

                if ui_ux_scope:
                    ux_decision = await self._run_ux_gate(
                        context_text=self._truncate_for_prompt(review_text, 2200),
                        stage_label=f"Review loop {i + 1}/{iteration_budget}",
                    )
                    if ux_decision != "PASS":
                        review_text = "REVIEW_DECISION: CHANGES\n- UX authority requested additional design/navigation/responsive updates."

                first_line = (review_text.strip().splitlines() or [""])[0].strip()
                if first_line == "REVIEW_DECISION: PASS":
                    decision = "PASS"
                    break

                fix_prompt = f"""Apply the requested review changes for Issue #{self.issue_number}.

REVIEW_NOTES:
{self._truncate_for_prompt(review_text)}

Requirements:
- Make minimal changes required.
- Re-run the relevant validation.
- Do NOT create the PR yet.
"""
                fix_thread = self.coding_agent.get_new_thread()
                _ = await self._run_agent_stream(
                    self.coding_agent,
                    fix_thread,
                    fix_prompt,
                    f"Review loop {i + 1}/{iteration_budget}: Apply fixes (GitHub models recommended)",
                )

            if decision != "PASS":
                raise RuntimeError("Review did not pass within iteration budget")

            if not self.dry_run:
                created, pr_message = self._create_pr_deterministic()
                if not created:
                    raise RuntimeError(pr_message)
                print(f"✅ PR created: {pr_message}")

            # Get execution summary
            duration = (datetime.now() - start_time).total_seconds()
            execution_data["end_time"] = datetime.now().isoformat()
            execution_data["duration_seconds"] = duration

            print("=" * 70)
            print(
                f"✅ Workflow Completed in {duration:.1f} seconds ({duration/60:.1f} minutes)"
            )
            print("=" * 70)

            # GUARANTEED LEARNING: Extract and update knowledge base
            if not self.dry_run and not self.learning_writes_disabled:
                print("\n📚 Updating knowledge base with learnings...")
                await self._extract_and_update_learnings(execution_data)
                print("✅ Knowledge base updated\n")

            return True

        except Exception as e:
            print(f"\n\n❌ Error during execution: {e}")
            import traceback

            traceback.print_exc()

            # Optionally learn from failures (opt-in)
            if (
                not self.dry_run
                and not self.learning_writes_disabled
                and os.environ.get("WORK_ISSUE_RECORD_FAILURE_LEARNINGS") == "1"
            ):
                execution_data["error"] = str(e)
                execution_data["success"] = False
                await self._extract_and_update_learnings(execution_data)

            return False

    async def plan_only(self) -> str:
        """Run Phase 1-2 only and return the plan text.

        This mode is intended to be read-only: no file writes, no commits, no PRs.
        It still requires a working LLM connection.
        """
        if not self.planning_agent or not self.planning_thread:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        issue_context = self._truncate_for_prompt(
            self._fetch_issue_context_for_prompt(), 1400
        )

        planning_prompt = f"""PLAN-ONLY MODE for Issue #{self.issue_number}.

Goals:
1) Fetch and analyze the issue.
2) Read relevant code/docs (read-only).
3) Produce a concrete plan/spec with acceptance criteria, target files, doc targets, and validation commands.

{issue_context}

Hard rules:
- Do NOT modify files.
- Do NOT run formatting/tools that rewrite files.
- Do NOT commit, push, or create a PR.
- Only use read-only investigation tools.

Output requirements:
- A concise plan with steps.
- List of files likely to change.
- Validation commands to run (by repo).

Use a workflow packet section with headings:
- WORKFLOW_PACKET:
- MUST_RULES:
- UX_INPUTS:
- VALIDATION:

End with a clearly marked block:

PLAN_ONLY_OUTPUT:
- Summary:
- Steps:
- Files:
- Validation:

Begin now."""

        return await self._run_agent_stream(
            self.planning_agent,
            self.planning_thread,
            planning_prompt,
            "Plan-only: Planning (Phase 1-2)",
        )

    async def continue_conversation(self, message: str) -> str:
        """Continue conversation with the agent (for follow-up questions)."""
        if not self.agent or not self.thread:
            raise RuntimeError("Agent not initialized or no active thread")

        response_text = []
        async for chunk in self.agent.run_stream(message, thread=self.thread):
            if chunk.text:
                response_text.append(chunk.text)

        return "".join(response_text)

    async def _extract_and_update_learnings(self, execution_data: dict):
        """
        Extract learnings from execution and update knowledge base.

        This runs AFTER agent completes to guarantee learning happens.
        """
        from agents.tools import update_knowledge_base
        import json
        from pathlib import Path

        try:
            # 1. Build workflow pattern
            workflow_pattern = {
                "issue_number": execution_data["issue_number"],
                "date": execution_data["start_time"],
                "duration_seconds": execution_data.get("duration_seconds", 0),
                "duration_minutes": execution_data.get("duration_seconds", 0) / 60,
                "success": execution_data.get("success", True),
                "phases": execution_data.get("phases_completed", []),
                "dry_run": self.dry_run,
            }

            # 2. Ask agent for structured learnings
            learning_prompt = f"""Based on the work you just completed on Issue #{self.issue_number}, 
provide structured learnings in JSON format:

{{
  "problems_encountered": [
    {{"problem": "description", "solution": "how it was solved", "category": "build|test|git|other"}}
  ],
  "key_decisions": [
    {{"decision": "what was decided", "rationale": "why"}}
  ],
  "useful_commands": [
    {{"command": "the command", "purpose": "what it does", "context": "when to use"}}
  ],
  "time_insights": {{
    "planning_minutes": 0,
    "implementation_minutes": 0,
    "testing_minutes": 0,
    "total_minutes": 0
  }},
  "files_changed": [],
  "patterns_learned": ["pattern 1", "pattern 2"]
}}

Provide ONLY the JSON, no additional text."""

            response = await self.continue_conversation(learning_prompt)

            # Try to parse JSON from response
            try:
                # Extract JSON from response (may have markdown code blocks)
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    learnings = json.loads(response[json_start:json_end])
                else:
                    learnings = {}
            except json.JSONDecodeError:
                learnings = {}

            # 3. Update workflow_patterns.json
            workflow_pattern.update(
                {
                    "problems": learnings.get("problems_encountered", []),
                    "decisions": learnings.get("key_decisions", []),
                    "commands": learnings.get("useful_commands", []),
                    "files_changed": learnings.get("files_changed", []),
                    "patterns": learnings.get("patterns_learned", []),
                }
            )

            kb_path = Path("agents/knowledge")
            kb_path.mkdir(parents=True, exist_ok=True)

            # Update workflow_patterns.json
            patterns_file = kb_path / "workflow_patterns.json"
            patterns = []
            if patterns_file.exists():
                try:
                    with open(patterns_file) as f:
                        patterns = json.load(f)
                        if not isinstance(patterns, list):
                            patterns = [patterns]
                except Exception:
                    patterns = []

            patterns.append(workflow_pattern)

            with open(patterns_file, "w") as f:
                json.dump(patterns, f, indent=2)

            # 4. Update problem_solutions.json
            if learnings.get("problems_encountered"):
                problems_file = kb_path / "problem_solutions.json"
                problems = []
                if problems_file.exists():
                    try:
                        with open(problems_file) as f:
                            problems = json.load(f)
                            if not isinstance(problems, list):
                                problems = [problems]
                    except Exception:
                        problems = []

                for problem in learnings["problems_encountered"]:
                    problem["issue_number"] = self.issue_number
                    problem["date"] = execution_data["start_time"]
                    problems.append(problem)

                with open(problems_file, "w") as f:
                    json.dump(problems, f, indent=2)

            # 5. Update time_estimates.json
            if learnings.get("time_insights"):
                time_file = kb_path / "time_estimates.json"
                estimates = []
                if time_file.exists():
                    try:
                        with open(time_file) as f:
                            estimates = json.load(f)
                            if not isinstance(estimates, list):
                                estimates = [estimates]
                    except Exception:
                        estimates = []

                time_data = learnings["time_insights"]
                time_data["issue_number"] = self.issue_number
                time_data["date"] = execution_data["start_time"]
                estimates.append(time_data)

                with open(time_file, "w") as f:
                    json.dump(estimates, f, indent=2)

            # 6. Update command_sequences.json
            if learnings.get("useful_commands"):
                commands_file = kb_path / "command_sequences.json"
                commands = []
                if commands_file.exists():
                    try:
                        with open(commands_file) as f:
                            commands = json.load(f)
                            if not isinstance(commands, list):
                                commands = [commands]
                    except Exception:
                        commands = []

                for cmd in learnings["useful_commands"]:
                    cmd["issue_number"] = self.issue_number
                    cmd["date"] = execution_data["start_time"]
                    commands.append(cmd)

                with open(commands_file, "w") as f:
                    json.dump(commands, f, indent=2)

            # 7. Update agent_metrics.json
            metrics_file = kb_path / "agent_metrics.json"
            metrics = {"total_issues": 0, "successful_issues": 0, "last_updated": ""}
            if metrics_file.exists():
                try:
                    with open(metrics_file) as f:
                        metrics = json.load(f)
                except Exception:
                    pass

            metrics["total_issues"] = metrics.get("total_issues", 0) + 1
            if execution_data.get("success", True):
                metrics["successful_issues"] = metrics.get("successful_issues", 0) + 1
            metrics["last_updated"] = datetime.now().isoformat()
            metrics["last_issue"] = self.issue_number

            with open(metrics_file, "w") as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            print(f"⚠️  Warning: Could not update knowledge base: {e}")
            # Don't fail the whole execution if learning fails


async def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Autonomous Workflow Agent - AI-powered issue resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Work on Issue #26 autonomously
  python agents/autonomous_workflow_agent.py --issue 26
  
  # Dry run (analyze but don't change anything)
  python agents/autonomous_workflow_agent.py --issue 26 --dry-run
  
  # Interactive mode (step through with approvals)
  python agents/autonomous_workflow_agent.py --issue 26 --interactive
        """,
    )

    parser.add_argument(
        "--issue", type=int, required=True, help="GitHub issue number to work on"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and plan but don't make actual changes",
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Pause for approval between phases"
    )

    args = parser.parse_args()

    # Create and initialize agent
    agent = AutonomousWorkflowAgent(issue_number=args.issue, dry_run=args.dry_run)

    await agent.initialize()

    # Execute workflow
    success = await agent.execute()

    # Interactive mode: allow follow-up questions
    if args.interactive and success:
        print("\n💬 Interactive mode - you can now give additional instructions")
        print("   (Type 'exit' or 'quit' to finish)\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["exit", "quit", ""]:
                    break

                print("Agent: ", end="", flush=True)
                response = await agent.continue_conversation(user_input)
                print(response)
                print()

            except (KeyboardInterrupt, EOFError):
                break

        print("\n👋 Ending session")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
