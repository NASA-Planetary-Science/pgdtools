"""Tests for the setup of local environment."""

from pathlib import Path

import pytest

from pgdtools.db.setup_local import setup_path


@pytest.mark.parametrize("platform", ["win32", "cygwin", "linux", "darwin", "unknown"])
def test_setup_path(mocker, platform: str, tmpdir_home: Path):
    """Test the setup of the local path."""
    _ = mocker.patch("sys.platform", platform)

    tmpdir_home.joinpath("csv").rmdir()
    tmpdir_home.joinpath("config").rmdir()

    app_local_path = setup_path()

    if platform == "win32" or platform == "cygwin":
        assert app_local_path == tmpdir_home.joinpath("AppData/Roaming/pgdtools/")
    else:
        assert app_local_path == tmpdir_home.joinpath(".config/pgdtools/")

    assert app_local_path.joinpath("csv").exists()
    assert app_local_path.joinpath("config").exists()

    # run again to ensure no error
    setup_path()
