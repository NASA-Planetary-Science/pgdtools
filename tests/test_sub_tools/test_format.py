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
        [("C12", "C13"), r"$^{12}\mathrm{C}/^{13}\mathrm{C}$"],
        [("Si29", "Si28"), r"$\delta(^{29}\mathrm{Si}/^{28}\mathrm{Si})\quad(‰)$"],
    ],
)
def test_ratio(pgd_head, rat):
    """Get header info formatted as html string."""
    ratios, exp_str = rat
    assert pgd_head.format.ratio(ratios) == exp_str
