"""Take the whole PGD and create an OLAF dataset.

This script uses `pgdtools` in order to create an OLAF compatible dataset.
This dataset can then be easily imported from OLAF into PDS. The first few variables
can be ajdusted in order to set up the export conditions (how much, etc.).

Global variables that define output behavior:
    - EXPORT_PATH: Path where to export the whole database to.
    - LIMIT_TO_GRAINS: List of grain IDs to limit the export to. If empty, all grains
        are exported.
    - OLAFREFKEY: Name of the csv file that contains all grain IDs and OLAF
        bibliography keys.

Example:
    todo
"""

from datetime import datetime
from pathlib import Path
from typing import List

from pgdtools.data import OLAFKEYFILE
from pgdtools.pds import bibparser
from pgdtools.pgdtools import PresolarGrains

# GLOBAL VARIABLES THAT DEFINE OUTPUT BEHAVIOR

EXPORT_PATH = Path(
    f"export_olaf_{datetime.now()}".replace(" ", "_")
    .replace(":", "-")
    .replace(".", "-")
)
LIMIT_TO_GRAINS = None

# some testing settings - uncomment if wanted
# EXPORT_PATH = Path("tmp/export_olaf")
# LIMIT_TO_GRAINS = ["SiC-2021-NIT-000024"]

# dictionary that defines the columns of the output file for PDS
# list entries are [type, unit, description]
COLUMNS_DESC = {
    "PGD Type": ["string", "", "Presolar grain database type"],
    "PGD Subtype": ["string", "", "Presolar grain database subtype"],
    "Type": ["string", "", "Author associated presolar grain type"],
    "p(M)": ["float", "", "Probability of the grain being of type M"],
    "p(X)": ["float", "", "Probability of the grain being of type X"],
    "p(Y)": ["float", "", "Probability of the grain being of type Y"],
    "p(Z)": ["float", "", "Probability of the grain being of type Z"],
    "p(AB)": ["float", "", "Probability of the grain being of type AB"],
    "p(C)": ["float", "", "Probability of the grain being of type C"],
    "p(D)": ["float", "", "Probability of the grain being of type D"],
    "p(N)": ["float", "", "Probability of the grain being of type N"],
    "Grain Label": ["string", "", "Author assigned grain label"],
    "Data Published": ["string", "", "How and in which form data were published"],
    "Size a": ["float", "micrometer", "Grain size along longest dimension"],
    "Size b": [
        "float",
        "micrometer",
        "Grain size along axis perpendicular to longest dimension",
    ],
    "Notes": [
        "string",
        "",
        "Additional information about the specific grain measurement",
    ],
}


def _authordict_creator() -> dict:
    """Create a dictionary of the bibliography to return the authors.

    :return: Dictionary with the bibliography. Keys are the grain IDs, values is a list
        of authors.
    """
    bibdb = bibparser.get_bibfile()

    # create the dictionary
    authordict = {}
    for entry in bibdb.entries:
        authordict[entry["ID"]] = bibparser.format_authors(entry["author"])

    return authordict


_AUTHOR_DICT = _authordict_creator()


def bibkey_olaf(grain: PresolarGrains.Grain) -> str:
    """Get the OLAF bibliography key from a grain ID string."""
    ref_id = _get_ref_id(grain.id)
    with open(OLAFKEYFILE, "r") as fin:
        for line in fin:
            if ref_id in line:
                return line.split(",")[-1].strip()
    return ""  # entry not found - unpublished data


def column_desc(col_name: str) -> List[str]:
    """Return PDS entries of for data description based on column name.

    Check if the column name is in the COLUMNS_DESC dictionary. If yes, return the
    corresponding description.
    For all columns that are not in the COLUMNS_DESC dictionary, return a description
    that is generated based on the column name.

    :param col_name: Name of the column.

    :return: List of column type, unit, and description.

    :raises KeyError: If the column name is not in the COLUMNS_DESC dictionary.
    """
    # sanitize input
    if "size" in col_name.lower():  # we have a size, throw away the unit
        col_name = " ".join(col_name.split()[0:2])

    if col_name in COLUMNS_DESC:
        return COLUMNS_DESC[col_name]
    else:
        if "[" in col_name:  # we have an uncertainty
            ratio_name = col_name.split("[")[1][:-1].replace("d(", "delta(")
        else:
            ratio_name = col_name.replace("d(", "delta(")
        unit = "permil" if "delta" in ratio_name else ""
        if col_name.startswith("rho"):
            return ["float", "", f"Correlation coefficient for {ratio_name}"]
        elif col_name.startswith("err+["):
            return ["float", unit, f"Absolute positive uncertainty of {ratio_name}"]
        elif col_name.startswith("err-["):
            return ["float", unit, f"Absolute negative uncertainty of {ratio_name}"]
        elif col_name.startswith("err["):
            return ["float", unit, f"Absolute uncertainty of {ratio_name}"]
        elif col_name.startswith("d("):
            return [
                "float",
                unit,
                f"Delta value of isotope ratio {ratio_name.split('(')[1][:-1]}.",
            ]
        elif col_name == ratio_name:
            return [
                "float",
                unit,
                f"Isotope ratio {col_name}",
            ]
        else:
            raise KeyError(f"Column name {col_name} not found in parser.")


