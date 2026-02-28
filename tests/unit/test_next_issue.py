import importlib.util
from pathlib import Path


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _KnowledgeStub:
    def get_adjusted_estimate(self, estimated_hours: float) -> float:
        return estimated_hours


class _GitHubStub:
    def __init__(self, open_issues):
        self._open_issues = open_issues
        self.verbose = False

    def get_open_issues(self, limit: int = 200):
        return self._open_issues[:limit]

    def is_issue_resolved(self, issue_number: int) -> bool:
        return True


def test_selector_uses_live_open_issues_beyond_legacy_range(tmp_path):
    script_path = Path("scripts/next-issue.py").resolve()
    mod = _load_module(script_path, "next_issue_script")

    tracking_file = tmp_path / "tracking.md"
    tracking_file.write_text("# empty", encoding="utf-8")

    open_issues = [
        {
            "number": 595,
            "title": "Step 6 issue",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        }
    ]

    selector = mod.IssueSelector(tracking_file, _KnowledgeStub(), _GitHubStub(open_issues))
    assert len(selector.issues) == 1
    assert selector.issues[0]["number"] == 595
    assert selector.issues[0]["state"] == "Open"


def test_selector_orders_live_open_issues_by_priority_then_number(tmp_path):
    script_path = Path("scripts/next-issue.py").resolve()
    mod = _load_module(script_path, "next_issue_script_order")

    tracking_file = tmp_path / "tracking.md"
    tracking_file.write_text("# empty", encoding="utf-8")

    open_issues = [
        {
            "number": 596,
            "title": "Step 6 second",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
        {
            "number": 595,
            "title": "Step 6 first",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
    ]

    selector = mod.IssueSelector(tracking_file, _KnowledgeStub(), _GitHubStub(open_issues))
    selected = selector.select_next_issue()

    assert selected is not None
    assert selected["number"] == 595
