"""Tools to read and work with the presolar grain database."""

from typing import List, Tuple, Union

from iniabu import ini
import numpy as np
import pandas as pd

from pgdtools import db, utilities as utils


class PresolarGrains:
    """Presolar grain database class.

    This class is the main class to work with the presolar grain database.

    Attention: Only SiC grains are currently supported!

    Example:
        Todo
    """

    def __init__(self):
        """Initialize the presolar grain class.

        Load the default database into self.db and self._db as a backup.
        """
        try:
            filepath = db.current()["sic"]
        except FileNotFoundError:
            print("No default database found, downloading latest versions...")
            db.update()
            filepath = db.current()["sic"]

        self.db = pd.read_csv(filepath, index_col=0)
        self._db = self.db.copy(deep=True)

    class Grain:
        """Class to represent a single grain."""

        def __init__(self, parent: "PresolarGrains", id: str):
            """Initialize the class for a single grain.

            :param parent: Parent class, must be of type ``PresolarGrains``.
            :param id: PGD ID of the grain to initialize, or list of IDs.

            :raises TypeError: Parent class is not of type ``PresolarGrains``.
            """
            if not isinstance(parent, PresolarGrains):
                raise TypeError("Parent class must be of type PresolarGrains.")

            self.parent = parent
            self._id = id

            self._entry = self.parent.db.loc[self._id]

        @property
        def entry(self) -> Union[pd.Series, pd.DataFrame]:
            """Return the whole data set of this entry.

            If only one entry is in dataframe, a pandas series is returned.

            :return: Data set of the grain.
            """
            if self._entry.shape[0] == 1:  # A Series
                ret_val = self._entry.iloc[0]
            else:
                ret_val = self._entry
            return ret_val

        @property
        def id(self):
            """Return the PGD ID of the grain."""
            return utils.return_list_simplifier(self._id)

        @property
        def pgd_type(self) -> Union[Tuple[str, str], Tuple[pd.Series, pd.Series]]:
            """Return the PGD type and subtype of the grain(s).

            :return: PGD type and subtype. If no subtype, returns ``NaN``.
            """
            subtype = self._entry["PGD Subtype"]
            if isinstance(subtype, pd.Series):
                subtype.replace({np.nan: None}, inplace=True)
            elif subtype == np.nan:
                subtype = None
            return (
                utils.return_list_simplifier(self._entry["PGD Type"]),
                utils.return_list_simplifier(subtype),
            )

        @property
        def probabilities(self) -> dict:
            """Return the probabilities for all types for a given grain.

            The probabilities are returned as a dictionary with key values of all types,
            namely M, X, Y, Z, AB, C, D, and N. The values are the probabilities for
            the given grain to be of the given type. See the paper for detail.

            :return: Probabilities for all types.
            """
            ret_dict = {}
            for pgd_type in ["M", "X", "Y", "Z", "AB", "C", "D", "N"]:
                ret_dict[pgd_type] = utils.return_list_simplifier(
                    self._entry[f"p({pgd_type})"]
                )
            return ret_dict

        @property
        def reference(self) -> Union[str, pd.Series]:
            """Return the reference of the grain."""
            return utils.return_list_simplifier(self._entry["Reference"])

        @property
        def source(self) -> str:
            """Return the source of the grain."""
            return str(utils.return_list_simplifier(self._entry["Source"]))

        def correlation(self, iso1: str, iso2: str) -> Union[float, pd.Series]:
            """Return the correlation between two isotopes.

            If no correlation is recorded, zero is returned (no correlation).

            :param iso1: First isotope.
            :param iso2: Second isotope.

            :return: Correlation between the two isotopes.
            """
            corr = self._entry[self.parent.header_correlation(iso1, iso2)]
            if isinstance(corr, pd.Series):
                corr.replace({np.nan: 0}, inplace=True)
            elif corr == np.nan:
                corr = 0
            return corr

        def value(self, iso1: str, iso2: str) -> Union[
            Tuple[float, Union[float, Tuple[float, float]], bool],
            Tuple[pd.Series, Union[pd.Series, Tuple[pd.Series, pd.Series]], bool],
        ]:
            """Return the value stored isotope ratio.

            If no value is recorded, ``NaN`` is returned.

            :param iso1: Nominator isotope.
            :param iso2: Denominator isotope.

            :return: value, sigma or (sigma+, sigma-), is_delta?
            """
            hdr, err, is_delta = self.parent.header_ratio(iso1, iso2)
            if isinstance(err, Tuple):
                errors = utils.return_list_simplifier(
                    self._entry[err[0]]
                ), utils.return_list_simplifier(self._entry[err[1]])
            else:
                errors = utils.return_list_simplifier(self._entry[err])
            return utils.return_list_simplifier(self._entry[hdr]), errors, is_delta

    # PROPERTIES #

    @property
    def grain(self):
        """Return instance for (a) specific grain ID(s)."""
        valid_keys = list(self.db.index)
        return utils.ProxyList(self, self.Grain, valid_keys)

    @property
    def reference(self) -> pd.DataFrame:
        """Return a pandas dataframe with grain references of all entries.

        fixme: garbage

        :return: Dataframe with grain references.
        """
        hdr = ["Reference"]
        return self.db[hdr]

    # METHODS #

    def filter_value(
        self, value: float, iso1: str, iso2: str, comparator: str, err=False
    ):
        """Filter an isotope ratio (iso1 / iso2) for a given value.

        fixme: garbage

        Will filter the database such that
        isotope_entry comparator value
        is True for all values.

        :param value: Value to compare with
        :type value: float
        :param iso1: Nominator isotope
        :type iso1: str
        :param iso2: Denominator isotope
        :type iso2: str
        :param comparator: Mathematical comparator to select for
        :type comparator: str
        :param err: Is the filter taking place on errors?
        :type err: bool

        :raises ValueError: Comparator is invalid

        Example to filter d(Si-29/Si-28) > 0.1, all others are out:
            >>> from pgdtools import PresolarGrains
            >>> pg = PresolarGrains()
            >>> pg.filter_value(0.1, "Si-29", "Si-28", ">")
        """
        hdr = self.header_ratio(iso1, iso2)[0]

        if err:
            hdr = f"err[{hdr}]"

        comp_dict = {
            "<": "<",
            ">": ">",
            "<=": "<=",
            "=<": "<=",
            ">=": ">=",
            "=>": ">=",
            "=": "==",
        }

        if comparator not in comp_dict.keys():
            raise ValueError(f"Comparator {comparator} is not valid.")

        # evaluate -- todo: insecure, but garbage anyway
        self.db = self.db[
            eval(f"self.db[hdr] {comp_dict[comparator]} {value}")  # noqa: S307
        ]

    def filter_type(self, grain_type):
        """Filter grain database by grain type.

        fixme: garbage


        :param grain_type: Grain type.
        :type grain_type: str, List[str]
        """
        if isinstance(grain_type, str):
            grain_type = [grain_type]

        self.db = self.db[self.db["PGD Type"].isin(grain_type)]

    def header_correlation(self, iso1: str, iso2: str) -> Union[str, None]:
        """Return the header of the correlation between two isotopes, if available.

        Returns ``None`` if no correlation is available.

        :param iso1: First isotope.
        :param iso2: Second isotope.

        :return: Header of the correlation.
        """
        corr_hdr = f"rho[{create_db_iso(iso1)}-{create_db_iso(iso2)}]"
        header = list(self.db.columns.values)
        if corr_hdr in header:
            return corr_hdr
        else:
            return None

    def header_ratio(
        self, iso1: str, iso2: str
    ) -> Union[Tuple[str, Union[str, Tuple[str, str], bool]], None]:
        """Check if isotope ratio is available and return it plus additional info.

        :param iso1: Nominator isotope, in format "Si-30"
        :param iso2: Denominator isotope, in format "Si-28"

        :return: name of ratio, name of sigma or (name of sigma+, name of sigma-),
            is delta?
        """
        header = list(self.db.columns.values)

        isos = (create_db_iso(iso1), create_db_iso(iso2))

        # check for delta
        hdr_ratio = f"{isos[0]}/{isos[1]}"
        hdr_delta = f"d({hdr_ratio})"
        if hdr_delta in header:
            delta = True
            hdr = hdr_delta
        elif hdr_ratio in header:
            delta = False
            hdr = hdr_ratio
        else:
            return None

        # get errors
        hdr_err = f"err[{hdr}]"
        if hdr_err not in header:
            hdr_err = f"err+[{hdr}]", f"err-[{hdr}]"

        return hdr, hdr_err, delta

    def reset(self):
        """Reset the database."""
        self.db = self._db.copy(deep=True)

    def return_ratios(
        self, isos1: Tuple[str, str], isos2: Tuple[str, str]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Grab ratios to plot after all the filtering was done.

        fixme: garbage


        This routine is mainly thought to get x,y data for plotting. Values that contain
        empties are dropped.

        Fixme: Will always return values and errors, I think all data have values
            and errors
        Fixme: Currently if no errors reported, the whole datapoint is rejected
            with the dropna...

        .. note:: If the database contains asymmetric errors, an array of errors with
            two entries per grain is returned. This array is transposed, such that
            it can be directly used to plot errorbars using ``matplotlib``.

        :param isos1: Isotopes for first axis, as ratio, e.g., ("Si-29", "Si-28")
        :param isos2: Isotopes for first axis, as ratio, e.g., ("Si-30", "Si-28")

        :return: xdata, ydata, xerr, yerr
        """
        hdr_x, hdr_x_err, _ = self.header_ratio(isos1[0], isos1[1])
        hdr_y, hdr_y_err, _ = self.header_ratio(isos2[0], isos2[1])

        columns = [hdr_x, hdr_y] + list(hdr_x_err) + list(hdr_y_err)

        df = self.db[columns].copy()
        df.dropna(inplace=True)

        # x errors to return
        xerr_ret = df[hdr_x_err].to_numpy()
        yerr_ret = df[hdr_y_err].to_numpy()

        return (
            df[hdr_x].to_numpy(),
            df[hdr_y].to_numpy(),
            xerr_ret.transpose() if xerr_ret.shape[1] > 1 else xerr_ret[:, 0],
            yerr_ret.transpose() if yerr_ret.shape[1] > 1 else yerr_ret[:, 0],
        )

    def return_ratios_empty(self, isos: List[str], normiso: str, filter: bool = False):
        """Return isotope ratios for all isotopes, if they exist.

        fixme: garbage


        Entries are only dropped if no data at all exists. Only data with no ratios
        are dropped if none exist. Errors are not part of dropping.

        :param isos: List of isotopes (nominator) to find.
        :param normiso: Normalization isotope for the given list.
        :param filter: Filter the database to drop all other values?

        :return: Ratios for all the data, Errors for all the data.
        """
        hdrs = [self.header_ratio(iso, normiso)[0] for iso in isos]
        # error header
        hdrs_err = []
        for hdr in hdrs:
            if (tmp := f"err[{hdr}]") in self.db.columns:
                hdrs_err.append(tmp)
            else:  # asymmetric errors
                hdrs_err.append([f"err-[{hdr}]", f"err+[{hdr}]"])

        all_cols = hdrs.copy()
        for hdr_err in hdrs_err:
            if isinstance(hdr_err, list):
                all_cols += hdr_err
            else:
                all_cols.append(hdr_err)

        data = self.db[all_cols].copy()
        data.dropna(inplace=True, how="all")  # drop data if all ratios are empty

        # todo: refractor this into its own filter
        if filter:
            self.db = self.db.dropna(subset=all_cols, how="all", axis=0)

        ratios = data[hdrs].copy()

        ratios_list = []
        for hdr in hdrs:
            ratios_list.append(ratios[hdr].to_numpy())

        errors_list = []
        for hdr_err in hdrs_err:
            if not isinstance(hdr_err, list):
                hdr_err = [hdr_err]
            df = data[hdr_err].to_numpy()
            errors_list.append(df.transpose() if df.shape[1] > 1 else df[:, 0])

        return ratios_list, errors_list


def create_db_iso(iso: str) -> str:
    """Create isotope name in database style.

    :param iso: Isotope name, class style, e.g., "Si-28"
    :type iso: str

    :return: Isotope name in database style, e.g., "28Si"
    :rtype: str
    """
    iso_ini = ini.iso[iso]
    iso_split = iso_ini.name.split("-")
    return iso_split[1] + iso_split[0]


if __name__ == "__main__":
    a = PresolarGrains()
    a.filter_type("M")
    # a.filter_value(10.0, "Si-29", "Si-28", comparator="<=", err=True)
    # a.filter_value(10.0, "Si-30", "Si-28", comparator="<=", err=True)
    # print(a.return_ratios(("Si-30", "Si-28"), ("Si-29", "Si-28")))
