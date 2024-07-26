"""Functional tests for the PGD tools."""

import pytest

import pgdtools.sub_tools.headers
import pgdtools.sub_tools.utilities as utl


# ISOTOPE CLASS #


@pytest.mark.parametrize(
    "iso",
    [["C12", "C", 12], ["238U", "U", 238], ["th-232", "Th", 232], ["SI-29", "Si", 29]],
)
def test_iso_ele_a(iso):
    """Check that the isotope is properly parsed."""
    iso_in, symb, aaa = iso
    inst = utl.Isotope(iso_in)

    assert inst.ele == symb
    assert inst.a == aaa

    assert str(inst) == f"{aaa}{symb.capitalize()}"


def test_iso_value_error():
    """Raise a value error if the input is not a string."""
    with pytest.raises(ValueError):
        _ = utl.Isotope(123)


# SEARCH HEADER CLASS #


def test_search_header_type_error(pgd):
    """Raise a type error if the parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = pgdtools.sub_tools.headers.Headers("test")
