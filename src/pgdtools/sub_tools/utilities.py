"""Utilities for all tool modules in pgdtools."""


class Isotope:
    """Class to parse isotope strings and return the element and atomic number."""

    def __init__(self, isotope: str, allow_element=False) -> None:
        """Initialize the Isotope class.

        :param isotope: Isotope string to parse.
        :param allow_element: Allow the input to be only an element symbol. This will
            set the atomic number to 0 and string representation will be just the
            elemental symbol.

        :raises ValueError: Input value is not a string.
        """
        if not isinstance(isotope, str):
            raise ValueError("Input value must be a string.")

        self._iso_in = isotope

        self._parse_isotope()

        a_invalid = self.a == 0 and not allow_element

        if self.ele == "" or a_invalid:
            raise ValueError("Input must contain an element symbol and atomic number.")

    def __repr__(self) -> str:
        """Return a string representation of the class.

        This will return atomic number followed by capitalized element symbol.
        This should be the standard way an isotope is represented in the PGD database.

        :return: String representation of the class.
        """
        if self.a == 0:
            return self.ele
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

    def _parse_isotope(self) -> None:
        """Parse the isotope string and return the element and atomic number.

        :return: Element and atomic number.
        """
        self._ele = "".join([i for i in self._iso_in if i.isalpha()]).capitalize()
        try:
            self._a = int("".join([i for i in self._iso_in if i.isdigit()]))
        except ValueError:
            self._a = 0
