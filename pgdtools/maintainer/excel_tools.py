"""Maintainer tools to work with the Excel files.

These tools are mainly used in order to release a new version of the database to be
used with `pgdtools`.
"""

from datetime import datetime
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd


def append_to_db_json(
    excel_file: Path, doi: str, db_json: Path = None, url: str = None, db_name=None
) -> None:
    """Take the information from a given Excel database and adds it to ``db.json``.

    Information is read from the `VersionHistory` tab. From here the `Date`,
    `Grains`, `Change`, and `Known issues` are read.

    Currently, only releases on Zenodo are supported for SiC grains are supported.

    :param excel_file: Path to the Excel file.
    :param doi: DOI of the database.
    :param db_json: Path to the `db.json` file. If not given, the default location in
        the repository is used.
    :param url: URL of the database. If not given, the default release location URL
        is constructed by assuming that the filename is identical to Excel filename
        but with the extension `csv`.
    :param db_name: Name of the database. If not given, it is extracted from the
        filename.

    :raises NotImplementedError: (1) If the database is not a SiC database.
        (2) If the database is not released on Zenodo.
    :raises FileNotFoundError: If the `db.json` file is not found.
    """
    # read the standard db.json file
    if db_json is None:
        db_json = Path(__file__).parent.parent.parent.joinpath("database/db.json")

    if not db_json.is_file():
        raise FileNotFoundError(f"db.json not found at {db_json}.")

    db = json.load(open(db_json, "r"))

    # create database key
    if db_name is None:
        if "sic" in excel_file.name.lower():
            db_key = "sic"
        else:
            raise NotImplementedError("Only SiC databases are currently supported.")

    # get the date from filename (between last "_" and suffix) and convert to datetime
    date = excel_file.name.split("_")[-1].split(".")[0]
    date = datetime.strptime(date, "%Y-%m-%d")

    # create released_on and url
    if "zenodo" in doi.lower():
        released_on = "Zenodo"
        if url is None:
            url = (
                f"https://zenodo.org/record/{doi.split('.')[-1]}/files/"
                f"{excel_file.with_suffix('.csv').name}"
            )
    else:
        raise NotImplementedError("Only Zenodo releases are currently supported.")

    # read the VersionHistory sheet for info where the correct date is displayed
    df = pd.read_excel(excel_file, sheet_name="VersionHistory")
    df = df.fillna("")
    grains = ""
    change = ""
    known_issues = ""
    for _, row in df.iterrows():
        if row["Date"] == date:
            grains = int(row["Grains"])
            change = row["Change"]
            known_issues = row["Known issues"]
            break

    # warn user if no date was found
    if grains == "" and change == "" and known_issues == "":
        warnings.warn(
            f"No entry for {date.strftime('%Y-%m-%d')} found in VersionHistory tab. "
            f"Using empty strings.",
            stacklevel=2,
        )

    # check if the entry already exists, if so, give warning and exit
    for entry in db[db_key]["versions"]:
        if doi in entry["DOI"]:
            warnings.warn(f"DOI {doi} already exists in db.json.", stacklevel=2)
            return

    # now add the entry to the db
    db[db_key]["versions"].append(
        {
            "Change": change,
            "Date": date.strftime("%Y-%m-%d"),
            "DOI": doi,
            "Grains": grains,
            "Known issues": known_issues,
            "Released on": released_on,
            "URL": url,
        }
    )

    # save out the json file
    with open(db_json, "w") as fout:
        json.dump(db, fout, indent=4)


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
                "DOI": row["DOI"],
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
    append_to_db_json(
        Path(__file__).parent.parent.parent.joinpath("tmp/PGD_SiC_2023-07-22.xlsx"),
        doi="10.5281/zenodo.8187488",
    )
