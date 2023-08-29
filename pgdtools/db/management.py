"""Management routines for the databases."""

import json
from pathlib import Path
from typing import Any, Dict

import requests

from pgdtools import data
from pgdtools import db


def current() -> Dict[str, Path]:
    """Get the current database version.

    Read the `current.json` file in the home folder and return a dictionary with all
    databases of the current grains.

    :return: Dictionary with paths to all current databases.

    :raises FileNotFoundError: If the `current.json` file is not found.
    :raises IOError: If the `current.json` file cannot be read.
    """
    file_io_error = (
        "The current database file could not be found. Please make sure that "
        "a database has been downloaded and and selected. You can select a new "
        "database for usage using `pgdtools.db.set_current()`."
    )

    if not db.LOCAL_CURRENT.is_file():
        raise FileNotFoundError(file_io_error)

    try:
        curr = json.load(open(db.LOCAL_CURRENT, "r"))
    except json.JSONDecodeError as err:
        raise IOError(file_io_error) from err

    # turn values of keys into paths
    curr_ret = {k: Path(v) for k, v in curr.items()}

    return curr_ret


def set_current(db_name: str, keyword: str, value: Any) -> None:
    """Set the current database to use.

    The current database is set based on a keyword and value pair. For example, if
    the keyword is `DOI` and the value is `10.5281/zenodo.1234567`, the database
    with this DOI will be set as the current database.
    If the selected database is not offline available, it will be downloaded from the
    internet.

    Note: It is highly recommended that keyword, value pairs are unique, and thus
    that only "Date", "DOI" or "URL" are used as keywords. If this is not the case,
    the first database that matches the keyword, value pair will be used.

    :param db_name: Name of the database, e.g., "sic".
    :param keyword: Keyword to use for selecting the database, e.g., "DOI".
    :param value: Value of the keyword, e.g., "10.5281/zenodo.1234567".

    :raises ValueError: If the keyword, value pair cannot be found.
    """
    curr = current()

    db_to_set = db.DataBases().database(db_name).entry_by_keyword(keyword, value)

    try:
        url = db_to_set["URL"]
    except KeyError as err:
        raise ValueError("Database could not be found.") from err

    # download the file if it is not already available
    if not db.LOCAL_PATH.joinpath(f"csv/{Path(url).name}").is_file():
        _download_file(url, db.LOCAL_PATH.joinpath(f"csv/{Path(url).name}"))

    # update the current database
    curr[db_name] = Path(db.LOCAL_PATH.joinpath(f"csv/{Path(url).name}"))

    curr_to_write = {k: str(v.absolute()) for k, v in curr.items()}

    # write the current database to file
    with open(db.LOCAL_CURRENT, "w") as fout:
        json.dump(curr_to_write, fout, indent=4)


def update(get_all: bool = False, clean: bool = False, get_config: bool = True) -> None:
    """Get the latest database(s) from the internet.

    This upgrades the local installation of `pgdtools` and gets the latest database(s)
    from the internet. If `clean` is True, all existing databases are first purged.
    By default, only the latest version of the database is downloaded. If `get_all` is
    True, all versions of the database are downloaded and stored locally.
    The update will set the current database to the latest version after it is
    downloaded.

    :param get_all: If True, get all versions of the database and store them locally.
    :param clean: If True, remove all existing databases before downloading.
    :param get_config: If True, get the latest configuration files from GitHub.
    """
    if clean:
        _clean_local_db()

    if get_config:
        _get_online_config()

    print("Configuration files updated.")

    data_bases = db.DataBases()

    urls = data_bases.urls(all=get_all)

    for url in urls:
        fname = Path(url).name
        _download_file(url, db.LOCAL_PATH.joinpath(f"csv/{fname}"))
        print(f"Database {fname} downloaded.")

    latest_version_dict = {}
    for db_name in data_bases.dbs:
        latest_version_dict[db_name] = str(
            db.LOCAL_PATH.joinpath(
                f"csv/{Path(data_bases.database(db_name).version_latest['URL']).name}"
            ).absolute()
        )

    with open(db.LOCAL_CURRENT, "w") as fout:
        json.dump(latest_version_dict, fout, indent=4)


def _clean_local_db() -> None:
    """Clean the local database folder: delete all csv files in csv folder."""
    files_to_delete = db.LOCAL_PATH.joinpath("csv").glob("*.csv")
    for file in files_to_delete:
        file.unlink()


def _get_online_config() -> None:
    """Get the database, bibliography, references, and techniques from GitHub.

    Here we get the latest configuration from GitHub (database folder) and store
    it locally in the `pgdtools` user folder in a config folder.
    """
    conf_local_zip = zip(
        [data.BIBFILE, data.DB_JSON, data.REFERENCES_JSON, data.TECHNIQUES_JSON],
        [db.LOCAL_BIB, db.LOCAL_DB_JSON, db.LOCAL_REF_JSON, db.LOCAL_TECH_JSON],
    )
    for url, local_file in conf_local_zip:
        _download_file(url, local_file)


def _download_file(url: str, local_file: Path) -> None:
    """Download a file from the internet and store it locally.

    This routine uses the `requests` library and downloads files as a stream in order
    to preserve memory. The file is stored locally at the given path.

    :param url: URL of the file to download.
    :param local_file: Path to the local file.

    :raises FileNotFoundError: If the file is not found at the given URL.
    :raises ConnectionError: If the connection to the URL fails in any other way.
    """
    with requests.get(url, stream=True) as rin:
        if rin.status_code == 404:
            raise FileNotFoundError(f"File not found at {url}.")
        elif rin.status_code != 200:
            raise ConnectionError(f"Connection error {rin.status_code} for url {url}.")

        with open(local_file, "wb") as floc:
            for chunk in rin.iter_content(chunk_size=8192):
                floc.write(chunk)
