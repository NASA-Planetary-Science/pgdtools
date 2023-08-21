"""Maintainer tools to work with the Excel files.

These tools are mainly used in order to release a new version of the database to be
used with `pgdtools`.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd


def create_techniques_json(excel_file: Path, tab_name: str = "Techniques") -> None:
    """Create `techniques.json` from the Excel file.

    :param excel_file: Path to the Excel file.
    :param tab_name: Name of the tab to use (default: Techniques).
    """
    # read in the Excel file
    df = pd.read_excel(excel_file, sheet_name=tab_name)

    df = df.fillna("")

    # create the dictionary
    techniques = {}
    for _, row in df.iterrows():
        if (tmp_id := row["PGD Technique"]) is not np.nan:
            techniques[tmp_id] = {
                "Institution": row["Institution"],
                "Technique": row["Technique"],
                "Instrument": row["Instrument"],
                "Reference": row["Reference"],
            }

    # save out the json file
    with open("techniques.json", "w") as fout:
        json.dump(techniques, fout, indent=4)


def create_references_json(excel_file: Path, tab_name: str = "References") -> None:
    """Create `references.json` from the Excel file.

    References that are not assigned a `PGD ID` (and are thus empty) are ignored.

    :param excel_file: Path to the Excel file.
    :param tab_name: Name of the tab to use (default: References).
    """
    # read in the Excel file
    df = pd.read_excel(excel_file, sheet_name=tab_name)

    # cols to replace NaN with empty string in
    nan_replace_cols = ["Reference - short", "Reference - full", "DOI", "Comments"]
    for col in nan_replace_cols:
        df[col] = df[col].fillna("")

    # create the dictionary
    references = {}
    for _, row in df.iterrows():
        if (tmp_id := row["PGD ID"]) is not np.nan:
            references[tmp_id] = {
                "Number of grains": int(row["Number of grains"]),
                "Reference - short": row["Reference - short"],
                "Reference - full": row["Reference - full"],
                "DOI": row["DOI"],
                "Comments": row["Comments"],
            }

    # save out the json file
    with open("references.json", "w") as fout:
        json.dump(references, fout, indent=4)


if __name__ == "__main__":
    create_references_json(
        Path(__file__).parent.parent.parent.joinpath("tmp/PGD_SiC_2023-07-22.xlsx")
    )
