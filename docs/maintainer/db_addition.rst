============================
Add database to ``pgdtools``
============================

Here we will first describe how a database is added and made available to ``pgdtools``.
No programming skills are required, however, you should be able to edit files on the GitHub repo.
While the database release itself is not hosted on GitHub,
adding a database requires us to update all the required metadata.
These metadata live in the
`GitHub repo database folder <https://github.com/NASA-Planetary-Science/pgdtools/tree/main/database>`_,
where a `README` file also explains the nomenclature of the files.
Please consult this file for more information.

----------------------
Prepare the references
----------------------

This section explains how to update the references.
We provide BibTeX, as well as plain text references.

++++++++++++++++++++++
BibTeX database update
++++++++++++++++++++++

All references that are given in the Excel file's `References` tab
have an entry in the presolar grain database public
`Zotero database <https://www.zotero.org/groups/4928655/presolar_grain_database>`_.
To prepare a new submission,
add the new references since the last submission to the Zotero database.
To do so,
you need `Zotero <https://www.zotero.org>`_
and the
`Better BibTeX for Zotero Plugin <https://retorque.re/zotero-better-bibtex/>`_.
Then create a new entry for each reference in the database.
The `PGD ID` value for each reference **must** be
the `Citation Key` in Zotero.

.. note::

    References without a `PGD ID` are also added to the bibliography.
    You can select a random citation key.
    Make sure that this citation key starts with letter earlier in the alphabeth than `S`.
    This will ensure that, in the next step, all references are properly sorted after parsing.

Using `Better BibTeX`, export the database into a BibTeX ``.bib`` file.
This file must then be saved in this repo as:

.. code-block::

    database/references.bib

++++++++++++++++++++++++
References ``json`` file
++++++++++++++++++++++++

In addition to the BibTeX file,
we also provide a ``json`` file with all references exactly as they are given in the Excel database file.
This file can be parsed by ``pgdtools`` to give the user the information on a reference.
You can create this automatically using the latest version of the Excel database and the maintainer tools.
The following shows an example of how to do this:

.. code-block:: python

    from pathlib import Path

    import pgdtools.maintainer as mt

    excel_file = Path("PGD_SiC_2023-07-22.xlsx")  # assuming the file is in the current directory
    mt.create_references_json(excel_file)


Note that we assume that the information is in a tab called "References".
If not, please specify the tab name using the ``tab_name`` argument.
This will create a ``json`` file in the current directory called ``references.json``.
You can now directly add this file to the GitHub repo
in the ``database`` folder.

---------------
Techniques file
---------------

To prepare the ``techniques.json`` file for upload to the GitHub repo,
a routine in ``pgdtools`` can be used.
You can create this automatically using the latest version of the Excel database and the maintainer tools.
The following shows an example of how to do this:

.. code-block:: python

    from pathlib import Path

    import pgdtools.maintainer as mt

    excel_file = Path("PGD_SiC_2023-07-22.xlsx")  # assuming the file is in the current directory
    mt.create_techniques_json(excel_file)

Note that we assume that the information is in a tab called "Techniques".
If not, please specify the tab name using the ``tab_name`` argument.
This will create a ``json`` file in the current directory called ``techniques.json``.
You can now directly add this file to the GitHub repo
in the ``database`` folder.

-----------------
Database ``json``
-----------------

The file ``db.json`` contains all the information about the databases.
This file is used by ``pgdtools`` to know which databases are available
and where to get them from.
A new release must be added to this file.
This can be done automatically with the maintainer tools.
You will need the excel file (as above) and the DOI of the release.

.. code-block:: python

    from pathlib import Path

    import pgdtools.maintainer as mt

    excel_file = Path("PGD_SiC_2023-07-22.xlsx")  # assuming the file is in the current directory
    db_json = Path("db.json")  # assuming the file is in the current directory

    doi = "10.5281/zenodo.1234567"  # replace with the DOI of the release
    mt.create_db_json(excel_file, doi, db_json=db_json)

If the current database is not yet in the ``db.json`` file,
it will be appended.
Otherwise a warning will be raised and the ``db.json`` file will not be modified.

If you run ``pgdtools`` from a cloned GitHub branch,
the ``db_json`` keyword can be omitted.
In this case, the ``db.json`` file in the repository will be updated.

The URL to the csv file and database name to add to the ``db.json`` file
are automatically extracted from the DOI and the Excel file.
It is assumed that the csv file has the same file name as the Excel file,
but with a different suffix.
If this is not the case, you can use the ``url`` and ``db_name`` keywords.
