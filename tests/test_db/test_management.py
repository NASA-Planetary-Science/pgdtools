"""Tests for database management tools."""

from pathlib import Path

import pytest
import requests_mock

from pgdtools.db import management as mgmt

# PRIVATE FUNCTIONS


def test_clean_local_db(tmpdir_home):
    """Clean the local database of all csv files."""
    csv_file = tmpdir_home.joinpath("csv/test.csv")
    other_file = tmpdir_home.joinpath("csv/README.md")

    csv_file.write_text("test")
    other_file.write_text("test")

    mgmt._clean_local_db()

    assert not csv_file.exists()
    assert other_file.exists()


def test_get_online_config(mocker):
    """Ensure online configuration getter calls download file and files properly."""
    mock_dl = mocker.patch.object(mgmt, "_download_file")
    mgmt._get_online_config()

    for call, _ in mock_dl.call_args_list:
        assert Path(call[0]).name == Path(call[1]).name
        assert Path(call[0]) != Path(call[1])


def test_download_file(mocker, tmpdir_home):
    """Test downloading of a file from `url` to `local_file` while mocking requests."""
    url = "https://test.com/test.csv"
    local_file = tmpdir_home.joinpath("test.csv")

    with requests_mock.Mocker() as mock_req:
        mock_req.get(url, text="test")

        mgmt._download_file(url, local_file)

        assert local_file.exists()
        assert local_file.read_text() == "test"


def test_download_file_file_not_found(tmpdir_home):
    """Raise FileNotFoundError if request returns status code 404."""
    url = "https://test.com/test.csv"
    local_file = tmpdir_home.joinpath("test.csv")

    with requests_mock.Mocker() as mock_req:
        mock_req.get(url, status_code=404)

        with pytest.raises(FileNotFoundError):
            mgmt._download_file(url, local_file)


def test_download_file_connection_error(tmpdir_home):
    """Raise ConnectionError if request returns status code != 200."""
    url = "https://test.com/test.csv"
    local_file = tmpdir_home.joinpath("test.csv")

    with requests_mock.Mocker() as mock_req:
        mock_req.get(url, status_code=500)

        with pytest.raises(ConnectionError):
            mgmt._download_file(url, local_file)
