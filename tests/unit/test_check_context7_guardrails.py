import importlib.util
import json
import sys
from pathlib import Path


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_context7_guardrails_pass_with_required_snippets(tmp_path: Path):
    script_path = Path("scripts/check_context7_guardrails.py").resolve()
    mod = _load_module("check_context7_guardrails_ok", script_path)

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "mcp": {
                    "servers": {
                        "context7": {
                            "url": "http://127.0.0.1:3010/mcp",
                            "headers": {
                                "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}",
                            },
                        },
                        "bashGateway": {
                            "url": "http://127.0.0.1:3011/mcp",
                        },
                        "git": {
                            "url": "http://127.0.0.1:3012/mcp",
                        },
                        "search": {
                            "url": "http://127.0.0.1:3013/mcp",
                        },
                        "filesystem": {
                            "url": "http://127.0.0.1:3014/mcp",
                        },
                        "dockerCompose": {
                            "url": "http://127.0.0.1:3015/mcp",
                        },
                        "testRunner": {
                            "url": "http://127.0.0.1:3016/mcp",
                        },
                        "offlineDocs": {
                            "url": "http://127.0.0.1:3017/mcp",
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    baseline_file = tmp_path / "prompt-quality-baseline.md"
    baseline_file.write_text(
        "Context7 external API guidance\nMCP Tool Arbitration Hard Rules\nPrompts must treat these as hard rules",
        encoding="utf-8",
    )

    create_file = tmp_path / "create-issue.md"
    create_file.write_text(
        "Context7 docs-grounding MCP Tool Arbitration Hard Rules",
        encoding="utf-8",
    )

    resolve_file = tmp_path / "resolve-issue-dev.md"
    resolve_file.write_text(
        "Context7 external API MCP Tool Arbitration Hard Rules",
        encoding="utf-8",
    )

    mod.SETTINGS_FILE = settings_file
    mod.PROMPT_BASELINE_FILE = baseline_file
    mod.CREATE_ISSUE_PROMPT = create_file
    mod.RESOLVE_ISSUE_PROMPT = resolve_file

    assert mod.main() == 0


def test_context7_guardrails_fail_when_context7_missing(tmp_path: Path):
    script_path = Path("scripts/check_context7_guardrails.py").resolve()
    mod = _load_module("check_context7_guardrails_missing", script_path)

    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"mcp": {"servers": {}}}), encoding="utf-8")

    baseline_file = tmp_path / "prompt-quality-baseline.md"
    baseline_file.write_text("no guardrail text", encoding="utf-8")

    create_file = tmp_path / "create-issue.md"
    create_file.write_text("no guardrail text", encoding="utf-8")

    resolve_file = tmp_path / "resolve-issue-dev.md"
    resolve_file.write_text("no guardrail text", encoding="utf-8")

    mod.SETTINGS_FILE = settings_file
    mod.PROMPT_BASELINE_FILE = baseline_file
    mod.CREATE_ISSUE_PROMPT = create_file
    mod.RESOLVE_ISSUE_PROMPT = resolve_file

    assert mod.main() == 1
