"""Test the techniques sub tool."""

import pytest

from pgdtools.sub_tools import Techniques


# DUNDER METHODS #


def test_init_type_error():
    """Raise type error if parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = Techniques("test")


def test_full_db(pgd):
    """Just get a dictionary with all techniques."""
    _ = pgd.technique.dict


def test_repr(pgd_head):
    """Check string representation of class prints IDs."""
    tech = pgd_head.technique
    assert isinstance(str(tech), str)
    for key in tech.dict:
        assert key in str(tech)


def test_eq(pgd, pgd_head):
    """Check for equality between two reference sets."""
    pgd.db = pgd.db.head(100)
    assert pgd_head.technique == pgd.technique


def test_len(pgd_head):
    """Get number of unique references."""
    assert len(pgd_head.technique) == len(pgd_head.technique.dict)


def test_iter(pgd_head):
    """Iterate over the key, value pairs."""
    tech = pgd_head.technique
    for key, value in tech:
        assert key in tech.dict.keys()
        assert value in tech.dict.values()


def test_getitem(pgd_head):
    """Get a reference item based on the key."""
    tech = pgd_head.technique
    for key in tech.dict:
        assert tech[key] == tech.dict[key]


# # METHODS #


def test_dict(pgd_head):
    """Return a dictionary representation of the class."""
    tech = pgd_head.technique

    assert len(tech.dict) == len(tech.table_set)
    for key in tech.table_set.index:
        assert key in tech.dict


def test_table_full(pgd_head):
    """Get reference for a grain ID as a pandas Series"""
    assert pgd_head.technique.table_full.shape[0] >= 100
    assert pgd_head.technique.table_full.shape[1] == 6


def test_table_set(pgd_head):
    """Get reference for some grains as a Set."""
    result = pgd_head.technique.table_set
    assert result.shape[0] < 100
    assert result.shape[1] == 5
