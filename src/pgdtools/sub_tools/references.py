"""Sub tool to gather references for data sets and return them."""

import json
from typing import List, Set

import pandas as pd

import pgdtools
from pgdtools import db


class References:
    """This class handles references for specific data sets."""

    def __init__(self, parent: "pgdtools.PresolarGrains") -> None:
        """Initialize the Reference class.

        :param parent: Parent class, must be of type ``PresolarGrains``.

        :raises TypeError: Parent class is not of type ``PresolarGrains``.
        """
        if not isinstance(parent, pgdtools.PresolarGrains):
            raise TypeError("Parent class must be of type PresolarGrains.")

        self.parent = parent

        self._reference_json = None
        self._get_reference_json()

    def __repr__(self) -> str:
        """Return a string representation of the class.

        In order to keep it pretty, this will return the following:
        - Reference key
        - Short reference
        - DOI (if available) in parentheses

        :return: String representation of the class.
        """
        ret_val = ""
        for it, (key, value) in enumerate(self.dict.items()):
            ret_val += f"{key}: {value['Reference - short']}"
            if value["DOI"]:
                ret_val += f" ({value['DOI']})"
            if it != len(self.dict) - 1:
                ret_val += "\n"

        return ret_val

    def __eq__(self, other) -> bool:
        """Check if the references are equal.

        Note: This will only check if the set of references are equal and has nothing
        to do with the number of grains that are associated with each reference.
        """
        return self.dict == other.dict

    def __len__(self) -> int:
        """Return the number of individual references in the class."""
        return len(self.dict)

    def __iter__(self) -> iter:
        """Iterate over the key, value pairs."""
        return iter(self.dict.items())

    def __getitem__(self, item) -> dict:
        """Return the reference for the given item."""
        return self.dict[item]

    @property
    def dict(self) -> dict:
        """Return a dictionary representation of the class.

        The keys are the reference IDs and the values are the full references, which
        contain further keys:
        - Number of grains
        - Reference - short
        - Reference - full
        - DOI
        - Comments

        :return: Dictionary representation of the class.
        """
        return {key: self._reference_json[key] for key in self._create_ref_keys_set}

    @property
    def doi(self) -> Set[str]:
        """Return a set of all DOIs for the references of the current database.

        If no DOI is available for a given reference, it will not be included in the
        set.
        """
        return {self.dict[key]["DOI"] for key in self.dict if self.dict[key]["DOI"]}

    @property
    def table_full(self) -> pd.DataFrame:
        """Return a full reference table for every individual grain in the database.

        The row indexes of the table are the PGD IDs. The following columns will be
        present:
        - Number of grains
        - Reference - short
        - Reference - full
        - DOI
        - Comments

        :return: Full reference table for every grain.
        """
        indexes = self.parent.db.index
        series = [
            pd.Series(self._reference_json[ref_id], name=indexes[it])
            for it, ref_id in enumerate(self._create_ref_keys_list)
        ]
        return pd.DataFrame(series)

    @property
    def table_set(self) -> pd.DataFrame:
        """Return a set of references for all grains in dataset in table format."""
        table_set = self.table_full.drop_duplicates()
        return table_set.set_index([self._create_ref_keys(table_set.index)])

    @property
    def _create_ref_keys_list(self) -> List[str]:
        """Create the reference key as a list (in order).

        :return: List of all the reference IDs.
        """
        return self._create_ref_keys(self.parent.db.index)

    @property
    def _create_ref_keys_set(self) -> Set[str]:
        """Create the reference key as a set."""
        return set(self._create_ref_keys_list)

    def _get_reference_json(self):
        """Return the reference JSON file."""
        with open(db.LOCAL_REF_JSON, "r") as file:
            self._reference_json = json.load(file)

    @staticmethod
    def _create_ref_keys(pgd_ids: List[str]) -> List[str]:
        """Create reference keys from a PGD IDs.

        :param pgd_ids: List of PGD IDs to create reference keys from.
        """
        ref_keys = []
        for pgd_id in pgd_ids:
            name_parts = pgd_id.split("-")
            name_parts[-1] = name_parts[-1][0]
            ref_keys.append("-".join(name_parts))
        return ref_keys