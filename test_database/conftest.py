"""Fixtures for pytest."""

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest
import requests

import test_database
from test_database import GH_FILES


def prepare_dataframe(fname: Path) -> pd.DataFrame:
    """Read in a csv file and returns it as our standard defined pandas dataframe.

    :param fname: File to read.

    :return: Data frame of the file.
    """
    kwargs = {"delimiter": ",", "header": 0, "index_col": 0}
    df = pd.read_csv(fname, **kwargs)
    return df


@pytest.fixture()
def gh_dbs(tmp_path) -> Dict[str, pd.DataFrame]:
    """Get the current database, store them locally, give a dictionary with fnames.

    This fixture downloads the current database from GitHub and stores the files
    locally in a temporary folder. Then a dictionary is returned where the keys
    are the filename of the db, e.g., `sic.csv`) and a default formatted
    ``pd.DataFrame`` as the value.

    :param tmp_path: Temporary path fixture.

    :return: Dictionary with file name (key), DataFrame with data (value)
    """
    retval = {}
    for key in GH_FILES:
        tmp_file = tmp_path.joinpath(key)
        dl = requests.get(GH_FILES[key])
        tmp_file.write_text(dl.text)
        df = prepare_dataframe(tmp_file.absolute())
        retval[str(tmp_file.name)] = df
    return retval


@pytest.fixture()
def curr_dbs() -> Dict[str, pd.DataFrame]:
    """Get the current database and return file name and path to file.

    This fixtures reads the current database stored locally and returns a
    dictionary with the file name and the data as a ``pd.DataFrame``.
    This dictionary has the same structure as fixture ``gh_db``.

    :return: Dictionary with file name (key), DataFrame with data (value)
    """
    pth = Path(test_database.__file__).parents[1]
    db_path = pth.joinpath("database")
    items = db_path.iterdir()

    retval = {}
    for item in items:
        if item.suffix == ".csv":
            df = prepare_dataframe(item.absolute())
            retval[str(item.name)] = df
    return retval
