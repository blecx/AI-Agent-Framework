import os
import subprocess
import time
from typing import Optional, Sequence


_LAST_GH_CALL_TS: Optional[float] = None


def _resolve_min_interval_seconds(override: Optional[int]) -> int:
    if override is not None:
        return int(override)
    return int(os.environ.get("GH_MIN_INTERVAL_SECONDS", "3") or "3")


def run_gh_throttled(
    args: Sequence[str],
    *,
    min_interval_seconds: Optional[int] = None,
    **subprocess_kwargs,
) -> subprocess.CompletedProcess[str]:
    """Run a `gh ...` command with a minimum interval between invocations.

    This helps avoid secondary GitHub API rate limits when automation issues many
    `gh` subprocess calls in a tight loop.

    Configuration:
    - `GH_MIN_INTERVAL_SECONDS` (default: 1)
    - Or pass `min_interval_seconds` explicitly.
    """

    global _LAST_GH_CALL_TS

    interval = _resolve_min_interval_seconds(min_interval_seconds)
    if interval > 0 and _LAST_GH_CALL_TS is not None:
        elapsed = time.monotonic() - _LAST_GH_CALL_TS
        remaining = interval - elapsed
        if remaining > 0:
            time.sleep(remaining)

    _LAST_GH_CALL_TS = time.monotonic()

    return subprocess.run(  # noqa: S603 (controlled internal CLI invocation)
        list(args),
        **subprocess_kwargs,
    )
