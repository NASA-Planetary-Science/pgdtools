"""Functional tests for the headers sub tools."""

import pytest

import pgdtools.sub_tools.headers


def test_search_header_type_error(pgd):
    """Raise a type error if the parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = pgdtools.sub_tools.headers.Headers("test")


@pytest.mark.parametrize(
    "isos",
    [[("C12", "C13"), ("12C/13C", False)], [("Si29", "Si28"), ("d(29Si/28Si)", True)]],
)
def test_search_header(pgd, isos):
    """Search the header for an isotope ratio and if it's a delta value."""
    iso1, iso2 = isos[0]
    hdr_exp = isos[1]

    assert pgd._header.ratio(iso1=iso1, iso2=iso2) == hdr_exp


def test_search_header_not_found(pgd):
    """Return None if the header is not found."""
    assert pgd._header.ratio("C532", "C789") is None
