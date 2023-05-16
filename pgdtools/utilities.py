"""Utilities for all modules in pgdtools."""


class ProxyList:
    """Proxy for accessing elements and isotopes as lists.

    This class is inspired by a class with the same name from the project
    ``InstrumentKit`` by Galvant Industries. It is used to generate lists of objects.
    The valid keys are defined by the `valid_set` initialization parameter. This allows
    generating a single property for elements and isotopes to access them.

    `InstrumentKit <https://github.com/Galvant/InstrumentKit>`_
    """

    def __init__(self, parent, proxy_cls, valid_set, *args, **kwargs):
        """Initialize a ProxyList object.

        :param parent: The "parent" of the proxy classes. In python, this is
            usually `self`
        :type parent: class
        :param proxy_cls: The child class that will be returned when the returned
            object is iterated through.
        :type proxy_cls: class
        :param valid_set: The set of valid keys by which the proxy class objects
            are accessed.
        :type valid_set: list
        :param *args: Variable length argument list.
        :param **kwargs: Arbitrary keyword arguments.
        """
        self._parent = parent
        self._proxy_cls = proxy_cls
        self._valid_set = valid_set

        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        """Yield iterator of the proxy list."""
        for idx in self._valid_set:
            yield self._proxy_cls(self._parent, idx, *self.args, **self.kwargs)

    def __getitem__(self, idx):
        """Get an item from the proxy list."""
        if hasattr(idx, "copy"):
            idx = idx.copy()  # do not modify user input
        # turn idx into a list
        if isinstance(idx, tuple):
            idx = list(idx)
        # turn into list if required
        idx = return_string_as_list(idx)

        for it, entry in enumerate(idx):
            idx[it] = entry
            if entry not in self._valid_set:
                raise IndexError(
                    "Item {} out of range. Must be "
                    "in {}.".format(entry, self._valid_set)
                )
        return self._proxy_cls(self._parent, idx, *self.args, **self.kwargs)

    def __len__(self):
        """Get length of the valid set."""
        return len(self._valid_set)


def return_string_as_list(s):
    """Return the input as a list.

    :param s: Input value.
    :type s: str,list

    :return: List of input value if not a list, otherwise return itself.
    :rtype: list
    """
    if isinstance(s, list):
        return s
    else:
        return [s]


def return_list_simplifier(return_list):
    """Simplify standard return values.

    Specifically written for classes with multiple return types, such as
    :class:`iniabu.elements.Elements` and :class:`iniabu.isotopes.Isotopes`. If only
    one entry is in the list, it should not be returned as a list but as a value.
    Otherwise, return the list.

    :param return_list: List or numpy array with the value to be returned.
    :type return_list: list,ndarray

    :return: If only one entry in list, return that entry. Otherwise return list.
    """
    length = len(return_list)
    if length == 0:
        return None
    elif len(return_list) == 1:
        return return_list[0]
    else:
        return return_list
