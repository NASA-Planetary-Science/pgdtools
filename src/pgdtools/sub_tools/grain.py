"""Sub-class to PresolarGrains to deal with individual grains."""

from typing import List, Tuple, Union

import pandas as pd
import numpy as np

import pgdtools
from pgdtools import utilities as utils


class Grain:
    """Class to represent a single grain."""

    def __init__(self, parent: "pgdtools.PresolarGrains", grain_id: List[str]):
        """Initialize the class for a single grain.

        :param parent: Parent class, must be of type ``PresolarGrains``.
        :param grain_id: PGD ID of the grain to initialize, or list of IDs.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent
        self._id = grain_id

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
        elif np.isnan(subtype):
            subtype = None
        return (
            utils.return_list_simplifier(self._entry["PGD Type"]),
            utils.return_list_simplifier(subtype),
        )

    @property
    def probabilities(self) -> dict:
        """Return the probabilities for all types for a given grain.

        fixme: only really valid for SiC grains

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

    def value(
        self, iso1: str, iso2: str
    ) -> Union[
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
            errors = (
                utils.return_list_simplifier(self._entry[err[0]]),
                utils.return_list_simplifier(self._entry[err[1]]),
            )
        else:
            errors = utils.return_list_simplifier(self._entry[err])
        return utils.return_list_simplifier(self._entry[hdr]), errors, is_delta
