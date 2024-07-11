"""Configuration tests for db management tests."""

import json
from pathlib import Path
from typing import Tuple

import pytest

from pgdtools.db import management as mgmt


@pytest.fixture
def conf_files(tmpdir_home, data_files_dir) -> Path:
    """Copy all the configuration files to the temporary directory."""
    config_files = ["db.json"]
    for fl in config_files:
        tmpdir_home.joinpath(f"config/{fl}").write_text(
            data_files_dir.joinpath(fl).read_text()
        )
    return tmpdir_home


@pytest.fixture
def current_file(tmpdir_home) -> Tuple[Path, dict]:
    """Create a fake `current.json` file and write into the right location."""
    curr_to_write = {"sic": "test.csv", "gra": "test-graphites.csv"}
    curr_ret = {k: Path(v) for k, v in curr_to_write.items()}

    with open(tmpdir_home.joinpath("current.json"), "w") as fout:
        json.dump(curr_to_write, fout)

    return tmpdir_home, curr_ret


@pytest.fixture
def mock_update(mocker, tmpdir_home, data_files_dir) -> Tuple:
    """Mock all downloads for db management tests and setup local files."""
    mock_get = mocker.patch.object(mgmt, "_get_online_config")
    mock_clean = mocker.patch.object(mgmt, "_clean_local_db")
    mock_download = mocker.patch.object(mgmt, "_download_file")

    # move "downloaded" files to local folder
    db_json = tmpdir_home.joinpath("config/db.json")
    db_json.write_text(data_files_dir.joinpath("db.json").read_text())

    return mock_get, mock_clean, mock_download
