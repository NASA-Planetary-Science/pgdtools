"""Functional tests for classification routine."""

import numpy as np
import pytest

from pgdtools import classify as cl, classify_sic_grain, PresolarGrains

# grains to test, following definitions:
# [
#   [c12_c13, n14_n15, d29Si, d30Si, al26_al27],
#   rho_si,
#   (expected type, expected subtype)
# ]
GRAIN_EXAMPLES = [
    [[None, None, None, None, None], None, ("U", None)],
    [[None, None, (50, 1), (50, 1), None], None, ("M", None)],
    [[None, None, (-500, 1), (-700, 1), None], None, ("X", "X1")],
    [[None, None, (-400, 1), (-700, 1), None], None, ("X", "X0")],
    [[None, None, (-900, 1), (-700, 1), None], None, ("X", "X2")],
    [
        [
            (np.float64(3.3885589239407), np.float64(0.00610853258708888)),
            (394.267547933069, 0.566450090035858),
            (-35.2919612590016, 18.3121630109112),
            (23.7422671345264, 27.7254617158076),
            (0.00315714392568678, 0.000163497375282813),
        ],
        None,
        ("AB", "AB1"),
    ],
    # SiC-2021-LIU-000066 (symmetric C,N errors)
    [
        [
            (4.83060142134851, (0.0477087585128927, 0.0477087585128927)),
            None,
            (32.4848700605198, 13.9315484224466),
            (52.9063347053509, 17.4166866728135),
            None,
        ],
        None,
        ("AB", None),
    ],  # SiC-0000-GYN-000001
    [
        [
            (20.0910687966414, (0.148923016686695, 0.148923016686695)),
            (500, (27.5735294117647, 27.5735294117647)),
            (27.8, 3.1),
            (29.8, 3.6),
            None,
        ],
        None,
        ("M", None),
    ],  # SiC-1992-VIR-000048
    [
        [(57.5, (3.5, 3.5)), None, (-71.5, 8.1), (17.4, 5.8), None],
        None,
        ("M", None),
    ],  # SiC-2007-HEC-000019
    [[None, None, None, -525, None], None, ("X", None)],  # SiC-2007-MAR-000017
    [
        [None, None, None, None, (0.000650691, 0.000141979)],
        None,
        ("U", None),
    ],  # SiC-2010-HOP-002106
    [
        [(11, (0.3, 0.3)), (13, (0.3, 0.3)), (-282, 101), (-3, 131), None],
        None,
        ("X", "X2"),
    ],  # SiC-2016-LIU-000005
    [
        [
            (258.2239612619, (8.8265045517372, 8.8265045517372)),
            (529.1688, (67.30157, 53.6538)),
            (23.23, 4.71695487974753),
            (134.98, 3.93278993367635),
            (0.00089428763819095, 0.00017743658291457),
        ],
        -0.269542481757476,
        ("Y", None),
    ],  # SiC-1994-HOP-000425
    [
        [
            (50.762, (0.423508, 0.416553)),
            (250.734, (13.3598, 12.0732)),
            (-21.34, 10.4385210385083),
            (-43.52, 10.071533077373),
            (0.0325437, 0.0014007),
        ],
        0.00459506923176846,
        ("X", "X1"),
    ],  # SiC-1996-NIT-100051
]


@pytest.mark.parametrize("grain", GRAIN_EXAMPLES)
def test_classify_grain(grain):
    """Test classification of grain examples."""
    data, rho_si, expected = grain
    if rho_si is not None:
        received = classify_sic_grain(*data, rho_si)
    else:
        received = classify_sic_grain(*data)
    assert received == expected


@pytest.mark.skip(reason="Takes too long.")
def test_classify_grain_whole_db():
    """Test classification of all grains in the whole database."""
    pgd = PresolarGrains()
    pgd.filter.db(pgd.DataBase.SiC)
    db = pgd.db
    grain_ids = list(db.index)

    for id in grain_ids:
        pgd.filter.pgd_id(id)
        type_db = pgd.db.loc[id, "PGD Type"]
        subtype_db = pgd.db.loc[id, "PGD Subtype"]
        if subtype_db is np.nan:
            subtype_db = None

        c12_c13 = np.array(pgd.data.ratio(["C12", "C13"], dropnan=False)).flatten()
        n14_n15 = np.array(pgd.data.ratio(["N14", "N15"], dropnan=False)).flatten()
        d29Si = np.array(pgd.data.ratio(["Si29", "Si28"], dropnan=False)).flatten()
        d30Si = np.array(pgd.data.ratio(["Si30", "Si28"], dropnan=False)).flatten()
        al26_al27 = np.array(pgd.data.ratio(["Al26", "Al27"], dropnan=False)).flatten()
        rho_si = pgd.db.loc[id, "rho[30Si-29Si]"]

        if np.isnan(c12_c13[0]):
            c12_c13 = None
        else:
            c12_c13 = (c12_c13[0], (c12_c13[1], c12_c13[2]))
        if np.isnan(n14_n15[0]):
            n14_n15 = None
        else:
            n14_n15 = (n14_n15[0], (n14_n15[1], n14_n15[2]))
        if np.isnan(d29Si[0]):
            d29Si = None
        else:
            d29Si = (d29Si[0], d29Si[1])
        if np.isnan(d30Si[0]):
            d30Si = None
        else:
            d30Si = (d30Si[0], d30Si[1])
        if np.isnan(al26_al27[0]):
            al26_al27 = None
        else:
            al26_al27 = (al26_al27[0], al26_al27[1])
        if np.isnan(rho_si):
            rho_si = 0

        type_rec, subtype_rec = classify_sic_grain(
            c12_c13,
            n14_n15,
            d29Si,
            d30Si,
            al26_al27,
            rho_si=rho_si,
            ret_probabilities=False,
        )
        # get the probabilities for all the grains
        probs_rec = classify_sic_grain(
            c12_c13,
            n14_n15,
            d29Si,
            d30Si,
            al26_al27,
            rho_si=rho_si,
            ret_probabilities=True,
        )

        # get probabilites from the database
        probs_db = {}
        for key in probs_rec.keys():
            probs_db[key] = pgd.db.loc[id, f"p({key})"]

        try:
            assert type_rec == type_db
            assert subtype_rec == subtype_db
            assert probs_rec == probs_db
        except AssertionError as err:
            raise AssertionError(f"Grain id: {id}") from err

        pgd.reset()


# TEST PRIVATE ROUTINES #


@pytest.mark.parametrize(
    "combination",
    [
        [-20, (-20, 2)],
        [(-20, None), (-20, 2)],
        [(-20, np.nan), (-20, 2)],
        [(-20, (None, None)), (-20, (2, 2))],
        [(-20, (np.nan, np.nan)), (-20, (2, 2))],
        [(-20, (None, 0.1)), (-20, (2, 0.1))],
        [(-20, (np.nan, 0.1)), (-20, (2, 0.1))],
        [(-20, (0.1, None)), (-20, (0.1, 2))],
        [(-20, (0.1, np.nan)), (-20, (0.1, 2))],
    ],
)
def test_replace_errors(combination):
    """Test private routine _replace_errors()."""
    received = cl._replace_errors(combination[0])
    expected = combination[1]
    assert received == expected
