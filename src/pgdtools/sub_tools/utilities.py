"""Utilities for all tool modules in pgdtools."""

from typing import Iterable


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

    @property
    def html(self) -> str:
        """Return the element symbol in html format.

        :return: Element symbol in html format.
        """
        if self.a != 0:
            return f"<sup>{self.a}</sup>{self.ele}"
        else:
            return self.ele

    @property
    def latex(self) -> str:
        """Return the element symbol in LaTeX format.

        :return: Element symbol in LaTeX format.
        """
        if self.a != 0:
            return f"^{{{self.a}}}\\mathrm{{{self.ele}}}"
        else:
            return self.ele

    def _parse_isotope(self) -> None:
        """Parse the isotope string and return the element and atomic number.

        :return: Element and atomic number.
        """
        self._ele = "".join([i for i in self._iso_in if i.isalpha()]).capitalize()
        try:
            self._a = int("".join([i for i in self._iso_in if i.isdigit()]))
        except ValueError:
            self._a = 0


def check_iso_rat(rat: Iterable[str]) -> None:
    """Checks an isotope ratio tuple consisting of two strings for errors.

    :param rat: Isotope ratio tuple consisting of two strings.
    """
    if len(rat) != 2:
        raise ValueError("Isotope ratio names must be a tuple of length 2.")

    for iso in rat:
        Isotope(iso)  # raised errors will be passed through
