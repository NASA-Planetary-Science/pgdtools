"""Fixtures for the maintainer tools."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def chtmpdir(tmpdir) -> Path:
    """Change to temp dir and return to original dir after the test.

    :param tmpdir: Temporary directory fixture.

    :yield: Path to the temporary directory.
    """
    curr_dir = Path.cwd()
    os.chdir(tmpdir)
    yield Path(tmpdir).absolute()
    os.chdir(curr_dir)


@pytest.fixture
def db_json(request, tmpdir) -> Path:
    """Take the existing `db.json`, put it in tmp path, and return the path."""
    curr = Path(request.fspath).parents[1]
    db_json = Path(curr).joinpath("data_files/db.json")
    tmp_db_json = Path(tmpdir).joinpath("db.json")
    tmp_db_json.write_text(db_json.read_text())
    return tmp_db_json


@pytest.fixture
def excel_file(request) -> Path:
    """Provide the path to the database Excel file from 2023-07-22."""
    curr = Path(request.fspath).parents[1]
    return Path(curr).joinpath("data_files/PGD_SiC_2025-03-10.xlsx").absolute()


@pytest.fixture
def excel_file_gra(request) -> Path:
    """Provide the path to the database Excel file for graphites."""
    curr = Path(request.fspath).parents[1]
    return Path(curr).joinpath("data_files/PGD_Gra_2024-05-13.xlsx").absolute()
