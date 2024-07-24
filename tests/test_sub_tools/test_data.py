"""Functional tests for the data sub tool."""

import pytest

import pgdtools
import pgdtools.sub_tools.data


def test_info_type_error():
    """Raise a type error if the parent is not of type PresolarGrains."""
    with pytest.raises(TypeError):
        _ = pgdtools.sub_tools.data.Data("test")


# PROPERTIES #


def test_notes(pgd_head):
    """Get the notes of the grain data."""
    assert len(pgd_head.data.notes) <= 100
    assert pgd_head.data.notes.isna().sum() == 0


@pytest.mark.parametrize(
    "grain",
    [
        [
            "Gra-2014-AMA-000277",
            ("C12", "C13"),
            (87.2794570845652, 3.11330638050518, 3.11330638050518),
        ],
        [
            "SiC-0000-GYN-000057",
            ("C12", "C13"),
            (4.21556490704735, 0.029750831332946, 0.029750831332946),
        ],
        [
            "SiC-1996-HOP-200074",
            ("C12", "C13"),
            (44.098971144544, 4.1795097157011, 3.5135176991617),
        ],
    ],
)
def test_ratio(pgd, grain):
    """Get an isotope ratio and the uncertainty."""
    pgd_id, ratio, exp_values = grain
    pgd.filter.pgd_id(pgd_id)
    data, unc_pos, unc_neg = pgd.data.ratio(ratio)
    assert data[0] == exp_values[0]
    assert unc_pos[0] == exp_values[1]
    assert unc_neg[0] == exp_values[2]


def test_size(pgd):
    """Get the size of the grain data."""
    sizes = pgd.data.size
    sizes_all = pgd.data.size_all

    assert len(sizes_all) == len(pgd)
    assert len(sizes) < len(sizes_all)

    assert sizes.isna().sum().sum() == 0
