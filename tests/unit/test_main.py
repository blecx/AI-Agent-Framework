import importlib.util
import sys
from pathlib import Path

from click.testing import CliRunner


ROOT_DIR = Path(__file__).resolve().parents[2]
TUI_DIR = ROOT_DIR / "apps" / "tui"
if str(TUI_DIR) not in sys.path:
    sys.path.insert(0, str(TUI_DIR))

spec = importlib.util.spec_from_file_location("tui_main_module", TUI_DIR / "main.py")
assert spec is not None
assert spec.loader is not None
tui_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tui_main)


def test_cli_help_includes_registered_groups():
    result = CliRunner().invoke(tui_main.cli, ["--help"])

    assert result.exit_code == 0
    assert "projects" in result.output
    assert "commands" in result.output
    assert "artifacts" in result.output
    assert "raid" in result.output
    assert "config" in result.output


def test_health_command_calls_client_and_closes(monkeypatch):
    calls = []

    class DummyClient:
        def health_check(self):
            calls.append("health")
            return {"status": "healthy"}

        def close(self):
            calls.append("close")

    monkeypatch.setattr(tui_main, "APIClient", lambda: DummyClient())
    monkeypatch.setattr(tui_main, "print_success", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(tui_main, "print_json", lambda *_args, **_kwargs: None)

    result = CliRunner().invoke(tui_main.cli, ["health"])

    assert result.exit_code == 0
    assert calls == ["health", "close"]
