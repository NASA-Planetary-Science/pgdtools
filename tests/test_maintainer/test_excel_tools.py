"""Tests for the Maintainer Excel tools."""

import json
from pathlib import Path

import pandas
import pytest

import pgdtools.maintainer as mt


def test_append_to_db_json(excel_file, db_json):
    """Append the information to the db.json file and ensure that doi is now in file."""
    doi = "10.5281/zenodo.1234567"
    mt.append_to_db_json(excel_file, doi, db_json=db_json)
    assert doi in db_json.read_text()


def test_append_to_db_json_repo_db(excel_file, mocker):
    """Assert that if no `db_json` is given, the default one is used."""
    # mock the open routine so that we won't write to the actual file
    mock_open = mocker.patch("builtins.open")

    # need to mock other things that use open
    _ = mocker.patch("json.load", return_value={"sic": {"versions": []}})
    _ = mocker.patch("pandas.read_excel", return_value=pandas.DataFrame())

    doi = "10.5281/zenodo.1234567"
    mt.append_to_db_json(excel_file, doi)

    path_to_repo_db_json = Path(__file__).parents[2].joinpath("database/db.json")

    mock_open.assert_called_with(path_to_repo_db_json, "w")


def test_append_to_db_json_db_not_found(excel_file):
    """Raise FileNotFoundError if database is not there."""
    doi = "10.5281/zenodo.1234567"
    with pytest.raises(FileNotFoundError):
        mt.append_to_db_json(excel_file, doi, db_json=Path("db.json"))


def test_append_to_db_json_unsupported_db_key(db_json):
    """Raise NotImplementedError if an unsupported database is in Excel file name."""
    excel_file = Path("asdf.xlsx")
    with pytest.raises(NotImplementedError):
        mt.append_to_db_json(excel_file, "10.5281/zenodo.1234567", db_json=db_json)


def test_append_to_db_json_unsupported_archive(excel_file, db_json):
    """Raise NotImplementedError if doi does not contain Zenodo as an archive."""
    doi = "10.5281/asdf.1234567"
    with pytest.raises(NotImplementedError):
        mt.append_to_db_json(excel_file, doi, db_json=db_json)


def test_append_to_json_date_not_found(excel_file, tmpdir, db_json):
    """Warn if date is not found in Excel file name."""
    doi = "10.5281/zenodo.1234567"
    tmp_excel_file = Path(tmpdir).joinpath("PGD_SiC_1999-05-05.xlsx")
    tmp_excel_file.write_bytes(excel_file.read_bytes())
    with pytest.warns(UserWarning):
        mt.append_to_db_json(tmp_excel_file, doi, db_json=db_json)


def test_append_to_json_doi_exists(excel_file, tmpdir, db_json, mocker):
    """Warn if DOI is already in json file and do nothing."""
    spy = mocker.spy(json, "dump")

    doi = "10.5281/zenodo.8187479"
    with pytest.warns(UserWarning):
        mt.append_to_db_json(excel_file, doi, db_json=db_json)

    spy.assert_not_called()


def test_create_techniques_json(excel_file, chtmpdir):
    """Create the techniques JSON file and ensure it exists."""
    mt.create_techniques_json(excel_file)
    assert chtmpdir.joinpath("techniques.json").exists()


def test_create_reference_json(excel_file, chtmpdir):
    """Create the reference JSON file and ensure it exists."""
    mt.create_references_json(excel_file)
    assert chtmpdir.joinpath("references.json").exists()
