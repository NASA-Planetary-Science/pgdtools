"""Tools to read and work with the presolar grain database."""

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd


MODULE_PATH = Path(__file__).parent


class PresolarGrains:
    def __init__(self, fname: str = "PGD_SiC_2021-01-10.csv"):
        """Initialize the presolar grain class.

        Load the database into self.db and self._db as a backup

        :param fname: file name of csv file for database, default to most recent csv
            file in data folder. File must be in the data folder.
        """
        filepath = MODULE_PATH.joinpath(f"data/{fname}")
        self.db = pd.read_csv(filepath, index_col=0)
        self._db = self.db.copy(deep=True)

    # PROPERTIES #

    @property
    def reference(self) -> pd.DataFrame:
        """Return a pandas dataframe with grain references of all entries."""
        hdr = ["Reference"]
        return self.db[hdr]

    # METHODS #

    def filter_value(
        self, value: float, iso1: str, iso2: str, comparator: str, err=False
    ):
        """Filter an isotope ratio (iso1 / iso2) for a given value.

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

        :raise ValueError: Comparator is invalid

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

        # evaluate
        self.db = self.db[eval(f"self.db[hdr] {comp_dict[comparator]} {value}")]

    def filter_type(self, grain_type):
        """Filter grain database by grain type.

        :param grain_type: Grain type.
        :type grain_type: str, List[str]
        """
        if isinstance(grain_type, str):
            grain_type = [grain_type]

        self.db = self.db[self.db["PGD Type"].isin(grain_type)]

    def header_ratio(self, iso1: str, iso2: str) -> Tuple[str, bool]:
        """Check if isotope ratio is available and return it plus additional info.

        :param iso1: Nominator isotope, in format "Si-30"
        :type iso1: str
        :param iso2: Denominator isotope, in format "Si-28"
        :type iso2: str

        :return: name of ratio if exists or "none", Ratio is delta (bool)
        :rtype: Tuple[str, bool]
        """
        header = list(self.db.columns.values)

        isos = (create_db_iso(iso1), create_db_iso(iso2))

        # test delta
        hdr_ratio = f"{isos[0]}/{isos[1]}"
        hdr_delta = f"d({hdr_ratio})"
        if hdr_delta in header:
            delta = True
            hdr = hdr_delta
        elif hdr_ratio in header:
            delta = False
            hdr = hdr_ratio
        else:
            return "none", False

        return hdr, delta

    def reset(self):
        """Reset the database."""
        self.db = self._db.copy(deep=True)

    def return_ratios(
        self, isos1: Tuple[str, str], isos2: Tuple[str, str]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Grab ratios to plot after all the filtering was done.

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
        hdr_x = self.header_ratio(isos1[0], isos1[1])[0]
        hdr_y = self.header_ratio(isos2[0], isos2[1])[0]
        hdr_x_err = [f"err[{hdr_x}]"]
        hdr_y_err = [f"err[{hdr_y}]"]

        # check if we have symmetric or asymmetric errors
        if hdr_x_err[0] not in self.db.columns:
            hdr_x_err = [f"err-[{hdr_x}]", f"err+[{hdr_x}]"]
        if hdr_y_err[0] not in self.db.columns:
            hdr_y_err = [f"err-[{hdr_y}]", f"err+[{hdr_y}]"]

        columns = [hdr_x, hdr_y] + hdr_x_err + hdr_y_err

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
    iso_split = iso.split("-")
    return iso_split[1] + iso_split[0]


if __name__ == "__main__":
    a = PresolarGrains()
    a.filter_type("M")
    # a.filter_value(10.0, "Si-29", "Si-28", comparator="<=", err=True)
    # a.filter_value(10.0, "Si-30", "Si-28", comparator="<=", err=True)
    # print(a.return_ratios(("Si-30", "Si-28"), ("Si-29", "Si-28")))
