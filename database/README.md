# Database

This folder serves a database file with links to all Zenodo releases of the databases.
The links are stored in the `db.json` file.
Each entry in the `db.json` file has the following structure:

```json
{
    "db_short_name": {
      "name": "Name of the database",
      "versions": ["link-to_version1.csv", "link-to_version2.csv", ...]
    }
}
```

The following databases are currently available:

- Presolar SiC grains (`"sic"`)

This json file is read in by the `pgdtools` whenever the database is updated.

## Zenodo links

The following links point to the Zenodo releases of the databases:

- [Silicon Carbide](https://zenodo.org/record/8187488)

## Changelog

In order to obtain the changelog of the databse,
please refer to `.xlsx` files on Zenodo.
