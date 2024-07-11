"""Utilities for all modules in pgdtools."""

from typing import Any, List, Union


def return_string_as_list(s: Any) -> List[Any]:
    """Return the input as a list.

    :param s: Input value.

    :return: List of input value if not a list, otherwise return itself.
    """
    if isinstance(s, list):
        return s
    else:
        return [s]


def return_list_simplifier(return_list: List[Any]) -> Union[Any, List[Any]]:
    """Simplify standard return values.

    Specifically written for classes with multiple return types, such as
    :class:`iniabu.elements.Elements` and :class:`iniabu.isotopes.Isotopes`. If only
    one entry is in the list, it should not be returned as a list but as a value.
    Otherwise, return the list.

    :param return_list: List or numpy array with the value to be returned.

    :return: If only one entry in list, return that entry. Otherwise return list.
    """
    length = len(return_list)
    if length == 0:
        return None
    elif len(return_list) == 1:
        return return_list[0]
    else:
        return return_list
