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


def test_prmerge_policy_checker_passes_with_required_snippets(tmp_path: Path):
    script_path = Path("scripts/check_prmerge_policy.py").resolve()
    mod = _load_module("check_prmerge_policy_ok", script_path)

    prmerge_file = tmp_path / "prmerge"
    prmerge_file.write_text(
        "\n".join(mod.REQUIRED_SNIPPETS),
        encoding="utf-8",
    )

    mod.PRMERGE_SCRIPT = prmerge_file

    assert mod.main() == 0


def test_prmerge_policy_checker_fails_when_snippet_missing(tmp_path: Path):
    script_path = Path("scripts/check_prmerge_policy.py").resolve()
    mod = _load_module("check_prmerge_policy_missing", script_path)

    prmerge_file = tmp_path / "prmerge"
    prmerge_file.write_text(
        "\n".join(mod.REQUIRED_SNIPPETS[:-1]),
        encoding="utf-8",
    )

    mod.PRMERGE_SCRIPT = prmerge_file

    assert mod.main() == 1
