"""Initialize the data folder."""

from pathlib import Path

DB_FILE_URL = "https://raw.githubusercontent.com/NASA-Planetary-Science/pgdtools/main/database/db.json"  # noqa: B950

BIBFILE = Path(__file__).parent.joinpath("pgd_references.bib").absolute()
OLAFKEYFILE = (
    Path(__file__).parent.joinpath("pgd_library_id_doi_olafkey.csv").absolute()
)

__all__ = ["BIBFILE", "OLAFKEYFILE"]
