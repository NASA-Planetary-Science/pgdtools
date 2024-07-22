"""Test the filters sub tool."""

import pytest

from pgdtools.sub_tools import Filters


# DUNDER METHODS #


def test_init_type_error():
    """Raise type error if parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = Filters("test")


# METHODS #


@pytest.mark.parametrize(
    "ids",
    [
        ["SiC-2005-NIT-000924", "SiC-2005-NIT-000925", "SiC-2005-NIT-000926"],
        "SiC-2005-NIT-000001",
    ],
)
def test_pgd_id(pgd, ids):
    """Filter the data set based on PGD IDs."""
    id_list = [ids] if isinstance(ids, str) else ids

    pgd.filter.pgd_id(ids)

    assert len(pgd) == len(id_list)
    assert pgd.db.index.tolist() == id_list

    pgd.filter.pgd_id(ids, exclude=True)
    assert len(pgd) == 0


@pytest.mark.parametrize("tp", ["X", ["X", "C"]])
def test_pgd_type(pgd, tp):
    """Filter for a given PGD type or types."""
    pgd.filter.pgd_type(tp)

    tp_list = [tp] if isinstance(tp, str) else tp

    unique_series = pgd.db["PGD Type"].unique()
    assert len(pgd.db["PGD Type"].unique()) == len(tp_list)
    assert all([tp in unique_series for tp in tp_list])

    # filter for exclusion
    pgd.filter.pgd_type(tp, exclude=True)
    assert len(pgd) == 0


@pytest.mark.parametrize("st", ["AB1", ["AB1", "X2"]])
def test_pgd_subtype(pgd, st):
    """Filter for a given PGD subtype or subtypes."""
    pgd.filter.pgd_subtype(st)

    st_list = [st] if isinstance(st, str) else st

    unique_series = pgd.db["PGD Subtype"].unique()
    assert len(pgd.db["PGD Subtype"].unique()) == len(st_list)
    assert all([st in unique_series for st in st_list])

    # filter for exclusion
    pgd.filter.pgd_subtype(st, exclude=True)
    assert len(pgd) == 0


def test_reset(pgd_head):
    """Reset the pgd_head database."""
    initial_length = len(pgd_head)
    pgd_head.filter.reset()
    assert len(pgd_head) > initial_length
