"""Fixtures for the ``test_database`` module tests."""

from pathlib import Path

import pytest


@pytest.fixture()
def curr_path(request) -> Path:
    """Return the current path for file path stitching."""
    return Path(request.fspath).parents[0]
