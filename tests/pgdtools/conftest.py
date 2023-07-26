"""Configuration for pytest."""

import pytest

from pgdtools import PresolarGrains


@pytest.fixture(scope="session")
def pgd():
    """Fixture for the PGD database."""
    pgd = PresolarGrains()
    yield pgd
    pgd.reset()
