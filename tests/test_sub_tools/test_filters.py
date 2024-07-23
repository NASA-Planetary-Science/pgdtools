"""Test the filters sub tool."""

import pandas as pd
import pytest

from pgdtools.sub_tools import filters as flt
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


def test_pgd_subtype_nan_there(pgd_head):
    """Check that NaN values are not dropped if `exclude` is set to `True`."""
    pgd_head.filter.pgd_subtype("XYZAB", exclude=True)
    assert len(pgd_head) == 100


def test_ratio(pgd_head):
    """Filter the data set based on a given isotope ratio."""
    ratio = ("C12", "C13")
    value = 98.0
    pgd_head.filter.ratio(ratio, "<", value)
    arr1 = pgd_head.db.copy(deep=True)
    assert len(arr1) < 100  # we got a good value

    # reset pgd_head
    pgd_head.reset()
    pgd_head.db = pgd_head.db.head(100)

    pgd_head.filter.ratio(ratio, ">=", value, exclude=True)
    arr2 = pgd_head.db
    pd.testing.assert_frame_equal(arr1, arr2)


def test_ratio_cmp_error(pgd_head):
    """Raise a value error if an invalid comparator was presented."""
    with pytest.raises(ValueError):
        pgd_head.filter.ratio(("C12", "C13"), "INV", 1.0)


@pytest.mark.parametrize("rat", [(2, 3, 4), "string", "st"])
def test_ratio_invalid_rat(pgd_head, rat):
    """Raise a value error if an invalid isotope ratio was presented."""
    with pytest.raises(ValueError):
        pgd_head.filter.ratio(rat, "<", 1.0)


def test_ratio_invalid_iso_name(pgd_head):
    """Raise a value error if an invalid isotope name was presented."""
    with pytest.raises(ValueError):
        pgd_head.filter.ratio(("C", "13"), "<", 1.0)


def test_ratio_isos_na(pgd_head):
    """Raise a value error if the isotope ratio is not found."""
    with pytest.raises(ValueError):
        pgd_head.filter.ratio(("C532", "C789"), "<", 1.0)


def test_reset(pgd_head):
    """Reset the pgd_head database."""
    initial_length = len(pgd_head)
    pgd_head.filter.reset()
    assert len(pgd_head) > initial_length


@pytest.mark.parametrize("cmp", ["<", "<=", ">", ">=", "==", "!="])
def test_check_comparator_default(cmp):
    """Check if the default comparator is correctly set."""
    assert flt._check_comparator(cmp) == cmp


@pytest.mark.parametrize(
    "cmps", [["=<", "<="], ["=>", ">="], ["=", "=="], ["<>", "!="], ["INV", None]]
)
def test_check_comparator_corr(cmps):
    """Check if the correct comparators are returned."""
    assert flt._check_comparator(cmps[0]) == cmps[1]
