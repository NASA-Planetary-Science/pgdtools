"""Functional tests for the data sub tool."""

import numpy as np
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
    assert data.iloc[0] == exp_values[0]
    assert unc_pos.iloc[0] == exp_values[1]
    assert unc_neg.iloc[0] == exp_values[2]


@pytest.mark.parametrize(
    "grains",
    [
        [
            ["SiC-2018-NGU-001467", "SiC-2018-NGU-001468", "SiC-2018-NGU-001469"],
            [("30Si", "28Si"), ("29Si", "28Si")],
            [
                np.array([2.878785, -14.65148, 9.194016]),
                np.array([17.3810739784015, 27.2944250477073, 25.2720715909656]),
                np.array([1.614332, 53.60126, -49.70938]),
                np.array([36.1074016544854, 16.603475361908, 35.379145053113]),
                np.array([0.0210329907738579, 0.0291273417717291, 0.0147633799686172]),
            ],
        ],
        [
            ["SiC-2005-NIT-000596", "SiC-2005-NIT-000597", "SiC-2005-NIT-000598"],
            [("12C", "13C"), ("14N", "15N")],
            [
                np.array([48.20253, 49.68008]),
                np.array([[1.128452, 1.07798], [0.790802, 0.766407]]),
                np.array([737.5635, 521.47]),
                np.array([[24.75354, 23.19659], [59.05438, 48.14899]]),
                None,
            ],
        ],
        [
            ["SiC-2005-NIT-000634", "Gra-2014-AMA-000882"],
            [("12C", "13C"), ("29Si", "28Si")],
            [
                np.array([67.38965, 115.233944372342]),
                np.array(
                    [[3.057106, 2.802803], [0.655507064626931, 0.655507064626931]]
                ),
                np.array([20.58721, -6.61727143485091]),
                np.array([23.4202779519643, 17.0911990170259]),
                None,
            ],
        ],
    ],
)
def test_ratio_xy(pgd, grains):
    """Search for two isotope ratios and their uncertianties, simplifying errors."""
    grain_list, ratios, exp_values = grains
    pgd.filter.pgd_id(grain_list)
    xdat_exp, xunc_exp, ydat_exp, yunc_exp, corr_exp = exp_values

    xdat, xunc, ydat, yunc, corr = pgd.data.ratio_xy(*ratios, simplify_unc=True)

    np.testing.assert_equal(xdat.to_numpy(), xdat_exp)
    np.testing.assert_equal(ydat.to_numpy(), ydat_exp)
    np.testing.assert_equal(xunc.to_numpy(), xunc_exp)
    np.testing.assert_equal(yunc.to_numpy(), yunc_exp)
    if corr_exp is None:
        assert corr is None
    else:
        np.testing.assert_equal(corr.to_numpy(), corr_exp)


def test_size(pgd):
    """Get the size of the grain data."""
    sizes = pgd.data.size
    sizes_all = pgd.data.size_all

    assert len(sizes_all) == len(pgd)
    assert len(sizes) < len(sizes_all)

    assert sizes.isna().sum().sum() == 0
