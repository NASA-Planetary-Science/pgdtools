"""Sub tool to add filtering capabilities."""

from typing import List, Union, Tuple

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

    def db(
        self,
        dbs: Union[
            "pgdtools.PresolarGrains.DataBase", List["pgdtools.PresolarGrains.DataBase"]
        ],
        exclude: bool = False,
    ) -> None:
        """Filter out a specific database.

        :param dbs: Database or databases to filter the data set on.
        :param exclude: Exclude the given databases from the data set.

        :raises TypeError: Database is not of type PresolarGrains.DataBase.
        """
        if not isinstance(dbs, List):
            dbs = [dbs]

        if not all(isinstance(db, pgdtools.PresolarGrains.DataBase) for db in dbs):
            raise TypeError("Database must be of type PresolarGrains.DataBase.")

        if exclude:
            self.parent.db = self.parent.db[
                ~self.parent.db.index.to_series().apply(
                    lambda x: any(x.startswith(db.value) for db in dbs)
                )
            ]
        else:
            self.parent.db = self.parent.db[
                self.parent.db.index.to_series().apply(
                    lambda x: any(x.startswith(db.value) for db in dbs)
                )
            ]

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

        Note: Empty values are not dropped if `exclude` is set to `True`.

        :param st: PGD subtype or subtypes to filter the data set on.
        :param exclude: Exclude the given subtypes from the data set.
        """
        self._filter_column("PGD Subtype", st, exclude)

    def ratio(
        self, rat: Tuple[str, str], cmp: str, value: float, exclude: bool = False
    ) -> None:
        """Filter the data set based on a given isotope ratio.

        Here, a given isotope ratio is filtered based on a comparator and a value.
        Some error checking is done on the comparator to ensure that it is valid.

        Note: rows with NaN values for the given comparator will be dropped
        from the dataset before filtering. This behavior is independent of the value
        of `exclude`.

        :param rat: Isotope ratio to filter the data set on. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").
        :param cmp: Comparison operator to use. Available operators are:
            "<", "<=", ">", ">=", "==", "!=".
        :param value: Value to compare the isotope ratio against.
        :param exclude: Exclude the given isotope ratio value range from the data set.

        :raises ValueError: Invalid comparator or
            isotope ratio names are not valid, not of length 2, or the chosen
            isotope ratio is not available in the database.
        """
        cmp = _check_comparator(cmp)

        if not isinstance(rat, tuple):
            rat = tuple(rat)

        if len(rat) != 2:
            raise ValueError("Isotope ratio names must be a tuple of length 2.")

        try:
            iso_rat = self.parent._header(rat[0], rat[1]).ratio
        except ValueError as err:
            raise ValueError(
                "Isotope names {rat[0]} and/or {rat[1]} are invalid."
            ) from err

        if iso_rat is None:
            raise ValueError(
                f"Isotope ratio {rat[0]}/{rat[1]} not available in the database."
            )

        # drop rows with NaN values for the given isotope ratio
        self.parent.db.dropna(subset=[iso_rat[0]], inplace=True)

        if exclude:
            self.parent.db = self.parent.db[
                ~self.parent.db[iso_rat[0]].apply(lambda x: eval(f"x {cmp} {value}"))
            ]
        else:
            self.parent.db = self.parent.db[
                self.parent.db[iso_rat[0]].apply(lambda x: eval(f"x {cmp} {value}"))
            ]

    def uncertainty(
        self, rat: Tuple[str, str], cmp: str, value: float, exclude: bool = False
    ) -> None:
        """Filter the data set based on a given uncertainty of an isotope ratio.

        Here, a given uncertainty is filtered based on a comparator and a value.
        Some error checking is done on the comparator to ensure that it is valid.

        Note: rows with NaN values for the given comparator will be dropped
        from the dataset before filtering. This behavior is independent of the value
        of `exclude`.

        :param rat: Isotope ratio to filter the data set on. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").
        :param cmp: Comparison operator to use. Available operators are:
            "<", "<=", ">", ">=", "==", "!=".
        :param value: Value to compare the isotope ratio against.
        :param exclude: Exclude the given isotope ratio value range from the data set.

        :raises ValueError: Invalid comparator or
            isotope ratio names are not valid, not of length 2, or the chosen
            isotope ratio is not available in the database.
        """
        cmp = _check_comparator(cmp)

        if not isinstance(rat, tuple):
            rat = tuple(rat)

        if len(rat) != 2:
            raise ValueError(
                "Isotope names for ratio uncertainty must be a tuple of length 2."
            )

        try:
            iso_unc = self.parent._header(rat[0], rat[1]).uncertainty
        except ValueError as err:
            raise ValueError(
                "Isotope names for uncertainty {rat[0]} and/or {rat[1]} are invalid."
            ) from err

        if all(v is None for v in iso_unc):
            raise ValueError(
                f"Uncertainty for isotope ratio {rat[0]}/{rat[1]} "
                f"not available in the database."
            )

        iso_unc = [v for v in iso_unc if v is not None]

        # drop rows with NaN values for the given isotope ratio
        self.parent.db.dropna(subset=iso_unc, how="all", inplace=True)

        number_of_values = (~self.parent.db[iso_unc].isna()).sum(axis=1)

        if exclude:
            self.parent.db = self.parent.db[
                ~(
                    self.parent.db[iso_unc]
                    .apply(lambda x: eval(f"x {cmp} {value}"))
                    .sum(axis=1)
                    > 0
                )
            ]
        else:
            self.parent.db = self.parent.db[
                self.parent.db[iso_unc]
                .apply(lambda x: eval(f"x {cmp} {value}"))
                .sum(axis=1)
                == number_of_values
            ]

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


def _check_comparator(cmp: str) -> Union[str, None]:
    """Check comparator for validity and correct if necessary and possible.

    If the comparator is not valid, a ValueError is raised.

    :param cmp: Comparator to check.

    :return: Corrected comparator if possible.

    :raises ValueError: Invalid comparator.
    """
    if cmp in ("<", "<=", ">", ">=", "==", "!="):
        return cmp
    elif cmp == "=":
        return "=="
    elif cmp == "<>":
        return "!="
    elif cmp == "=>":
        return ">="
    elif cmp == "=<":
        return "<="
    else:
        raise ValueError("Invalid comparator. Please use one of: <, <=, >, >=, ==, !=")