"""Classes to deal with the configuration files."""

from datetime import datetime
import json
from typing import List

from pgdtools import db


class DataBases:
    """Class to read and get information from `db.json` file.

    This class is used to read the `db.json` file and get information about the
    databases that are available. It has various methods to get different information
    and to print the information in the terminal nicely.

    Example:
        >>> # todo
    """

    def __init__(self):
        """Initialize the class.

        :raises FileNotFoundError: If the `db.json` file is not found.
        """
        if not db.LOCAL_DB_JSON.is_file():
            raise FileNotFoundError(
                f"The database file db.json not found at "
                f"{db.LOCAL_DB_JSON}. If this is the first time "
                f"you use pgdtools, please make sure you ran "
                f"`pgdtools.db.update()` first."
            )

        self._dbs = json.load(open(db.LOCAL_DB_JSON, "r"))

        # formatting of the dictionary entries
        for key in self._dbs:
            for version in self._dbs[key]["versions"]:
                # format date properly
                version["Date"] = datetime.strptime(version["Date"], "%Y-%m-%d").date()

    class DataBase:
        """Class to read and get information from a single database, e.g., `sic`."""

        def __init__(self, parent, db: str):
            """Initialize the class.

            :param parent: Parent class.
            :param db: Name of the database to get.

            :raises TypeError: If the parent class is not of type `DataBases`.
            """
            if not isinstance(parent, DataBases):
                raise TypeError("Parent class must be of type DataBases.")
            self._db = parent._dbs[db]

        @property
        def name(self):
            """Return the name of the database."""
            return self._db["db_name"]

        @property
        def version_latest(self) -> dict:
            """Return the latest version of the database, according to date."""
            versions = self.versions
            newest_index = 0
            newest_date = versions[newest_index]["Date"]
            for it, version in enumerate(versions):
                if (curr_date := version["Date"]) > newest_date:
                    newest_index = it
                    newest_date = curr_date
            return versions[newest_index]

        @property
        def versions(self) -> List[dict]:
            """Return all versions of the database."""
            return self._db["versions"]

    @property
    def dbs(self) -> List[str]:
        """Return a list of all available databases.

        :return: List of all available databases as a list of strings.
        """
        return list(self._dbs.keys())

    def database(self, db: str) -> DataBase:
        """Return a single database.

        :param db: Name of the database to get, e.g., "sic".

        :return: A single database as a `DataBase` object.
        """
        return self.DataBase(self, db)

    def urls(self, all=False) -> List[str]:
        """Return a list of URLs for all types of databases.

        :param all: If True, return all URLs for all versions of the database.
            Otherwise, return the latest databases.

        :return: List of URLs for all databases chosen as a list of strings.
        """
        ret_val = []
        for key in self._dbs:
            db = self.database(key)
            if all:
                for version in db.versions:
                    ret_val.append(version["URL"])
            else:
                ret_val.append(db.version_latest["URL"])

        return ret_val
