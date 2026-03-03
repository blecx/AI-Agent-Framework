import importlib.util
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


def test_publish_issues_dry_run_and_mapping_existing(tmp_path: Path, monkeypatch):
    script_path = Path("scripts/publish_issues.py").resolve()
    mod = _load_module("publish_issues", script_path)

    spec_file = tmp_path / "issues.yml"
    spec_file.write_text(
        """
AI-Agent-Framework:
  - id: BE-1
    title: Example backend issue
    labels: [backend/api, size:S]
    body: |
      ## Goal / Problem Statement
      Goal

      ## Scope
      ### In Scope
      - A
      ### Out of Scope
      - B
      ### Dependencies
      - None

      ## Acceptance Criteria
      - [ ] done

      ## Technical Approach
      - steps

      ## Testing Requirements
      - `pytest -q`

      ## Documentation Updates
      - [ ] docs

      ## Cross-Repository Coordination
      No
""",
        encoding="utf-8",
    )

    specs = mod._load_specs([spec_file])
    assert len(specs) == 1
    assert specs[0].source_id == "BE-1"

    # Duplicate exists in GitHub -> should map as existing even in dry mode
    monkeypatch.setattr(
        mod,
        "_find_existing_by_title",
        lambda repo, title: {
            "number": 999,
            "title": title,
            "url": f"https://example.com/{repo}/999",
        },
    )

    mapping = {"version": 1, "entries": {}}
    logs, out = mod.publish(specs, mapping, apply=False, repo_filter=None)

    assert any("MAP existing" in line for line in logs)
    assert "blecx/AI-Agent-Framework|BE-1" in out["entries"]
    assert out["entries"]["blecx/AI-Agent-Framework|BE-1"]["issue_number"] == 999


def test_publish_issues_apply_creates_issue(tmp_path: Path, monkeypatch):
    script_path = Path("scripts/publish_issues.py").resolve()
    mod = _load_module("publish_issues_apply", script_path)

    spec_file = tmp_path / "issues.yml"
    spec_file.write_text(
        """
AI-Agent-Framework-Client:
  - number: UX-1
    title: Example client issue
    labels: [webui/ux, size:S]
    body: |
      ## Goal / Problem Statement
      Goal

      ## Scope
      ### In Scope
      - A
      ### Out of Scope
      - B
      ### Dependencies
      - None

      ## Acceptance Criteria
      - [ ] done

      ## Technical Approach
      - steps

      ## Testing Requirements
      - `npm run test`

      ## Documentation Updates
      - [ ] docs

      ## Cross-Repository Coordination
      Yes
""",
        encoding="utf-8",
    )

    specs = mod._load_specs([spec_file])
    monkeypatch.setattr(mod, "_find_existing_by_title", lambda repo, title: None)
    monkeypatch.setattr(
        mod,
        "_create_issue",
        lambda spec: (
            123,
            "https://github.com/blecx/AI-Agent-Framework-Client/issues/123",
        ),
    )

    mapping = {"version": 1, "entries": {}}
    logs, out = mod.publish(specs, mapping, apply=True, repo_filter=None)

    assert any("CREATED" in line for line in logs)
    key = "blecx/AI-Agent-Framework-Client|UX-1"
    assert out["entries"][key]["issue_number"] == 123
