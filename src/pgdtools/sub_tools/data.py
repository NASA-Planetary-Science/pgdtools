"""Sub tool to retrieve data from the filtered database."""

from typing import List, Tuple, Union

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
        Note that `Size a (µm)` is always the longer or average reported dimensions.
        `Size b (µm)` is either the shorter dimension or - if not available in the
        database, set equal here to `Size a`.

        :return: Two columns of size information.
        """
        ret_db = self.parent.db[["Size a (µm)", "Size b (µm)"]].copy()
        ret_db["Size b (µm)"] = ret_db["Size b (µm)"].fillna(ret_db["Size a (µm)"])
        return ret_db

    # METHODS

    def ratio(
        self, rat: Tuple[str, str], dropnan: bool = True
    ) -> Tuple[
        pd.Series,
        pd.Series,
        pd.Series,
    ]:
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
            df = df.dropna(how="all")

        ret_ratio = df[iso_rat]

        unc_sym = df[iso_unc_none[0]] if iso_unc_none[0] else None
        if iso_unc_none[1] is not None:
            ret_uncp = df[iso_unc_none[1]].copy()
            if unc_sym is not None:  # so we have symmetric and asymmetric errs
                ret_uncp.where(ret_uncp.notna(), unc_sym, inplace=True)
        else:
            ret_uncp = unc_sym.copy()
            ret_uncp.name = ret_uncp.name.replace("err", "err+")

        if iso_unc_none[2] is not None:
            ret_uncn = df[iso_unc_none[2]].copy()
            if unc_sym is not None:
                ret_uncn.where(ret_uncn.notna(), unc_sym, inplace=True)
        else:
            ret_uncn = unc_sym.copy()
            ret_uncn.name = ret_uncn.name.replace("err", "err-")

        return ret_ratio, ret_uncp, ret_uncn

    def ratios(
        self,
        rat: List[Union[str, Tuple[str, str]]],
        dropnan: bool = True,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Get multiple isotope ratios, even for whole elements.

        This function retrieves multiple isotope ratios from the database. It can
        also retrieve isotope ratios for a whole element, e.g., "Si" for all Si
        isotope ratios. The function returns a dataframe with the isotope ratios,
        and a dataframe with the uncertainties.

        FIXME: Currently uncertainties for graphite/SiC mix grains, e.g., for N isotopes
        would be returned with three error columns (err+,err- for SiC, err for graphite).

        :param rat: List of isotope ratios to retrieve. Each ratio can be a string
            for an element (e.g., "Si") or a tuple of two strings for an isotope
            ratio (e.g., ("29Si", "28Si")).
        :param dropnan: Drop rows that have NaN values for all isotopes.
            Defaults to `True`.

        :return: A tuple of two dataframes: The first dataframe contains all the
            data for the given isotope ratios. The second dataframe contains
            all the uncertainties. Note that while they are ordered the same,
            the uncertainties dataframe might contain more columns than the value
            dataframe, as for certain isotope ratios asymmetric errors are available.
        """
        if isinstance(rat, str):
            rat = [rat]

        headers = []
        for rt in rat:
            if isinstance(rt, str):  # a whole element!
                ele_ratios = self.parent.info.ratios(rt, no_print=True)
                for entry in ele_ratios:
                    isos_tpl = pgdtools.sub_tools.headers.get_iso_ratio_from_hdr(
                        entry[0]
                    )
                    headers.append(self.parent._header(*isos_tpl))
            else:
                if len(rt) != 2:
                    raise ValueError("Isotope ratio names must be a tuple of length 2.")
                headers.append(self.parent._header(rt[0], rt[1]))

        hdr_ratios = [h.ratio[0] for h in headers]
        hdr_uncertainties = []
        for h in headers:
            [hdr_uncertainties.append(u) for u in h.uncertainty if u is not None]

        data_df = self.parent.db[hdr_ratios].copy(deep=True)
        unc_df = self.parent.db[hdr_uncertainties].copy(deep=True)

        if dropnan:
            unc_df = unc_df.dropna(axis=1, how="all")
            data_df = data_df.dropna(how="all")
            unc_df = unc_df.dropna(how="all")

        return data_df, unc_df

    def ratio_xy(
        self, rat_x: Tuple[str, str], rat_y: Tuple[str, str], simplify_unc=False
    ) -> Tuple[
        pd.Series,
        Union[pd.Series, pd.DataFrame],
        pd.Series,
        Union[pd.Series, pd.DataFrame],
        Union[None, pd.Series],
    ]:
        """Retrieve two isotope ratios and their respective uncertainties.

        This function is similar to the `ratio` function. It drops all NaNs, i.e.,
        all rows that do not contain values for the wanted x and y ratio. This makes
        this function, as the name implies, very useful for plotting.

        :param rat_x: Isotope ratio to get for x-axis of plot. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").
        :param rat_y: Isotope ratio to get for y-axis of plot. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").
        :param simplify_unc: By default, uncertainties are returned as asymmetric
            errors. This would return a dataframe with two columns.
            However, if `simplify_unc` is set to `True` and both columns are identical,
            a Series will be returned with only one column.

        :return: This function returns a tuple with various Series or Dataframes.
            1. The values for `rat_x`
            2. The uncertainties for `rat_x`, either as a dataframe (asymmetric) or
                as a Series (symmetric, see `simplify_unc=True`).
            3. The values for `rat_y`
            4. The uncertainties for `rat_y`, either as a dataframe (asymmetric) or
                as a Series (symmetric, see `simplify_unc=True`).
            5. The correlation coefficient between the `x` and `y` axis, if available,
                as a Series. Otherwise, `None` is returned. If the correlation column
                is available but no values have been reported (i.e., entries are left
                empty), these empties are replaced with 0 (no correlation).
        """
        dat_x = self.ratio(rat_x, dropnan=False)
        dat_y = self.ratio(rat_y, dropnan=False)

        corr_header = self.parent._header(rat_x[0], rat_y[0]).correlation
        corr_ser = self.parent.db[corr_header] if corr_header is not None else None

        df = pd.DataFrame(dat_x + dat_y).transpose()
        if corr_ser is not None:
            df = df.join(corr_ser.fillna(0).to_frame())

        df = df.dropna()

        xdat = df.iloc[:, 0]
        ydat = df.iloc[:, 3]
        xunc = df.iloc[:, [1, 2]]
        yunc = df.iloc[:, [4, 5]]
        corr = None if corr_ser is None else df.iloc[:, 6]

        if simplify_unc:
            if xunc.iloc[:, 0].equals(xunc.iloc[:, 1]):
                xunc = xunc.iloc[:, 0]
                xunc.name = xunc.name.replace("err+", "err")
            if yunc.iloc[:, 0].equals(yunc.iloc[:, 1]):
                yunc = yunc.iloc[:, 0]
                yunc.name = yunc.name.replace("err-", "err")

        return xdat, xunc, ydat, yunc, corr
