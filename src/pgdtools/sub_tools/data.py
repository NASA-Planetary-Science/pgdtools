"""Sub tool to retrieve data from the filtered database."""

from typing import Tuple

import pandas as pd

import pgdtools


class Data:
    """Data retrieving class.

    By default, the length of any the returned data is not necessarily the same as the
    length of the parent class database. This is because empty values are filtered out.
    For certain methods you can specify `dropnan=False` in order to avoid this
    behavior. Properties that automatically drop empty values generally have a
    `NAME_all` in addition that do not drop empty values.
     See the documentation of individual routines to see how data are filtered.
    """

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the Data class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent

    @property
    def notes(self):
        """Retrieve the notes from the filtered database.

        Note: Values with empty notes will be dropped. To avoid this, use
        the `notes_all` property.

        :return: Series with notes. Index is the PGD ID.
        """
        return self.notes_all.dropna()

    @property
    def notes_all(self) -> pd.Series:
        """Retrieve the notes from the filtered database.

        Note: This routine does not drop any values, even if no notes are present.

        :return: Series with notes. Index is the PGD ID.
        """
        return self.parent.db["Notes"]

    @property
    def size(self) -> pd.DataFrame:
        """Retrieve the size data from the filtered database.

        This retrieves the grain sizes in µm from the presolar grain database.
        Two columns are returned, "Size a" and "Size b".

        Note: This routine will drop the rows that have no size information.
        Note that `Size a (µm)` is always the longer or average reported dimesnions.
        `Size b (µm)` is either the shorter dimension or - if not available in the
        database, set equal here to `Size a`.

        :return: Two columns of size information.
        """
        return self.size_all.dropna(how="all")

    @property
    def size_all(self) -> pd.DataFrame:
        """Retrieve the size data from the filtered database.

        This retrieves the grain sizes in µm from the presolar grain database.
        Two columns are returned, "Size a" and "Size b".

        Note: This routine does not drop any values, even if no size information is
        present.
        Note that `Size a (µm)` is always the longer or average reported dimesnions.
        `Size b (µm)` is either the shorter dimension or - if not available in the
        database, set equal here to `Size a`.

        :return: Two columns of size information.
        """
        ret_db = self.parent.db[["Size a (µm)", "Size b (µm)"]]
        ret_db["Size b (µm)"].where(
            ret_db["Size b (µm)"].notna(), ret_db["Size a (µm)"], inplace=True
        )
        return ret_db

    # METHODS

    def ratio(self, rat: Tuple[str, str], dropnan: bool = True) -> Tuple[pd.Series]:
        """Retrieve a given isotope ratio from the database.

        :param rat: Isotope ratio to retrieve. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").
        :param dropnan: Drop rows with NaN values for the given isotope ratio.
            Defaults to `True`.

        :return: Series with the isotope ratio.
        """
        if len(rat) != 2:
            raise ValueError("Isotope ratio names must be a tuple of length 2.")

        parent_header = self.parent._header(rat[0], rat[1])
        iso_rat, _ = parent_header.ratio
        iso_unc_none = parent_header.uncertainty
        iso_unc = [v for v in iso_unc_none if v is not None]

        if iso_rat is None:
            raise ValueError(
                f"Isotope ratio {rat[0]}/{rat[1]} not available in the database."
            )

        all_hdrs = [iso_rat] + iso_unc

        df = self.parent.db[all_hdrs]

        if dropnan:
            df.dropna(how="all")

        ret_ratio = df[iso_rat]

        unc_sym = df[iso_unc_none[0]] if iso_unc_none[0] else None
        if iso_unc_none[1] is not None:
            ret_uncp = df[iso_unc_none[1]]
            if unc_sym is not None:  # so we have symmetric and asymmetric errs
                ret_uncp.where(ret_uncp.notna(), unc_sym, inplace=True)
        else:
            ret_uncp = unc_sym

        if iso_unc_none[2] is not None:
            ret_uncn = df[iso_unc_none[2]]
            if unc_sym is not None:
                ret_uncn.where(ret_uncn.notna(), unc_sym, inplace=True)
        else:
            ret_uncn = unc_sym

        return ret_ratio, ret_uncp, ret_uncn
