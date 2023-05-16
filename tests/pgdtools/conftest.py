"""Configuration for pytest."""

from pgdtools import PresolarGrains

import pytest


@pytest.fixture(scope="session")
def pgd():
    """Fixture for the PGD database."""
    pgd = PresolarGrains()
    yield pgd
    pgd.reset()
