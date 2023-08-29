"""Configuration for pytest."""

from pathlib import Path

import pytest

from pgdtools import PresolarGrains


@pytest.fixture
def data_files_dir(request):
    """Provide the path to the data_files directory."""
    curr = Path(request.fspath).parents[1]
    return Path(curr).joinpath("data_files/").absolute()


@pytest.fixture(scope="session")
def pgd():
    """Fixture for the PGD database."""
    pgd = PresolarGrains()
    yield pgd
    pgd.reset()


@pytest.fixture(autouse=True)
def tmpdir_home(tmpdir, mocker) -> Path:
    """Fixture to patch all local paths to a temporary home directory."""
    tmp_home = Path(tmpdir).joinpath(".config/pgdtools/")

    mocker.patch.object(Path, "home", return_value=tmp_home)

    mocker.patch("pgdtools.db.LOCAL_PATH", tmp_home)
    mocker.patch("pgdtools.db.LOCAL_PATH", tmp_home)

    mocker.patch(
        "pgdtools.db.LOCAL_CURRENT",
        tmp_home.joinpath("current.json"),
    )

    mocker.patch(
        "pgdtools.db.LOCAL_BIB",
        tmp_home.joinpath("config/pgd_references.bib"),
    )
    mocker.patch(
        "pgdtools.db.LOCAL_DB_JSON",
        tmp_home.joinpath("config/db.json"),
    )
    mocker.patch(
        "pgdtools.db.LOCAL_REF_JSON",
        tmp_home.joinpath("config/references.json"),
    )
    mocker.patch(
        "pgdtools.db.LOCAL_TECH_JSON",
        tmp_home.joinpath("config/techniques.json"),
    )

    tmp_home.joinpath("csv").mkdir(parents=True, exist_ok=True)
    tmp_home.joinpath("config").mkdir(parents=True, exist_ok=True)
    return tmp_home
