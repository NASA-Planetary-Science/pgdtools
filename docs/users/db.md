# Database Management

The database management is independent of the `pgdtools` package,
since updates to the database do not require package changes.
In order for the package however to being able to update to the latest database,
we include a database manager.

Note that all databases,
i.e., for all different grain types ("sic", ...)
can be managed with this tool.

## Currently impelmented databases

The following grain types are currently implemented:

- Silicon carbide
- Graphite

## Background

In order to be able to update the database without updating the package,
we provide configuration files that contain links to
all releases of the database (including the latest ones).
These configuration files live in the
[GitHub repo database folder](https://github.com/NASA-Planetary-Science/pgdtools/tree/main/database)
and are updated with each new release of the database.
Updating the database therefore always requires to first upgrading the configuration files.

Configuration files, as well as the database itself,
are stored locally.
The location of the data is

- `~/.config/pgdtools/` for Linux and Mac OS
- `%APPDATA%/Roaming/pgdtools/` for Windows

The database is stored in a subfolder called `csv`,
while the configuration files are stored in a subfolder called `config`.

Finally, a `current.json` file is stored in the data folder.
This file contains the name of the currently used database.

## Configuration

!!! note

    Todo:
    Some text on the configuration managers.
    This will need to be written later when all managers are available.

## Updating

The database manager can be used to update the database.
Simply updating to the latest version of the database can be done using the following command:

```python
from pgdtools import db
db.update()
```

This will update the configuration files and the database to the latest version,
and set the currently used database to the latest version as well.

The update function has a few more options:

- `get_all`: If set to `True`, all databases will be downloaded.
  If set to `False`, only the latest databases for all grain types will be downloaded.
  Default: ``False``.
- `clean`: If set to `True`, the database folder will be deleted before downloading the database.
  Default: `False`.
- `get_config`: If set to `True`, the configuration files will be downloaded anew.
  Default: `True`.

## Current database

To display the currently used database, use the following command:

```python
from pgdtools import db
db.current()
```

For each grain type, the currently used database is shown as a dictionary.

## Setting current

To set the current database, e.g., for "sic",
you need to have a `keyword`, `value` pair
that characterizes the database.
These keywords are the ones that show up in a given database under `"versions"`.
It is best to use a `keyword` that will have a unique `value`.
These keywords are:

- "Date"
- "DOI"
- "URL"

Practically, the "Date" and "DOI" keywords are the most useful ones.

!!! note

    You can use other keywords as well, e.g,. "Grains".
    However, if multiple versions contain the same value,
    the first one found will be used.

To set the current database use the following command:

```python
from pgdtools import db
doi = "10.5281/zenodo.8187446"
db.set_current("sic", "DOI", doi)
```

If a database is available in the configuration file
but has not yet been downloaded,
the package will try to download and save it.
