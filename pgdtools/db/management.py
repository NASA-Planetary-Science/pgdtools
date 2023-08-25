"""Management routines for the databases."""

from pathlib import Path

import requests

from pgdtools import data
from pgdtools import db


def update(get_all: bool = False, clean: bool = False, **kwargs) -> None:
    """Get the latest database(s) from the internet.

    This upgrades the local installation of `pgdtools` and gets the latest database(s)
    from the internet. If `clean` is True, all existing databases are first purged.
    By default, only the latest version of the database is downloaded. If `get_all` is
    True, all versions of the database are downloaded and stored locally.

    Note for developers: When testing, pass the addidional argument `is_test=True` to
        skip any downloads.

    :param get_all: If True, get all versions of the database and store them locally.
    :param clean: If True, remove all existing databases before downloading.
    :param kwargs: Additional keyword arguments for developers (see note above).
    """
    is_test = kwargs.get("is_test", False)

    _get_online_config() if not is_test else None


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
