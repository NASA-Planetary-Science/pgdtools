"""Tests for database management tools."""

from pathlib import Path

import pytest
import requests_mock

from pgdtools import db
from pgdtools.db import DataBases, management as mgmt


def test_update(mock_update):
    """Ensure update calls the correct functions and downloads the files."""
    _, _, mock_update = mock_update
    get_all = False

    mgmt.update(get_all=get_all)

    urls = DataBases().urls(all=get_all)

    assert mock_update.call_count == len(urls)
    for url in urls:
        local_file = db.LOCAL_PATH.joinpath(f"csv/{Path(url).name}")
        mock_update.assert_any_call(url, local_file)


@pytest.mark.parametrize("clean", [True, False])
@pytest.mark.parametrize("get_config", [True, False])
def test_update_clean_config(mock_update, clean, get_config):
    """Ensure update calls the correct functions when selecting clean and configs."""
    mock_get, mock_clean, mock_update = mock_update

    mgmt.update(clean=clean, get_config=get_config)

    mock_get.assert_called_once() if get_config else mock_get.assert_not_called()
    mock_clean.assert_called_once() if clean else mock_clean.assert_not_called()


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
