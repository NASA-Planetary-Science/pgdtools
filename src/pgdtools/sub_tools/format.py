"""Sub tool to format header infor, etc."""

from typing import Tuple


import pgdtools
import pgdtools.sub_tools.utilities as utl


class Format:
    """Formatting class.

    Default formatting for strings are in LaTeX notation. These can directly be used,
    e.g., with matplotlib.
    """

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the Format class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent

    def ratio(self, rat: Tuple[str, str]) -> str:
        """Format an isotope ratio header in html style.

        This can, e.g,. directly be used as an axis label for a plot.

        :param rat: Isotope ratio to filter the data set on. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").

        :return: Formatted isotope ratio header.
        """
        _, delta = self._get_and_check_hdr_ratio(rat)
        iso1 = utl.Isotope(rat[0])
        iso2 = utl.Isotope(rat[1])

        if delta:
            out_str = f"$\\delta({iso1.latex}/{iso2.latex})\\quad(‰)$"
        else:
            out_str = f"${iso1.latex}/{iso2.latex}$"
        return out_str

    def _get_and_check_hdr_ratio(self, rat: Tuple[str, str]):
        """Get the header ratio for a given isotope ratio.

        :param rat: Isotope ratio to filter the data set on. Tuple of two strings.
            Each string represents an isotope. Example: ("29Si", "28Si").

        :return: Header information for the given isotope ratio.

        :raise ValueError: Ratio tuple does not contain two strings.
            Isotope ratio is not found in the header.
        """
        utl.check_iso_rat(rat)

        iso1, iso2 = rat
        hdr = self.parent._header(iso1, iso2).ratio
        if hdr is None:
            raise ValueError(f"Isotope ratio {iso1}/{iso2} not found in the header.")
        else:
            return hdr
