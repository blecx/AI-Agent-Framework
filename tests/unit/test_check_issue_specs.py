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


def test_issue_spec_validator_accepts_canonical(tmp_path: Path):
    script_path = Path("scripts/check_issue_specs.py").resolve()
    mod = _load_module("check_issue_specs", script_path)

    content = """
AI-Agent-Framework:
  - id: BE-1
    title: Example issue
    labels: [backend/api, size:S]
    size_estimate: S
    body: |
      ## Goal / Problem Statement
      Goal.

      ## Scope
      ### In Scope
      - Item
      ### Out of Scope
      - None
      ### Dependencies
      - None

      ## Acceptance Criteria
      - [ ] Done

      ## Technical Approach
      - Steps

      ## Testing Requirements
      - `pytest tests/unit -q`

      ## Documentation Updates
      - [ ] docs

      ## Cross-Repository Coordination
      No
"""
    spec_file = tmp_path / "spec.yml"
    spec_file.write_text(content, encoding="utf-8")

    findings = mod.validate_file(spec_file, allow_legacy=False)
    assert findings == []


def test_issue_spec_validator_flags_missing_fields(tmp_path: Path):
    script_path = Path("scripts/check_issue_specs.py").resolve()
    mod = _load_module("check_issue_specs_missing", script_path)

    content = """
AI-Agent-Framework:
  - labels: [backend/api]
    body: |
      ## Goal / Problem Statement
      Missing title and id.
"""
    spec_file = tmp_path / "bad.yml"
    spec_file.write_text(content, encoding="utf-8")

    findings = mod.validate_file(spec_file, allow_legacy=False)
    messages = "\n".join(str(f) for f in findings)
    assert "missing non-empty title" in messages
    assert "missing stable source ID" in messages
