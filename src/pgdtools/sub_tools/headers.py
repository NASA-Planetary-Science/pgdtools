"""Sub tool to search the header for information."""

from typing import Tuple, Union

import pgdtools
import pgdtools.sub_tools.utilities as utl


class Headers:
    """Class to search all header information for a isotope ratio."""

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the SearchHeader class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent

    def ratio(self, iso1: str, iso2: str) -> Union[None, Tuple[str, bool]]:
        """Search the header for a given isotope ratio.

        :param iso1: Isotope 1 to search for.
        :param iso2: Isotope 2 to search for.

        :return: Header information for the given isotope ratio: Name and bool if delta.
        """
        iso_rat = self._iso_ratio(iso1, iso2)
        hdrs = [hdr for hdr in self.parent.db.columns if iso_rat in hdr]
        hdr = None
        for hdr in hdrs:
            if "err" not in hdr and "rho" not in hdr:
                break

        if hdr is None:
            return None
        else:
            delta = True if hdr.lower().startswith("d") else False
            return hdr, delta

    def _iso_ratio(self, iso1: str, iso2: str) -> str:
        """Stitch together two isotopes to a ratio string.

        :param iso1: Isotope 1 to search for.
        :param iso2: Isotope 2 to search for.

        :return: Header information for the given isotope ratio.
        """
        iso1 = utl.Isotope(iso1)
        iso2 = utl.Isotope(iso2)
        return f"{iso1}/{iso2}"
