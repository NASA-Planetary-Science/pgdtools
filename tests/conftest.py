"""Configuration for pytest."""

from pathlib import Path

import pytest

from pgdtools import PresolarGrains


@pytest.fixture
def data_files_dir(request):
    """Provide the path to the data_files directory."""
    curr = Path(__file__).parent
    return Path(curr).joinpath("data_files/").absolute()


@pytest.fixture
def pgd(pgd_setup):
    """Fixture for the PGD database."""
    pgd = PresolarGrains()
    yield pgd
    pgd.reset()


@pytest.fixture
def pgd_head(pgd):
    """Return the first 100 rows of the PGD."""
    pgd.db = pgd.db.head(100)
    return pgd


@pytest.fixture
def pgd_setup(tmpdir_home, data_files_dir):
    """Copy and create the required files for reading the PGD."""
    sic_db_name = "PGD_SiC_2025-03-10.csv"
    gra_db_name = "PGD_Gra_2024-05-13.csv"

    db_json = tmpdir_home.joinpath("config/db.json")
    db_json.write_text(data_files_dir.joinpath("db.json").read_text())

    ref_json = tmpdir_home.joinpath("config/references.json")
    ref_json.write_text(data_files_dir.joinpath("references.json").read_text())

    tech_json = tmpdir_home.joinpath("config/techniques.json")
    tech_json.write_text(data_files_dir.joinpath("techniques.json").read_text())

    sic_db = tmpdir_home.joinpath(f"csv/{sic_db_name}")
    sic_db.write_bytes(data_files_dir.joinpath(sic_db_name).read_bytes())
    gra_db = tmpdir_home.joinpath(f"csv/{gra_db_name}")
    gra_db.write_bytes(data_files_dir.joinpath(gra_db_name).read_bytes())

    current_file = tmpdir_home.joinpath("current.json")
    current_file.write_text(
        f'{{"sic": "{str(sic_db.absolute())}", "gra": "{str(gra_db.absolute())}"}}'
    )  # noqa: B907


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
