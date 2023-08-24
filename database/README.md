# Database and information

This folder serves a database file with links to all Zenodo releases of the databases.
These json files are read in by the `pgdtools` whenever the database is updated.

## Database versions and change log

The links and descriptions are stored in the `db.json` file.
Each entry in the `db.json` file has the following structure:

```json
{
    "Sample Database": {
      "db_name": "Name of the database",
      "versions": [
        {
          "Change": "Description of what has changed in this version compared to the old ones",
          "Date": "Date of the database release in YYYY-MM-DD format",
          "DOI": "DOI of the database release",
          "Grains": "Number of grains in the database",
          "Known issues": "Known issues with this version of the database",
          "Released on": "Where this database has been released",
          "URL": "URL of the csv database",
        }
      ]
    }
}
```

The outer layer gives a database name (see below), e.g., `"sic"`.
The inner layer has first a `"db_name"`,
giving the database name in a human-readable format, e.g., `"Silicon Carbide"`.
The `"versions"` list contains all versions of the database,
where each version has multiple entries as described in the example `json` file above.

The following databases are currently available:

- Presolar SiC grains (`"sic"`)

## Techniques

The `techniques.json` file contains a list of all techniques that are currently in the presolar grain database.
Each entry has the following structure:

```json
{
  "technqiue_name": {
    "institution": "Institution where the technique was used",
    "techique": "Name of the technique",
    "instrument": "Name of the instrument",
    "reference": "Reference to the publication where the instrument was described"
  }
}
```

Note that the `"technique_name"` is simply the name of the technique as given in the Excel file.

## References

There are two files with references:

- `references.json` contains all references that are used in the database, identical to the Excel file.
- `references.bib` contains all references in BibTeX format.
