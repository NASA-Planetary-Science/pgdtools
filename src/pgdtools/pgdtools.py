"""Main PresolarGrains class that handles the overall database stuff.

All sub functions and tools live in the `sub_tools` folder and are imported here."""

from enum import Enum

import pandas as pd

import pgdtools.sub_tools.headers
from pgdtools import db
from pgdtools.sub_tools import Filters, References, Techniques


class PresolarGrains:
    """Presolar grain database class.

    This class is the main class to work with the presolar grain database.

    Attention: Only SiC grains are currently supported!

    Example:
        Todo
    """

    class DataBase(Enum):
        """Enum to represent the different databases.

        The name of each enum is something that should make sense to the user,
        the value the 3 letter abbreviation that each PGD Grain Name starts with.
        """

        SiC = "SiC"
        Graphite = "Gra"

    def __init__(self):
        """Initialize the presolar grain class.

        Load the default database into self.db and self._db as a backup.
        """
        try:
            curr_db = db.current()
        except FileNotFoundError:
            print("No default database found, downloading latest versions...")
            db.update()
            curr_db = db.current()

        keys = curr_db.keys()
        if not keys:
            raise ValueError("No database found. Try to update the database.")

        filepaths = []
        for key in keys:
            filepaths.append(curr_db[key])

        dfs = [pd.read_csv(filepath, index_col=0) for filepath in filepaths]
        self.db = pd.concat(dfs)
        self._db = self.db.copy(deep=True)

    def __repr__(self):
        """Return a string representation of the class."""
        return str(self.db)

    def __eq__(self, other):
        """Check if the databases are equal."""
        return self.db.equals(other.db)

    def __len__(self):
        """Return the number of grains in the current, filtered database."""
        return len(self.db)

    def __iter__(self):
        """Iterate over (index, row) for all entries the filtered database."""
        return self.db.iterrows()

    # SUB TOOL ACCESS #

    @property
    def info(self):
        raise NotImplementedError("Info class not implemented yet.")

    @property
    def filter(self):
        """Filter the database for specific grains.

        Various filters are implements, the examples below show some of the
        possibilities. Please consult the documentation for a full list of options.

        Generally, all filter default to select the grains that are in the filter.
        If you want to exclude grains, you can set the `exclude` parameter to `True`.
        This will invert the selection.

        :return: Filter class

        Example:
        todo
        """
        return Filters(self)

    def get(self):
        raise NotImplementedError("Get class not implemented yet.")

    @property
    def reference(self):
        """Return the reference class initialized with current database.

        Various routines are implemented, e.g., to return references for each
        grain as a table, or to return references as a set,
        which can be useful to ensure the original authors are cited
        when you use the database. For a quick overview, you can also simply
        print the reference representation of the grains.

        :return: Reference class

        Example:
        todo
        """
        return References(self)

    @property
    def technique(self):
        """Return the technique class initialized with the current database

        Various routines are implemented, e.g., to return technques for each
        grain as a table, or to return techniques as a set,
        which can be useful to ensure the original authors are cited
        when you use the database. For a quick overview, you can also simply
        print the technique representation of the grains.

        :return: Technique class

        Example:
        todo
        """
        return Techniques(self)

    def _header(self, iso1: str, iso2: str) -> "pgdtools.sub_tools.headers.Headers":
        """Access the headers class for a given isotope ratio.

        :param iso1: Nominator isotope.
        :param iso2: Denominator isotope.

        :return: Headers class
        """
        return pgdtools.sub_tools.headers.Headers(self, iso1, iso2)

    # METHODS #

    def reset(self):
        """Reset the database."""
        self.db = self._db.copy(deep=True)
