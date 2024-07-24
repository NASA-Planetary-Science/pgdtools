"""Test the utilities sub tool."""

import pytest

from pgdtools.sub_tools import utilities as utl

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
    assert inst.html == f"<sup>{aaa}</sup>{symb.capitalize()}"

    assert str(inst) == f"{aaa}{symb.capitalize()}"


def test_iso_value_error():
    """Raise a value error if the input is not a string."""
    with pytest.raises(ValueError):
        _ = utl.Isotope(123)


def test_iso_element_value_error():
    """Raise a value error if no atomic number or no element symbol is given."""
    with pytest.raises(ValueError):
        _ = utl.Isotope("C")
    with pytest.raises(ValueError):
        _ = utl.Isotope("12")


def test_iso_element_allowed():
    """Pass through with element only input if allowed."""
    inst = utl.Isotope("C", allow_element=True)

    assert inst.ele == "C"
    assert inst.a == 0

    assert str(inst) == "C"

    with pytest.raises(ValueError):  # still fails for only atomic number
        _ = utl.Isotope("12", allow_element=True)
