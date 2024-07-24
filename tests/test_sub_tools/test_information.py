"""Functional tests for the information sub tools."""

import pytest

import pgdtools
import pgdtools.sub_tools.info


def test_info_type_error():
    """Raise a type error if the parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = pgdtools.sub_tools.info.Info("test")


# PROPERTIES #


def test_dbs(pgd):
    """Get available databases."""
    dbs = pgd.info.dbs
    for en in pgdtools.PresolarGrains.DataBase:
        assert en in dbs


def test_number_of_grains(pgd_head):
    """Get number of grains in current database."""
    assert pgd_head.info.number_of_grains == 100


def test_pgd_types(pgd):
    """Get a set of the PGD types that are available."""
    types_exp = ["X", "AB"]
    pgd.filter.pgd_type(types_exp)
    assert pgd.info.pgd_types == set(types_exp)


# METHODS #


def test_correlations(pgd_head):
    """Get correlations for elements or isotopes."""
    assert len(pgd_head.info.correlations("Mo")) > 1

    si_correlation_exp = ["rho[30Si-29Si]"]
    inp_options = ["si", "si-29", "30-si"]
    for inp in inp_options:
        assert pgd_head.info.correlations(inp) == si_correlation_exp


def test_correlations_none(pgd_head):
    """Get None if no correlation available for a given element or isotope."""
    assert pgd_head.info.correlations("XYZ") is None


def test_ratio(pgd_head):
    """Get isotope ratio and delta information."""
    assert pgd_head.info.ratios("Si") == [
        ("d(29Si/28Si)", True),
        ("d(30Si/28Si)", True),
    ]

    assert pgd_head.info.ratios("29Si") == [("d(29Si/28Si)", True)]


def test_ratio_none(pgd_head):
    """Return None if ratios were not found."""
    assert pgd_head.info.ratios("275C") is None
