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


class _GitHubBlockerStub(_GitHubStub):
    def __init__(self, open_issues, resolved_issue_numbers):
        super().__init__(open_issues)
        self._resolved_issue_numbers = set(resolved_issue_numbers)

    def is_issue_resolved(self, issue_number: int) -> bool:
        return issue_number in self._resolved_issue_numbers


def _create_selector(tmp_path, open_issues, tracking_text: str = "# empty", github=None):
    script_path = Path("scripts/next-issue.py").resolve()
    mod = _load_module(script_path, f"next_issue_script_{id(open_issues)}")

    tracking_file = tmp_path / "tracking.md"
    tracking_file.write_text(tracking_text, encoding="utf-8")

    if github is None:
        github = _GitHubStub(open_issues)

    selector = mod.IssueSelector(tracking_file, _KnowledgeStub(), github)
    return selector


def test_selector_uses_live_open_issues_beyond_legacy_range(tmp_path):
    open_issues = [
        {
            "number": 595,
            "title": "Step 6 issue",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        }
    ]

    selector = _create_selector(tmp_path, open_issues)
    assert len(selector.issues) == 1
    assert selector.issues[0]["number"] == 595
    assert selector.issues[0]["state"] == "Open"


def test_selector_orders_live_open_issues_by_priority_then_number(tmp_path):
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

    selector = _create_selector(tmp_path, open_issues)
    selected = selector.select_next_issue()

    assert selected is not None
    assert selected["number"] == 595, (
        "policy violation: with equal priority, selector must choose lowest issue number"
    )


def test_selector_skips_blocked_issue_and_selects_next_ready(tmp_path):
    open_issues = [
        {
            "number": 30,
            "title": "Blocked by #595",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
        {
            "number": 31,
            "title": "Ready issue",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
    ]
    tracking_text = """### Issue #30: blocked
Blockers: #24
Estimated: 4.0

### Issue #31: ready
Blockers: none
Estimated: 4.0
"""

    github = _GitHubBlockerStub(open_issues, resolved_issue_numbers=set())
    selector = _create_selector(tmp_path, open_issues, tracking_text=tracking_text, github=github)
    selected = selector.select_next_issue()

    assert selected is not None
    assert selected["number"] == 31, (
        "policy violation: blocked issues must not be selected when a ready issue exists"
    )


def test_selector_returns_none_when_all_open_issues_are_blocked(tmp_path):
    open_issues = [
        {
            "number": 30,
            "title": "Blocked A",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
        {
            "number": 31,
            "title": "Blocked B",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
    ]
    tracking_text = """### Issue #30: blocked
Blockers: #24
Estimated: 4.0

### Issue #31: blocked
Blockers: #25
Estimated: 4.0
"""

    github = _GitHubBlockerStub(open_issues, resolved_issue_numbers=set())
    selector = _create_selector(tmp_path, open_issues, tracking_text=tracking_text, github=github)
    selected = selector.select_next_issue()

    assert selected is None, "policy violation: selector must return None when every open issue is blocked"


def test_selector_prefers_higher_priority_over_lower_issue_number(tmp_path):
    open_issues = [
        {
            "number": 24,
            "title": "Low-number medium issue",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
        {
            "number": 29,
            "title": "High-priority issue",
            "state": "OPEN",
            "labels": [],
            "closedAt": None,
        },
    ]
    tracking_text = """### Issue #24: medium
Priority: Medium
Blockers: none
Estimated: 4.0

### Issue #29: high
Priority: High
Blockers: none
Estimated: 4.0
"""

    selector = _create_selector(tmp_path, open_issues, tracking_text=tracking_text)
    selected = selector.select_next_issue()

    assert selected is not None
    assert selected["number"] == 29, (
        "policy violation: selector must prioritize High over Medium regardless of issue number"
    )
