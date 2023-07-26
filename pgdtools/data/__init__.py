"""Initialize the data folder."""

from pathlib import Path

BIBFILE = Path(__file__).parent.joinpath("pgd_references.bib").absolute()
OLAFKEYFILE = (
    Path(__file__).parent.joinpath("pgd_library_id_doi_olafkey.csv").absolute()
)

__all__ = ["BIBFILE", "OLAFKEYFILE"]
