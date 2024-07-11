"""Functional tests for the PGD tools."""

import pytest

from pgdtools import PresolarGrains


def test_pg_init(mocker):
    """Test initialization of the presolar grain database without a config file."""
    mock_pd = mocker.patch("pandas.read_csv")
    mock_pd_concat = mocker.patch("pandas.concat")
    mock_update = mocker.patch("pgdtools.db.update", return_value=None)
    mock_current = mocker.patch("pgdtools.db.current")

    mock_current.side_effect = [
        FileNotFoundError,
        {"sic": "test.csv", "gra": "gra.csv"},
    ]

    _ = PresolarGrains()

    mock_update.assert_called_once()
    mock_pd_concat.assert_called_once()
    assert mock_pd.call_count == 2
    assert mock_current.call_count == 2


@pytest.mark.parametrize(
    "corrs", [[["Si30", "Si29"], "rho[30Si-29Si]"], [["Fe54", "Ni67"], None]]
)
def test_pg_header_correlation(pgd, corrs):
    """Test header correlation."""
    isos, expected = corrs
    received = pgd.header_correlation(*isos)
    assert received == expected
