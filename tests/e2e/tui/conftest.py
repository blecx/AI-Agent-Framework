"""Pytest configuration for TUI E2E tests."""

import sys
from pathlib import Path

# Add tests directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import fixtures to make them available to all tests
from fixtures.fixtures import *  # noqa: F401, F403, E402
