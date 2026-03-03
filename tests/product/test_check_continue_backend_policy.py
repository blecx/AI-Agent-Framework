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


def test_continue_backend_policy_checker_passes_with_required_snippets(tmp_path: Path):
    script_path = Path("scripts/check_continue_backend_policy.py").resolve()
    mod = _load_module("check_continue_backend_policy_ok", script_path)

    backend_loop = tmp_path / "continue-backend.sh"
    backend_loop.write_text(
        "\n".join(
            [
                "MAX_ISSUES=25",
                "MAX_ISSUES_CAP=25",
                'if [[ "$MAX_ISSUES" -lt "$MAX_ISSUES_CAP" ]]',
                'if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]',
                "Override baseline and continue",
            ]
        ),
        encoding="utf-8",
    )

    phase3_loop = tmp_path / "continue-phase-3.sh"
    phase3_loop.write_text(backend_loop.read_text(encoding="utf-8"), encoding="utf-8")

    prompt_file = tmp_path / "continue-backend.md"
    prompt_file.write_text("Default run limit is `25` issues", encoding="utf-8")

    module_file = tmp_path / "continue-backend-workflow.md"
    module_file.write_text("Default `max-issues` per run is `25`", encoding="utf-8")

    mod.BACKEND_LOOP_SCRIPT = backend_loop
    mod.PHASE3_LOOP_SCRIPT = phase3_loop
    mod.PROMPT_FILE = prompt_file
    mod.MODULE_FILE = module_file

    assert mod.main() == 0


def test_continue_backend_policy_checker_fails_when_snippet_missing(tmp_path: Path):
    script_path = Path("scripts/check_continue_backend_policy.py").resolve()
    mod = _load_module("check_continue_backend_policy_missing", script_path)

    backend_loop = tmp_path / "continue-backend.sh"
    backend_loop.write_text("MAX_ISSUES=25\nMAX_ISSUES_CAP=25", encoding="utf-8")

    phase3_loop = tmp_path / "continue-phase-3.sh"
    phase3_loop.write_text("MAX_ISSUES=25\nMAX_ISSUES_CAP=25", encoding="utf-8")

    mod.BACKEND_LOOP_SCRIPT = backend_loop
    mod.PHASE3_LOOP_SCRIPT = phase3_loop

    assert mod.main() == 1
