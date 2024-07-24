"""Sub tool to search the header for information."""

from typing import List, Tuple, Union

import pgdtools
import pgdtools.sub_tools.utilities as utl


class Headers:
    """Class to search all header information for an isotope ratio."""

    def __init__(self, parent: "pgdtools.PresolarGrains", iso1: str, iso2: str) -> None:
        """Initialize the SearchHeader class.

        :param parent: Parent class, must be of type ``PresolarGrains``.
        :param iso1: Isotope 1 (nominator).
        :param iso2: Isotope 2 (denominator).

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent
        self.iso1 = utl.Isotope(iso1)
        self.iso2 = utl.Isotope(iso2)

    @property
    def correlation(self) -> Union[None, str]:
        """Search the header for a given isotope correlation.

        If the correlation is not found in the header, return `None`.

        :return: Header information for the given isotope correlation.
        """
        search_str = f"rho[{self.iso1}-{self.iso2}]"
        return search_str if search_str in self.parent.db.columns else None

    @property
    def ratio(self) -> Tuple[str, bool]:
        """Search the header for a given isotope ratio.

        If the header is not found, None is returned.

        :return: Header information for the given isotope ratio: Name and bool if delta.

        :raise ValueError: Isotope ratio not found in header.
        """
        iso_rat = self._iso_ratio
        hdrs = [hdr for hdr in self.parent.db.columns if iso_rat in hdr]
        hdr = None
        for hdr in hdrs:
            if "err" not in hdr and "rho" not in hdr:
                break

        if hdr is None:
            raise ValueError(f"Isotope ratio {iso_rat} not found in header.")
        else:
            delta = True if hdr.lower().startswith("d") else False
            return hdr, delta

    @property
    def uncertainty(self) -> List[Union[str, None]]:
        """Search the header for uncertainty of a given isotope ratio.

        If the errors are not found, a tuple of three None values is returned.

        :return: Header information for the given isotope ratio:
            - Symmetric error (if available) or None.
            - Asymmetric error (+) (if available) or None.
            - Asymmetric error (-) (if available) or None.

        :raise ValueError: No uncertainties found.
        """
        iso_rat = self._iso_ratio
        hdrs = [hdr for hdr in self.parent.db.columns if iso_rat in hdr]
        return_hdr = [None, None, None]

        for hdr in hdrs:
            if "err[" in hdr:
                return_hdr[0] = hdr
            elif "err+[" in hdr:
                return_hdr[1] = hdr
            elif "err-[" in hdr:
                return_hdr[2] = hdr

        if all(v is None for v in return_hdr):
            raise ValueError(
                f"No uncertainties found in header for isotope ratio {iso_rat}."
            )

        return return_hdr

    @property
    def _iso_ratio(self) -> str:
        """Stitch together two isotopes to a ratio string.

        :param iso1: Isotope 1 (nominator).
        :param iso2: Isotope 2 (denominator).

        :return: Correct formatting for finding given isotope ratio.
        """
        return f"{self.iso1}/{self.iso2}"
