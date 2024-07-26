"""Test the filters sub tool."""

import pandas as pd
import pytest

from pgdtools import PresolarGrains
from pgdtools.sub_tools import filters as flt
from pgdtools.sub_tools import Filters


# DUNDER METHODS #


def test_init_type_error():
    """Raise type error if parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = Filters("test")


# METHODS #


@pytest.mark.parametrize(
    "dbs",
    [
        PresolarGrains.DataBase.SiC,
        PresolarGrains.DataBase.Graphite,
        [PresolarGrains.DataBase.SiC, PresolarGrains.DataBase.Graphite],
    ],
)
@pytest.mark.parametrize("exclude", [True, False])
def test_db(pgd, dbs, exclude):
    """Filter out a specific the database is correctly set."""
    pgd.filter.db(dbs, exclude=exclude)

    if not isinstance(dbs, list):
        dbs = [dbs]

    for db in dbs:
        if exclude:
            any(~pgd.db.index.to_series().apply(lambda x: x.startswith(db.value)))
        else:
            any(pgd.db.index.to_series().apply(lambda x: x.startswith(db.value)))


def test_db_type_error(pgd):
    """Raise a type error if the database is not of type PresolarGrains.DataBase."""
    with pytest.raises(TypeError):
        pgd.filter.db("SiC")


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


@pytest.mark.parametrize("rat", [(2, 3, 4), ("C12", "C13", "c14"), "string", "st"])
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


def test_reference(pgd_head):
    """Filter the data based on references."""
    ref = "Amari (1992) unpublished"  # in head data
    pgd_head.filter.reference(ref)
    assert len(pgd_head) > 0


def test_reference_none_left(pgd_head):
    """Filter references until none are left."""
    ref = "This will never be a correct reference."
    pgd_head.filter.reference(ref)
    assert len(pgd_head) == 0


def test_reset(pgd_head):
    """Reset the pgd_head database."""
    initial_length = len(pgd_head)
    pgd_head.filter.reset()
    assert len(pgd_head) > initial_length


def test_uncertainty_carbon(pgd):
    """Filter on carbon uncertainty of a ratio measurement symmetric and asymmetric."""
    isos = ("C12", "C13")
    comparator = "<"

    pgd_id_sic = "SiC-1996-HOP-200183"  # 12C/13C unc: 0.8
    pgd_id_gra = "Gra-1995-HOP-000004"  # 12C/13C unc: +2.34, -2.07

    pgd.filter.uncertainty(isos, comparator, 1.0)
    assert pgd_id_sic not in pgd.db.index
    assert pgd_id_gra in pgd.db.index

    pgd.filter.reset()

    pgd.filter.uncertainty(isos, comparator, 2.0, exclude=True)
    assert pgd_id_sic in pgd.db.index
    assert pgd_id_gra not in pgd.db.index

    pgd.filter.reset()
    pgd.filter.uncertainty(isos, comparator, 2.3)
    assert pgd_id_sic not in pgd.db.index
    assert pgd_id_gra in pgd.db.index

    pgd.filter.reset()
    pgd.filter.uncertainty(isos, comparator, 2.5)
    assert pgd_id_sic in pgd.db.index
    assert pgd_id_gra in pgd.db.index

    pgd.filter.reset()
    pgd.filter.uncertainty(isos, comparator, 2.3, exclude=True)
    assert pgd_id_sic not in pgd.db.index
    assert pgd_id_gra not in pgd.db.index


def test_uncertainty_silicon(pgd):
    """Filter on silicon uncertainty of a ratio measurement."""
    isos = ("29Si", "28Si")
    comparator = "<"

    pgd_id_sic = "SiC-1996-NIT-100009"  # d(29Si/28Si) unc: 5.3
    pgd_id_gra = "Gra-1995-HOP-000073"  # d(29Si/28Si) unc: 37.35

    pgd.filter.uncertainty(isos, comparator, 5.0)
    assert pgd_id_sic not in pgd.db.index
    assert pgd_id_gra not in pgd.db.index

    pgd.filter.reset()
    pgd.filter.uncertainty(isos, comparator, 5.5)
    assert pgd_id_sic in pgd.db.index
    assert pgd_id_gra not in pgd.db.index

    pgd.filter.reset()
    pgd.filter.uncertainty(isos, comparator, 37.0, exclude=True)
    assert pgd_id_sic not in pgd.db.index
    assert pgd_id_gra in pgd.db.index


@pytest.mark.parametrize("unc", [(2, 3, 4), "string", "st"])
def test_uncertainty_invalid_rat(pgd_head, unc):
    """Raise a value error if an invalid isotope ratio was presented."""
    with pytest.raises(ValueError):
        pgd_head.filter.uncertainty(unc, "<", 1.0)


def test_uncertainty_invalid_iso_name(pgd_head):
    """Raise a value error if an invalid isotope name was presented."""
    with pytest.raises(ValueError):
        pgd_head.filter.uncertainty(("C", "13"), "<", 1.0)


def test_uncertainty_isos_na(pgd_head):
    """Raise a value error if the isotope ratio is not found."""
    with pytest.raises(ValueError):
        pgd_head.filter.uncertainty(("C532", "C789"), "<", 1.0)


@pytest.mark.parametrize("cmp", ["<", "<=", ">", ">=", "==", "!="])
def test_check_comparator_default(cmp):
    """Check if the default comparator is correctly set."""
    assert flt._check_comparator(cmp) == cmp


@pytest.mark.parametrize(
    "cmps", [["=<", "<="], ["=>", ">="], ["=", "=="], ["<>", "!="]]
)
def test_check_comparator_corr(cmps):
    """Check if the correct comparators are returned."""
    assert flt._check_comparator(cmps[0]) == cmps[1]


def test_check_comparator_invalid():
    """Check if an invalid comparator raises a ValueError."""
    with pytest.raises(ValueError):
        flt._check_comparator("INV")
