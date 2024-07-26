"""Functional tests for the headers sub tools."""

import pytest

import pgdtools.sub_tools.headers


def test_search_header_type_error(pgd):
    """Raise a type error if the parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = pgdtools.sub_tools.headers.Headers("test", "a", "b")


@pytest.mark.parametrize(
    "isos",
    [[("C12", "C13"), ("12C/13C", False)], [("Si29", "Si28"), ("d(29Si/28Si)", True)]],
)
def test_ratio(pgd, isos):
    """Search the header for an isotope ratio and if it's a delta value."""
    iso1, iso2 = isos[0]
    hdr_exp = isos[1]

    assert pgd._header(iso1, iso2).ratio == hdr_exp


def test_ratio_not_found(pgd):
    """Raise ValueError if the header is not found."""
    with pytest.raises(ValueError):
        pgd._header("C532", "C789").ratio


@pytest.mark.parametrize(
    "isos",
    [
        [("7Li", "6Li"), ["err[7Li/6Li]", None, None]],
        [("C12", "C13"), ["err[12C/13C]", "err+[12C/13C]", "err-[12C/13C]"]],
        [("N14", "N15"), ["err[14N/15N]", "err+[14N/15N]", "err-[14N/15N]"]],
        [("Si29", "Si28"), ["err[d(29Si/28Si)]", None, None]],
    ],
)
def test_uncertainty(pgd, isos):
    """Search the header for the uncertainty of an isotope ratio."""
    iso1, iso2 = isos[0]
    hdr_exp = isos[1]

    assert pgd._header(iso1, iso2).uncertainty == hdr_exp


@pytest.mark.parametrize(
    "isos",
    [
        [("C12", "C13"), None],
        [("Si30", "Si29"), "rho[30Si-29Si]"],
    ],
)
def test_rho(pgd, isos):
    """Search the header for the correlation of an isotope ratio."""
    iso1, iso2 = isos[0]
    hdr_exp = isos[1]

    assert pgd._header(iso1, iso2).correlation == hdr_exp