def get_authors(grain: PresolarGrains.Grain) -> str:
    """Get the authors from a grain ID string.

    :param grain: Grain instance.

    :return: String of authors in OLAF format.
    """
    # check for unpublished grains
    if "unpublished" in grain.reference.lower():
        return grain.reference.split()[0]  # Just return last name of unpub. ref.

    # read authors from bibliography for published studies
    ref_id = _get_ref_id(grain.id)
    authors = _AUTHOR_DICT[ref_id]

    # format the authors
    authors_ret = '"'
    for auth in authors:
        authors_ret += f"{auth[0]}, {auth[1]}"
        if auth != authors[-1]:  # all except last entry
            authors_ret += "; "
        else:
            authors_ret += '"'

    return authors_ret


def olaf_export():
    """Create the database to import into OLAF as csv with embedded metadata."""
    # create th export path, if it does not exist
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)

    # create the PGD object
    pgd = PresolarGrains()

    # get the IDs of the grains to export
    if LIMIT_TO_GRAINS:
        grain_ids = LIMIT_TO_GRAINS
    else:
        grain_ids = list(pgd.db.index)

    done_counter = 1
    # export the grains
    for id in grain_ids:
        grain = pgd.grain[id]

        # prepare the data
        data = grain.entry.dropna()

        # drop columns `Reference`, `Source`, and `Technique` from the data
        data = data.drop(["Reference", "Source", "Technique"])

        # determine the number of commas we need
        n_comma = len(data) - 1

        # write the output file
        with open(EXPORT_PATH.joinpath(id).with_suffix(".csv"), "w") as fout:
            fout.writelines(f"# Keywords{',' * n_comma}\n")
            fout.writelines(f"Product Name,{id}{',' * (n_comma -1)}\n")
            fout.writelines(f"Start Time,N/A{',' * (n_comma -1)}\n")
            fout.writelines(f"Stop Time,N/A{',' * (n_comma -1)}\n")
            fout.writelines(f"Target Name,{grain.source}{',' * (n_comma -1)}\n")
            fout.writelines(f"Target Type,Sample{',' * (n_comma -1)}\n")
            fout.writelines(f"Author List,{get_authors(grain)}{',' * (n_comma - 1)}\n")
            fout.writelines(
                f"Product Processing Level,Calibrated{',' * (n_comma -1)}\n"
            )
            fout.writelines(
                f'Science Search Facet,"Dust Study, Meteoritics"{"," * (n_comma -1)}\n'
            )
            fout.writelines(f"Product Wavelength Ranges{',' * n_comma}\n")
            fout.writelines(f"Reference Key,{bibkey_olaf(grain)}{',' * (n_comma -1)}\n")
            fout.writelines(f"Observing System Bookmark,???{',' * (n_comma -1)}\n")

            fout.writelines(f"# Column Definitions{',' * n_comma}\n")

            # temporary strings for the data columns
            col_names = ""
            col_types = ""
            col_units = ""
            col_desc = ""
            col_data = ""
            for it, dat in enumerate(data):
                if it != len(data) - 1:  # not the last
                    sep = ","
                else:
                    sep = "\n"
                col_name = data.index[it]
                col_names += f"{col_name}{sep}"

                tp, unit, desc = column_desc(col_name)
                col_types += f"{tp}{sep}"
                col_units += f"{unit}{sep}"
                col_desc += f"{desc}{sep}"
                col_data += f"{dat}{sep}"

            fout.writelines(col_names)
            fout.writelines(col_types)
            fout.writelines(col_units)
            fout.writelines(col_desc)
            fout.writelines(col_data)

        # print progress
        print(f"Done with {done_counter} of {len(grain_ids)} grains.")
        done_counter += 1


def _get_ref_id(grain_id: str) -> str:
    """Get the reference ID from a grain ID string.

    :param grain_id: Grain ID string.

    :return: Reference ID string.

    Example:
        >>> _get_ref_id("SiC-1992-VIR-000026")
        'SiC-1992-VIR-0'
    """
    id_split = grain_id.split("-")
    id_split[-1] = id_split[-1][0]
    ref_id = "-".join(id_split)
    return ref_id


if __name__ == "__main__":
    olaf_export()
