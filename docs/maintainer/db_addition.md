# Add database to ``pgdtools``

Here we will first describe how a database is added and made available to `pgdtools`.
No programming skills are required, however, you should be able to edit files on the GitHub repo.
While the database release itself is not hosted on GitHub,
adding a database requires us to update all the required metadata.
These metadata live in the
[GitHub repo database folder](https://github.com/NASA-Planetary-Science/pgdtools/tree/main/database),
where a `README` file also explains the nomenclature of the files.
Please consult this file for more information.

## Prepare the references

This section explains how to update the references.
We provide BibTeX, as well as plain text references.

### BibTeX database update

All references that are given in the Excel file's `References` tab
have an entry in the presolar grain database public
[Zotero database](https://www.zotero.org/groups/4928655/presolar_grain_database).
To prepare a new submission,
add the new references since the last submission to the Zotero database.
To do so,
you need [Zotero](https://www.zotero.org)
and the
[Better BibTeX for Zotero Plugin](https://retorque.re/zotero-better-bibtex).
Then create a new entry for each reference in the database.
The `PGD ID` value for each reference **must** be
the `Citation Key` in Zotero.

!!! note

    References without a `PGD ID` are also added to the bibliography.
    You can select a random citation key.
    Make sure that this citation key starts with letter earlier in the alphabeth than `S`.
    This will ensure that, in the next step, all references are properly sorted after parsing.

Using `Better BibTeX`, export the database into a BibTeX `.bib` file.
This file must then be saved in this repo as:

```
database/pgd_references.bib
```

### References `json` file

In addition to the BibTeX file,
we also provide a `json` file with all references exactly as they are given in the Excel database file.
This file can be parsed by `pgdtools` to give the user the information on a reference.
You can create this automatically using the latest version of the Excel database and the maintainer tools.
The following shows an example of how to do this:

```python
from pathlib import Path

import pgdtools.maintainer as mt

excel_file = Path("PGD_SiC_2023-07-22.xlsx", quiet=True)  # assuming the file is in the current directory
mt.append_reference_json(excel_file)
```


Note that we assume that the information is in a tab called "References".
If not, please specify the tab name using the `tab_name` argument.
This will add the references to the `references.json` file in the `database` directory of the repository.
Keys that already exist will be overwritten with the new information.
If you do not want to overwrite existing keys,
select `quiet=False` (which is also the default value).
Then you will be asked if you want to overwrite existing keys.
If you select `n` (no), no keys will be overwritten.

## Techniques file

To prepare the `techniques.json` file for upload to the GitHub repo,
a routine in `pgdtools` can be used.
You can create/update the technique file automatically
using the latest version of the Excel database and the maintainer tools.
The following shows an example of how to do this:

```python
from pathlib import Path

import pgdtools.maintainer as mt

excel_file = Path("PGD_SiC_2023-07-22.xlsx")
mt.append_techniques_json(excel_file, quiet=True)
```

Note that we assume that the information is in a tab called "Techniques".
If not, please specify the tab name using the `tab_name` argument.
This will create/update the `techniques.json` file in the database directory of the repository.
If you do not want to overwrite existing keys,
select `quiet=False` (which is also the default value).
Then you will be asked if you want to overwrite existing keys.
If you select `n` (no), no keys will be overwritten.

## Database `json`

The file `db.json` contains all the information about the databases.
This file is used by `pgdtools` to know which databases are available
and where to get them from.
A new release must be added to this file.
This can be done automatically with the maintainer tools.
You will need the excel file (as above) and the DOI of the release.

```python
from pathlib import Path

import pgdtools.maintainer as mt

excel_file = Path("PGD_SiC_2023-07-22.xlsx")
db_json = Path("db.json")

doi = "10.5281/zenodo.1234567"  # replace with the DOI of the release
mt.append_to_db_json(excel_file, doi, db_json=db_json)
```

If the current database is not yet in the `db.json` file,
it will be appended.
Otherwise, a warning will be raised and the `db.json` file will not be modified.

If you run `pgdtools` from a cloned GitHub branch,
the `db_json` keyword can be omitted.
In this case, the `db.json` file in the repository will be updated.

The URL to the csv file and database name to add to the `db.json` file
are automatically extracted from the DOI and the Excel file.
It is assumed that the csv file has the same file name as the Excel file,
but with a different suffix.
If this is not the case, you can use the `url` and `db_name` keywords.

!!! info "Database on Astromat but cross-listed on Zenodo"

    If the doi of the database does not contain the word `zenodo`,
    it was not minted by Zenodo and was most likely created by Astromat (IEDA).
    If the database is cross-referenced on Zenodo,
    hover over the Zenodo download link and extract the record ID manually.
    This record ID is the number after `record/` and before `files` in the URL.
    Provide this record ID to `append_to_db_json` using the `zenodo_record` keyword.
