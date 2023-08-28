"""Tests for routines dealing with config files."""

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
    assert db.dbs == ["sic", "graphites"]


def test_databases_urls_all(conf_files):
    """Return all URLs from all dbs as a list."""
    db = DataBases()
    urls = db.urls(all=True)

    assert isinstance(urls, list)
    assert len(set(urls)) == 8  # 8 unique URLs in the test database
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
    latest_dates = ["2023-07-22", "2021-01-01"]
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
