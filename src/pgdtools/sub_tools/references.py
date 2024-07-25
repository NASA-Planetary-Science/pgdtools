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

        :param other: Other reference set to compare against.

        :return: True if the references are equal, otherwise False.
        """
        return self.dict == other.dict

    def __len__(self) -> int:
        """Return the number of individual references in the class.

        :return: Number of references.
        """
        return len(self.dict)

    def __iter__(self) -> iter:
        """Iterate over the key, value pairs.

        :return: Iterator for the reference keys and values.
        """
        return iter(self.dict.items())

    def __getitem__(self, key) -> dict:
        """Return the reference for the given item.

        :param key: Reference key.

        :return: Reference details.
        """
        return self.dict[key]

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

    def search(self, search_str: str) -> List[str]:
        """Search all references information (except for notes) for keywords.

        If you want to provide multiple keywords to search for, please provide
        them separated by a comma. For example: `"Name Firstname"` would search
        all references for "Name Firstname", while `"Name, Firstname"` would search
        for "Name" and "Firstname" separately. For example, a reference with information
        "Firstname Name" would in this case only match with the latter search.

        All searches are case-insensitive.

        :param search_str: Search string.

        :return: List of strings with all short references that match the search terms.
        """
        search_terms = search_str.split(",")
        search_terms = [x.strip().lower() for x in search_terms]

        fields_to_add = ["Reference - short", "Reference - full", "DOI"]

        ref_search_dict = {}
        for ref_key, ref_item in self.dict.items():
            key = ref_item["Reference - short"]
            value = ref_key  # the PGD ID for this reference
            for add_key in fields_to_add:
                value += f" {ref_item[add_key]}"
            ref_search_dict[key] = value.lower()  # make it case-insensitive

        ret_list = []
        for key, item in ref_search_dict.items():
            if all([x in item for x in search_terms]):
                ret_list.append(key)

        ret_list.sort()

        if len(ret_list) == 0:
            print("No references found.")
        else:
            print("References found:")
            for entry in ret_list:
                print(f"- {entry}")
        return ret_list

    def _get_reference_json(self):
        """Load and store the reference JSON file."""
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
