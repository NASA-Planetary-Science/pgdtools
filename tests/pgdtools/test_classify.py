"""Functional tests for classification routine."""

import pytest
import numpy as np

from pgdtools import classify as cl, classify_grain, PresolarGrains

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
            (4.83060142134851, (0.0477087585128927, 0.0477087585128927)),
            None,
            (32.4848700605198, 13.9315484224466),
            (52.9063347053509, 17.4166866728135),
            None,
        ],
        None,
        ("AB", None),
    ],  # SiC-0000-GYN-0000001
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
    # [[None, None, None, -525, None], None, ("X", None)],  # SiC-2007-MAR-000017
    # [
    #     [None, None, None, None, (0.000650691, 0.000141979)],
    #     None,
    #     ("U", None),
    # ],  # SiC-2010-HOP-002106
    [
        [
            (138.674465468262, (1.4378027705659, 1.4378027705659)),
            (16.6278181598623, (0.343038104843092, 0.343038104843092)),
            (60.678699273462, 17.5771124080633),
            (57.6361448173834, 13.5037014583254),
            (0.0623910427236267, 0.00100851492307657),
        ],
        None,
        ("U", None),  # SiC-2017-LIU-200012
    ],
]


@pytest.mark.smoke
@pytest.mark.parametrize("grain", GRAIN_EXAMPLES)
def test_classify_grain(grain):
    """Test classification of grain examples."""
    data, rho_si, expected = grain
    if rho_si is not None:
        received = classify_grain(*data, rho_si)
    else:
        received = classify_grain(*data)
    assert received == expected


@pytest.mark.skip(reason="Takes too long.")
def test_classify_grain_whole_db():
    """Test classification of all grains in the whole database."""
    pgd = PresolarGrains()
    db = pgd.db
    grain_ids = list(db.index)

    for id in grain_ids:
        grain = pgd.grain[id]
        type_db, subtype_db = grain.pgd_type
        if subtype_db == np.nan:
            subtype_db = None

        c12_c13 = grain.value("C12", "C13")[0:2]
        n14_n15 = grain.value("N14", "N15")[0:2]
        d29Si = grain.value("29Si", "28Si")[0:2]
        d30Si = grain.value("30Si", "28Si")[0:2]
        al26_al27 = grain.value("26Al", "27Al")[0:2]
        rho_si = grain.correlation("Si30", "Si29")

        if np.isnan(c12_c13[0]):
            c12_c13 = None
        if np.isnan(n14_n15[0]):
            n14_n15 = None
        if np.isnan(d29Si[0]):
            d29Si = None
        if np.isnan(d30Si[0]):
            d30Si = None
        if np.isnan(al26_al27[0]):
            al26_al27 = None

        type_rec, subtype_rec = classify_grain(
            c12_c13, n14_n15, d29Si, d30Si, al26_al27, rho_si=rho_si
        )

        assert type_rec == type_db
        assert subtype_rec == subtype_db


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
