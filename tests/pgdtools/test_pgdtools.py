"""Functional tests for the PGD tools."""

import pytest
import numpy as np


# TESTS FOR PRESOLAR GRAINS CLASS #


@pytest.mark.parametrize(
    "corrs", [[["Si30", "Si29"], "rho[30Si-29Si]"], [["Fe54", "Ni67"], None]]
)
def test_pg_header_correlation(pgd, corrs):
    """Test header correlation."""
    isos, expected = corrs
    received = pgd.header_correlation(*isos)
    assert received == expected


@pytest.mark.parametrize(
    "headers",
    [
        [("C12", "C13"), ("12C/13C", ("err+[12C/13C]", "err-[12C/13C]"), False)],
        [("29Si", "28Si"), ("d(29Si/28Si)", "err[d(29Si/28Si)]", True)],
        [("29Si", "30Si"), None],
    ],
)
def test_pg_header_ratio(pgd, headers):
    """Test header ratio."""
    isos, expected = headers
    received = pgd.header_ratio(*isos)
    assert received == expected


# TESTS FOR GRAINS SUBCLASS #


def test_pg_grain_pgd_type_single_id(pgd):
    """Test grain type."""
    id = "SiC-1992-VIR-000026"
    grain = pgd.grain[id]
    assert grain.pgd_type == ("M", None)


def test_pg_grain_probabilities_single_id(pgd):
    """Probabilities for a given grain."""
    id = "SiC-1996-HOP-200030"
    grain = pgd.grain[id]

    probs_expected = {
        "M": 0.765,
        "X": 0.103,
        "Y": 0.05,
        "Z": 0,
        "AB": 0.001,
        "C": 0,
        "D": 0,
        "N": 0,
    }

    assert grain.probabilities == probs_expected


def test_pg_grain_reference_single_id(pgd):
    """Test reference for a given grain."""
    id = "SiC-1992-VIR-000026"
    ref_expected = "Virag et al. (1992) GCA 56:1715"
    grain = pgd.grain[id]
    assert grain.reference == ref_expected


def test_pg_grain_reference_multi_ids(pgd):
    """Test references for multiple grains."""
    ids = ["SiC-1992-VIR-000026", "SiC-1993-ALE-000047"]
    refs_expected = np.array(
        [
            "Virag et al. (1992) GCA 56:1715",
            "Alexander (1993) GCA 57:2869",
        ]
    )
    grains = pgd.grain[ids]
    np.testing.assert_equal(grains.reference.values, refs_expected)


def test_pg_grain_source_single_id(pgd):
    """Test source of a grain for one given grain."""
    id = "SiC-1992-VIR-000026"
    src_exp = "Murchison"
    grain = pgd.grain[id]
    assert grain.source == src_exp
