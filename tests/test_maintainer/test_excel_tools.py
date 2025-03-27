"""Tests for the Maintainer Excel tools."""

import json
from pathlib import Path

import pandas
import pytest

import pgdtools.maintainer as mt


@pytest.mark.parametrize("grain_type", ["sic", "gra"])
def test_append_to_db_json(excel_file, excel_file_gra, db_json, grain_type):
    """Append the information to the db.json file and ensure that doi is now in file."""
    if grain_type == "sic":
        ex_file = excel_file
    elif grain_type == "gra":
        ex_file = excel_file_gra
    doi = "10.5281/zenodo.1234567"
    mt.append_to_db_json(ex_file, doi, db_json=db_json)
    assert doi in db_json.read_text()


def test_append_to_db_json_astromat(excel_file, db_json):
    """Append the information to the db.json file and ensure that doi is now in file."""
    doi = "10.5281/IEDA.1234567"
    zenodo_record = "3p141592654"
    mt.append_to_db_json(excel_file, doi, db_json=db_json, zenodo_record=zenodo_record)
    assert zenodo_record in db_json.read_text()


@pytest.mark.filterwarnings("ignore::UserWarning")
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


def test_append_reference_json_create_append_quiet(excel_file, chtmpdir):
    """Create the reference file, delete a key, append it again in quiet mode."""
    fout = chtmpdir.joinpath("my_references.json")
    mt.append_reference_json(excel_file, ref_json=fout)
    assert fout.exists()

    # pop one key
    with open(fout, "r") as f:
        refs = json.load(f)
    key = list(refs.keys())[0]
    refs.pop(key)
    with open(fout, "w") as f:
        json.dump(refs, f, indent=4)

    with pytest.warns(UserWarning):
        mt.append_reference_json(excel_file, ref_json=fout, quiet=True)

    # ensure key exists again
    with open(fout, "r") as f:
        refs = json.load(f)
    assert key in refs.keys()

    assert fout.exists()


def test_append_techniques_json_create_append_quiet(excel_file, chtmpdir):
    """Create the techniques file, delete a key, append it again in quiet mode."""
    fout = chtmpdir.joinpath("my_techniques.json")
    mt.append_techniques_json(excel_file, tech_json=fout)
    assert fout.exists()

    # pop one key
    with open(fout, "r") as f:
        refs = json.load(f)
    key = list(refs.keys())[0]
    refs.pop(key)
    with open(fout, "w") as f:
        json.dump(refs, f, indent=4)

    with pytest.warns(UserWarning):
        mt.append_techniques_json(excel_file, tech_json=fout, quiet=True)

    # ensure key exists again
    with open(fout, "r") as f:
        refs = json.load(f)
    assert key in refs.keys()

    assert fout.exists()


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_compare_and_append_dictionaries_new_and_existing_overwrite():
    """Test the comparison of two dictionaries."""
    dict_ex = {"a": 1, "b": 2}
    dict_new = {"b": 3, "c": 4}

    dict_ex = mt.excel_tools._compare_and_append_dictionaries(
        dict_ex, dict_new, quiet=True
    )

    assert dict_ex == {"a": 1, "b": 3, "c": 4}


@pytest.mark.parametrize("overwrite", [True, False])
def test_compare_and_append_dictionaries_new_and_existing_no_overwrite(
    mocker, overwrite
):
    """Test the comparison of two dictionaries."""
    if overwrite:
        mocker.patch("builtins.input", return_value="y")
    else:
        mocker.patch("builtins.input", return_value="n")

    dict_ex = {"a": 1, "b": 2}
    dict_new = {"b": 3, "c": 4}

    dict_ex = mt.excel_tools._compare_and_append_dictionaries(
        dict_ex, dict_new, quiet=False
    )

    if overwrite:
        assert dict_ex == {"a": 1, "b": 3, "c": 4}
    else:
        assert dict_ex == {"a": 1, "b": 2, "c": 4}


@pytest.mark.parametrize("fname", ["db.json", "references.json", "techniques.json"])
def test_get_database_file(fname):
    """Get a file from a database folder, ensure it exists."""
    file_check = mt.excel_tools._get_database_file(fname)
    assert file_check.exists()
