"""Functional tests for the data sub tool."""

import pytest

import pgdtools
import pgdtools.sub_tools.format


def test_info_type_error():
    """Raise a type error if the parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = pgdtools.sub_tools.format.Format("test")


@pytest.mark.parametrize(
    "rat",
    [
        [("C12", "C13"), "<sup>12</sup>C/<sup>13</sup>C"],
        [("Si29", "Si28"), "δ(<sup>29</sup>Si/<sup>28</sup>Si)"],
    ],
)
def test_ratio(pgd_head, rat):
    """Get header info formatted as html string."""
    ratios, exp_str = rat
    assert pgd_head.format.ratio(ratios) == exp_str
