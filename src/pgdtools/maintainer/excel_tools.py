"""Maintainer tools to work with the Excel files.

These tools are mainly used in order to release a new version of the database to be
used with `pgdtools`.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Union
import warnings

import numpy as np
import pandas as pd


def append_to_db_json(
    excel_file: Path,
    doi: str,
    db_json: Path = None,
    url: str = None,
    zenodo_record: str = None,
    db_name=None,
    sheet_name: str = "VersionHistory",
) -> None:
    """Take the information from a given Excel database and adds it to ``db.json``.

    Information is read from the `VersionHistory` tab. From here the `Date`,
    `Grains`, `Change`, and `Known issues` are read.

    Currently, only releases on Zenodo are supported for SiC and Graphite grains.
    If the DOI does not contain the word `zenodo`, it refers likely to another archive
    (Astromat - IEDA) and the `zenodo_record` number is required.

    :param excel_file: Path to the Excel file.
    :param doi: DOI of the database.
    :param db_json: Path to the `db.json` file. If not given, the default location in
        the repository is used.
    :param url: URL of the database. If not given, the default release location URL
        is constructed by assuming that the filename is identical to Excel filename
        but with the extension `csv`.
    :param zenodo_record: Zenodo record number. This is required if the DOI is not
        a Zenodo DOI. Hover over the download link for the zenodo_record to get the
        record number.
    :param db_name: Name of the database. If not given, it is extracted from the
        filename.
    :param sheet_name: Name of the tab to use (default: VersionHistory).

    :raises NotImplementedError: (1) If the database is not a SiC or graphite database.
        (2) If the database is not released on Zenodo.
    :raises FileNotFoundError: If the `db.json` file is not found.
    """
    db_json = _get_database_file("db.json") if db_json is None else db_json

    if not db_json.is_file():
        raise FileNotFoundError(f"db.json not found at {db_json}.")

    db = json.load(open(db_json, "r"))

    # create database key
    if db_name is None:
        if "sic" in excel_file.name.lower():
            db_key = "sic"
        elif "gra" in excel_file.name.lower():
            db_key = "gra"
        else:
            raise NotImplementedError(
                "Only SiC,and graphite databases are currently supported."
            )

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
    elif zenodo_record is not None and "IEDA" in doi:  # Astromat/Zenodo cross release
        released_on = "Astromat"
        if url is None:
            url = (
                f"https://zenodo.org/record/{zenodo_record}/files/"
                f"{excel_file.with_suffix('.csv').name}"
            )
    else:
        raise NotImplementedError(
            "Only Zenodo releases and Astromat (IEDA) releases that are "
            "cross-released on Zenodo are currently supported."
        )

    # read the VersionHistory sheet for info where the correct date is displayed
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df = df.fillna("")
    grains = ""
    change = ""
    known_issues = ""
    for _, row in df.iterrows():
        if row["Date"] == date:
            grains = int(row["Grains"])
            change = row["Changes"]
            known_issues = row["Known issues"]
            break

    # todo: maybe ask the user what to do in this case?
    # warn user if no date was found
    if grains == "" and change == "" and known_issues == "":
        warnings.warn(
            f"No entry for {date.strftime('%Y-%m-%d')} found in VersionHistory tab. "
            f"Using empty strings.",
            stacklevel=2,
        )

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


def append_reference_json(
    excel_file: Path,
    sheet_name: str = "References",
    ref_json: Path = None,
    quiet: bool = False,
) -> None:
    """Create/append to `references.json` from the Excel file.

    References that are not assigned a `PGD ID` (and are thus empty) are ignored.

    :param excel_file: Path to the Excel file.
    :param sheet_name: Name of the tab to use (default: References).
    :param ref_json: Path to the `references.json` file. If not given, the default
        location in the repository is used.
    :param quiet: If True, just overwrite existing keys. If False, warn if a key
        already exists and ask user if it should be overwritten or not.
    """
    ref_json = _get_database_file("references.json") if ref_json is None else ref_json

    if not ref_json.is_file():  # create the file
        refs = {}
    else:
        refs = json.load(open(ref_json, "r"))

    # read in the Excel file
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # cols to replace NaN with empty string in
    nan_replace_cols = ["Reference - short", "Reference - full", "DOI", "Comments"]
    for col in nan_replace_cols:
        df[col] = df[col].fillna("")

    # create the dictionary
    new_refs = {}
    for _, row in df.iterrows():
        if (tmp_id := row["PGD ID"]) is not np.nan:
            new_refs[tmp_id] = {
                "Number of grains": int(row["Number of grains"]),
                "Reference - short": row["Reference - short"],
                "Reference - full": row["Reference - full"],
                "DOI": row["DOI"],
                "Comments": row["Comments"],
            }

    refs = _compare_and_append_dictionaries(refs, new_refs, quiet=quiet)

    # save out the json file
    with open(ref_json, "w") as fout:
        json.dump(refs, fout, indent=4)


def append_techniques_json(
    excel_file: Path,
    sheet_name: str = "Techniques",
    tech_json: Path = None,
    quiet: bool = False,
) -> None:
    """Create/append to `techniques.json` from the Excel file.

    :param excel_file: Path to the Excel file.
    :param sheet_name: Name of the tab to use (default: Techniques).
    :param tech_json: Path to the `techniques.json` file. If not given, the default
        location in the repository is used.
    :param quiet: If True, just overwrite existing keys. If False, warn if a key
        already exists and ask user if it should be overwritten or not.
    """
    tech_json = (
        _get_database_file("techniques.json") if tech_json is None else tech_json
    )

    if not tech_json.is_file():  # create the file
        techniques = {}
    else:
        techniques = json.load(open(tech_json, "r"))
    # read in the Excel file
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    df = df.fillna("")

    # create the dictionary
    techniques_new = {}
    for _, row in df.iterrows():
        if (tmp_id := row["PGD Technique"]) is not np.nan:
            techniques_new[tmp_id] = {
                "Institution": row["Institution"],
                "Technique": row["Technique"],
                "Instrument": row["Instrument"],
                "Reference": row["Reference"],
                "DOI": row["DOI"],
            }

    techniques = _compare_and_append_dictionaries(
        techniques, techniques_new, quiet=quiet
    )

    # save out the json file
    with open(tech_json, "w") as fout:
        json.dump(techniques, fout, indent=4)


def _compare_and_append_dictionaries(
    dict_ex: dict, dict_new: dict, quiet: bool = True
) -> dict:
    """Compare two dictionaries and append the new one to the existing one.

    Overwriting of keys is done automatically if `quiet=True`. If not, then the user
    is asked if keys shall be overwritten.

    :param dict_ex: Existing dictionary.
    :param dict_new: New dictionary.
    :param quiet: If True, just overwrite existing keys. If False, warn if a key
        already exists and ask user if it should be overwritten or not.
    """
    keys_exist = []
    for key in dict_new:
        if key in dict_ex:
            keys_exist.append(key)

    if keys_exist:
        if quiet:
            warnings.warn(
                f"Keys {keys_exist} already exists in references.json. Overwriting."
            )
            for key in dict_new:
                dict_ex[key] = dict_new[key]
        else:
            print("The following keys already exist in the references.json file:")
            print(keys_exist)
            print("Do you want to overwrite them? (y/n)")
            answer = input()
            if answer.lower() == "y":
                for key in dict_new:
                    dict_ex[key] = dict_new[key]
            else:
                print("Not overwriting keys.")
                for key in dict_new:
                    if key not in keys_exist:
                        dict_ex[key] = dict_new[key]
    else:
        dict_ex.update(dict_new)

    return dict_ex


def _get_database_file(fname: Union[Path, str]) -> Path:
    """Get the path for a file in the database folder."""
    return Path(__file__).parents[3].joinpath(f"database/{fname}")
