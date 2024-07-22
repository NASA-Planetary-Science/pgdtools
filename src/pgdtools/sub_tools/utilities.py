"""Utilities for all tool modules in pgdtools."""


class Isotope:
    """Class to parse isotope strings and return the element and atomic number."""

    def __init__(self, isotope: str) -> None:
        """Initialize the Isotope class.

        :param isotope: Isotope string to parse.

        :raises ValueError: Input value is not a string.
        """
        if not isinstance(isotope, str):
            raise ValueError("Input value must be a string.")

        self._iso_in = isotope
        self._parse_isotope()

    def _parse_isotope(self) -> None:
        """Parse the isotope string and return the element and atomic number.

        :return: Element and atomic number.
        """
        self._ele = "".join([i for i in self._iso_in if i.isalpha()]).capitalize()
        self._a = int("".join([i for i in self._iso_in if i.isdigit()]))

    def __repr__(self) -> str:
        """Return a string representation of the class.

        This will return atomic number followed by capitalized element symbol.
        This should be the standard way an isotope is represented in the PGD database.

        :return: String representation of the class.
        """
        return f"{self.a}{self.ele}"

    @property
    def a(self) -> int:
        """Return the atomic number.

        :return: Atomic number.
        """
        return self._a

    @property
    def ele(self) -> str:
        """Return the element symbol.

        :return: Element symbol.
        """
        return self._ele
