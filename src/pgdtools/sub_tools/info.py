"""Sub tool to add information querying capabilities."""

from typing import List, Union, Set, Tuple

import pgdtools
import pgdtools.sub_tools.utilities as utl


class Info:
    """Class to obtain information about the database.

    Note: This class will print and return values.
    """

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the Info class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent

    @property
    def dbs(self) -> Tuple["pgdtools.PresolarGrains.DataBase", ...]:
        """Get/print what databases are currently in the selection."""
        index_start = set()
        for ind in self.parent.db.index:
            index_start.add(ind.split("-")[0])

        dbs = tuple(pgdtools.PresolarGrains.DataBase(x) for x in index_start)
        print("Currently available databases are:")
        if len(dbs) == 0:
            print("- None")
        else:
            for db in dbs:
                print(f"- {db.name}")

        return dbs

    @property
    def number_of_grains(self) -> int:
        """Get/print how many presolar grains are in the currently filtered database.

        :return: Number of presolar grains.
        """
        nog = len(self.parent)
        print(f"Number of grains in current selection: {nog}")
        return nog

    @property
    def pgd_types(self) -> Set[str]:
        """Get/print what PGD types of presolar grains are in the current database.

        :return: List of all PGD grain types available.
        """
        ret_set = set(self.parent.db["PGD Type"].drop_duplicates())

        print("Currently available PGD types in filtered database:")
        if len(ret_set) == 0:
            print("- None")
        else:
            for entry in ret_set:
                print(f"- {entry}")
        return ret_set

    # METHODS #

    def correlations(self, inp: str) -> Union[None, List[str]]:
        """Get/print available correlations for a given element or isotope."""
        iso = str(utl.Isotope(inp, allow_element=True))

        entries = [
            x for x in self.parent.db.columns if iso in x and x.startswith("rho")
        ]

        if len(entries) == 0:
            print(f"No correlations for {iso} found.")
            return None
        else:
            print(f"Correlations containing {iso}:")
            for entry in entries:
                print(f"- {entry}")
            return entries

    def ratios(self, inp: str) -> Union[None, List[Tuple[str, bool]]]:
        """Get/print available ratios for a given element or isotope.

        :param inp: Input isotope or element.

        :return: A tuple of tuples. In the latter, each entry consists of available
            isotope ratio and a boolean value to indicate if this is a delta-value.
        """
        excl_startswith = ("err", "rho")

        iso = str(utl.Isotope(inp, allow_element=True))
        all_in_hdr = (x for x in self.parent.db.columns if iso in x)
        flt_hdr = [
            (x, x.startswith("d"))
            for x in all_in_hdr
            if all([not x.startswith(y) for y in excl_startswith]) and "/" in x
        ]

        if len(flt_hdr) == 0:
            print(f"No isotope ratios containing {iso} found.")
            return None
        else:
            print(f"Isotope ratios containing {iso}:")
            for entry in flt_hdr:
                print(f"- {entry[0]}, delta value: {entry[1]}")
            return flt_hdr
