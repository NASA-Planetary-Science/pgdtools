"""Test the references sub tool."""

import pytest

from pgdtools.sub_tools import References


# DUNDER METHODS #


def test_init_type_error():
    """Raise type error if parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = References("test")


def test_repr(pgd_head):
    """Check string representation of class prints IDs."""
    ref = pgd_head.reference
    assert isinstance(str(ref), str)
    for key in ref.dict:
        assert key in str(ref)


def test_eq(pgd, pgd_head):
    """Check for equality between two reference sets."""
    pgd.db = pgd.db.head(100)
    assert pgd_head.reference == pgd.reference


def test_len(pgd_head):
    """Get number of unique references."""
    assert len(pgd_head.reference) == len(pgd_head.reference.dict)


def test_iter(pgd_head):
    """Iterate over the key, value pairs."""
    ref = pgd_head.reference
    for key, value in ref:
        assert key in ref.dict.keys()
        assert value in ref.dict.values()


def test_getitem(pgd_head):
    """Get a reference item based on the key."""
    ref = pgd_head.reference
    for key in ref.dict:
        assert ref[key] == ref.dict[key]


# METHODS #


def test_dict(pgd_head):
    """Return a dictionary representation of the class."""
    ref = pgd_head.reference

    assert len(ref.dict) == len(ref.table_set)
    for key in ref.table_set.index:
        assert key in ref.dict


def test_doi(pgd_head):
    """Return a set of DOIs for the references."""
    ref = pgd_head.reference
    doi_direct = pgd_head.reference.doi
    assert isinstance(ref.doi, set)
    assert ref.doi == doi_direct


@pytest.mark.parametrize(
    "ref",
    [
        [
            "hECK",
            [
                "Heck et al. (2009) ApJ 701:1415",
                "Meier et al. (2012) GCA 76:147",
                "Heck et al. (2018) MAPS 53:2327",
            ],
        ]
    ],
)
def test_reference_graphite_db(pgd, ref):
    """Search for references."""
    search_str, ref_exp = ref
    ref_exp.sort()

    pgd.filter.db(pgd.DataBase.Graphite)
    assert pgd.reference.search(search_str) == ref_exp


def test_table_full(pgd_head):
    """Get reference for a grain ID as a pandas Series"""
    assert pgd_head.reference.table_full.shape == (100, 5)


def test_table_set(pgd_head):
    """Get reference for some grains as a Set."""
    result = pgd_head.reference.table_set
    assert result.shape[0] < 100
    assert result.shape[1] == 5
