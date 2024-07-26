"""Sub tool to gather used techniques for data sets and return them."""

import itertools
import json
from typing import List, Set
import re

import pandas as pd

import pgdtools
from pgdtools import db


class Techniques:
    """This class handles techniques for specific data sets."""

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the Techniques class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        # list of separators for splitting techniques
        self._separators = ["&", "and/or"]

        self.parent = parent

        self._techniques_json = None
        self._get_techniques_json()

    def __repr__(self) -> str:
        """Return a string representation of the class.

        Simply print out all the PGD techniques, comma separated.

        :return: String representation of the class.
        """
        return ", ".join(self.dict.keys())

    def __eq__(self, other):
        """Check if the techniques are equal.

        Note: This will only check if the set of techniques are equal and has nothing
        to do with the number of grains that are associated with each technique.

        :param other: Other technique set to compare against.

        :return: True if the techniques are equal, otherwise False.
        """
        return self.dict == other.dict

    def __len__(self) -> int:
        """Return the number of individual techniques in the class.

        :return: Number of unique techniques.
        """
        return len(self.dict)

    def __iter__(self):
        """Iterate over the techniques key, value pairs.

        :return: Key, value pairs of the techniques.
        """
        return iter(self.dict.items())

    def __getitem__(self, key: str) -> dict:
        """Get a technique item based on the key.

        :param key: Technique key.

        :return: Technique details.
        """
        return self.dict[key]

    @property
    def dict(self) -> dict:
        """Return a dictionary representation of the techniques.

        The keys are the PGD Techniques and the values are the technique details.
        - Institution
        - Technique
        - Instrument
        - Reference
        - DOI

        :return: Dictionary of techniques.
        """
        return {key: self._techniques_json[key] for key in self._create_ref_keys_set}

    @property
    def table_full(self) -> pd.DataFrame:
        """Return a full techniques table for every individual grain in the database.

        The row indexes of the table are the PGD IDs. The following columns will be
        present:
        - PGD Technique
        - Institution
        - Technique
        - Instrument
        - Reference
        - DOI

        :return: Full reference table for every grain.
        """
        indexes = self.parent.db.index

        series = []
        for ind, key_list in enumerate(self._create_ref_keys_list):
            for key in key_list:
                lst = {"PGD Technique": key}
                lst.update(self._techniques_json[key])
                ser = pd.Series(lst, name=indexes[ind])
                series.append(ser)
        ret_frame = pd.DataFrame(series)

        return ret_frame

    @property
    def table_set(self) -> pd.DataFrame:
        """Return a set of techniques for all grains in dataset in table format."""
        series = [
            pd.Series(self._techniques_json[key], name=key)
            for key in self._create_ref_keys_set
        ]
        ret_frame = pd.DataFrame(series)
        return ret_frame

    @property
    def _create_ref_keys_list(self) -> List[List[str]]:
        """Create the techniques key as a list (in order).

        :return: List of all the reference IDs.
        """
        ref_keys = self.parent.db["Technique"].to_list()
        seps = "|".join(self._separators)
        ret_keys = [[x.strip() for x in re.split(seps, y)] for y in ref_keys]
        return ret_keys

    @property
    def _create_ref_keys_set(self) -> Set[str]:
        """Create the techniques key as a set."""
        return set(itertools.chain.from_iterable(self._create_ref_keys_list))

    def _get_techniques_json(self):
        """Load and store the techniques JSON file."""
        with open(db.LOCAL_TECH_JSON, "r") as file:
            self._techniques_json = json.load(file)
