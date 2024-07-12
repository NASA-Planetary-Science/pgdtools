"""Test the references sub tool."""

import pytest

from pgdtools.sub_tools import References


def test_type_error():
    """Raise type error if parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = References("test")


def test_dict(pgd_head):
    """Return a dictionary representation of the class."""
    ref = pgd_head.reference

    assert len(ref.dict) == len(ref.table_set)
    for key in ref.table_set.index:
        assert key in ref.dict


def test_doi(pgd_head):
    """Return a set of DOIs for the references."""
    ref = pgd_head.reference
    assert isinstance(ref.doi, set)


def test_str(pgd_head):
    """Check string representation of class prints IDs."""
    ref = pgd_head.reference
    assert isinstance(str(ref), str)
    for key in ref.dict:
        assert key in str(ref)


def test_table_full(pgd_head):
    """Get reference for a grain ID as a pandas Series"""
    assert pgd_head.reference.table_full.shape == (100, 5)


def test_table_set(pgd_head):
    """Get reference for some grains as a Set."""
    result = pgd_head.reference.table_set
    assert result.shape[0] < 100
    assert result.shape[1] == 5
