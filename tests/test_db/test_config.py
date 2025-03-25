"""Tests for routines dealing with config files."""

from datetime import datetime

import pytest

from pgdtools.db import DataBases


def test_databases_conf_not_found():
    """Raise FileNotFoundError with useful error message if config file not found."""
    with pytest.raises(FileNotFoundError) as exc:
        DataBases()

    assert "pgdtools.db.update()" in str(exc.value)


def test_databases_dbs(conf_files):
    """Assert that the database reader returns all databases when asked."""
    db = DataBases()
    assert db.dbs == ["sic", "gra"]


def test_databases_urls_all(conf_files):
    """Return all URLs from all dbs as a list."""
    db = DataBases()
    urls = db.urls(all=True)

    assert isinstance(urls, list)
    assert len(set(urls)) == 9  # 8 unique URLs in the test database
    for url in urls:
        assert isinstance(url, str)
        assert url.startswith("http")
        assert url.endswith(".csv")


def test_databases_urls_latest(conf_files):
    """Return only latest URLs from all dbs as a list."""
    db = DataBases()
    urls = db.urls(all=False)

    assert isinstance(urls, list)
    assert len(set(urls)) == 2  # 2 unique URLs in the test database
    for url in urls:
        assert isinstance(url, str)
        assert url.startswith("http")
        assert url.endswith(".csv")

    # ensure that really the latest dates were chosen
    latest_dates = ["2025-03-10", "2023-07-22", "2021-01-01"]
    for url in urls:
        assert any(latest_date in url for latest_date in latest_dates)


def test_databases_database_wrong_parent(conf_files):
    """Assert that the database reader raises an error when the parent is wrong."""
    with pytest.raises(TypeError):
        DataBases.DataBase(None, "sic")


def test_databases_database_name(conf_files):
    """Assert that the database has a name return when asked."""
    db = DataBases()
    assert db.database("sic").name == "Silicon Carbide"


@pytest.mark.parametrize(
    "key_vals",
    [
        ("DOI", "10.5281/zenodo.8187488"),
        ("Date", datetime.strptime("2023-07-22", "%Y-%m-%d").date()),
        ("URL", "https://zenodo.org/record/8187488/files/PGD_SiC_2023-07-22.csv"),
    ],
)
def test_databases_database_entry(conf_files, key_vals):
    """Return the version entry of a given database when searching for a keyword."""
    dict_exp = {
        "Change": "1. New PGD Type asignments including new Type D.\n"
        "2. Now probabilities for being consistent with a given grain "
        "type are provided.\n"
        "3. Size is now split up into Size a and Size b with only numerical "
        "entries.\n"
        "4. Zero uncertainties in err[12C/13C] replaced by best estimate.\n"
        "5. Some notes added.\n"
        "6. Corrected typo in abbreviated reference (Hoppe et al. (2019) "
        "ApJ 887:8).\n"
        "7. Data from the following references added:\n"
        "NIttler et al. (2020) MAPS 55:1160\n"
        "Liu et al. (2021) ApJL 920:L26\n"
        "NIttler et al. (2021) MAPS 56:260\n"
        "Barosch et al. (2022) ApJL 935:L3\n"
        "Barosch et al. (2022) GCA 335:169\n"
        "Liu et al. (2022) EPJA 58:216\n"
        "Hoppe et al. (2023) ApJL 943:L22\n",
        "Date": datetime.strptime("2023-07-22", "%Y-%m-%d").date(),
        "DOI": "10.5281/zenodo.8187488",
        "Grains": 20230,
        "Known issues": "",
        "Released on": "Zenodo",
        "URL": "https://zenodo.org/record/8187488/files/PGD_SiC_2023-07-22.csv",
    }

    dbs = DataBases()
    db = dbs.database("sic")
    dict_rec = db.entry_by_keyword(*key_vals)

    assert dict_rec == dict_exp


def test_databases_database_entry_by_keyword_not_found(conf_files):
    """Return an empty dict if no entry is found."""
    db = DataBases()
    assert db.database("sic").entry_by_keyword("DOI", "test") == {}
