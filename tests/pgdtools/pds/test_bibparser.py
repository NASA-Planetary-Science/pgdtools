import pytest

from pgdtools.pds import bibparser as bprs


examples = [
    (
        ["Trappitsch, Reto", "Savina, M. R.", "Isselhardt, Brett Hallen"],
        [("Trappitsch", "R."), ("Savina", "M.R."), ("Isselhardt", "B.H.")],
    ),
    (
        ["Alexander, C. M. O'D.", "Nittler, Larry R."],
        [("Alexander", "C.M.O'D."), ("Nittler", "L.R.")],
    ),
    (
        ["Amari, S.", "Nichols, Jr., R. H.", "Pellin, M. J."],
        [("Amari", "S."), ("Nichols Jr.", "R.H."), ("Pellin", "M.J.")],
    ),
    (["Stephan, Thomas"], [("Stephan", "T.")]),
]


@pytest.mark.parametrize("ex", examples)
def test_format_author(ex):
    """Check that author formatting works appropriately."""
    inp = ex[0]
    out_exp = ex[1]

    assert bprs.format_authors(inp) == out_exp
