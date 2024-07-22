"""Sub tool to add filtering capabilities."""

from typing import List, Union

import pgdtools


class Filters:
    """Filtering class to filter the data set.

    Note that this class will filter the dataset in the parent class!
    """

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the Filters class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent

    def pgd_id(self, ids: Union[str, List[str]], exclude: bool = False) -> None:
        """Filter the data set based on PGD IDs.

        :param ids: PGD ID (single or multiple) to filter the data set on.
        :param exclude: Exclude the given IDs from the data set.
        """
        if isinstance(ids, str):
            ids = [ids]
        if exclude:
            self.parent.db = self.parent.db[~self.parent.db.index.isin(ids)]
        else:
            self.parent.db = self.parent.db.loc[ids]

    def pgd_type(self, tp: Union[str, List[str]], exclude: bool = False) -> None:
        """Filter for a given PGD type or types.

        :param tp: PGD type or types to filter the data set on.
        :param exclude: Exclude the given types from the
        """
        self._filter_column("PGD Type", tp, exclude)

    def pgd_subtype(self, st: Union[str, List[str]], exclude: bool = False) -> None:
        """Filter for a given PGD subtype or subtypes.

        :param st: PGD subtype or subtypes to filter the data set on.
        :param exclude: Exclude the given subtypes from the data set.
        """
        self._filter_column("PGD Subtype", st, exclude)

    def reset(self) -> None:
        """Reset all the filters and re-instate the original database.

        Alternatively, this can also be done directly from the parent class by using
        the `reset` method.
        """
        self.parent.reset()

    def _filter_column(
        self, column: str, value: Union[str, List[str]], exclude: bool
    ) -> None:
        """Filter the data set based on a given column.

        :param column: Column to filter the data set on.
        :param value: Value or values to filter the data set on.
        :param exclude: Exclude the given values from the data set.
        """
        if isinstance(value, str):
            value = [value]
        if exclude:
            self.parent.db = self.parent.db[~self.parent.db[column].isin(value)]
        else:
            self.parent.db = self.parent.db[self.parent.db[column].isin(value)]
