=============
PDS Archiving
=============

This part of the documentation describes how to semi-automatically
deploy an archive for NASA's `Planetary Data System (PDS) <https://pds.nasa.gov/>`_.
This process is not fully automated and requires user input.
The documentation is aimed at the database maintainer and requires the appropriate access
in order to be successfully completed.
Please follow the steps below in order to prepare a submission to PDS.

.. note::
    The database is not directly prepared in the PDS format,
    but is submitted to PDS via `OLAF <https://sbnapps.psi.edu/olaf-node>`_.
    The steps here provide you with information on how to upload the
    presolar grain database into OLAF.
    The PDS contact will then help further with the move from OLAF to PDS.

The following flowchart shows the process how the database gets imported into OLAF.

.. mermaid::
    :align: center

    graph TD
        A(Update Zotero bibliography) --> |Copy bibliography to repo| B{Parse the bib file}
        B --> |Open generated output| C(Import new references into OLAF)
        C --> D(Save OLAF Keys into keyfile)
        D --> E{Export Database\n ready for OLAF\n import}
        E --> F(Import Database into OLAF\n and contact PDS contact)

---------------------------------------
Update the reference database on Zotero
---------------------------------------

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
This file must then be saved in source code in as:

.. code-block::

    pgdtools/data/pgd_references.bib

----------------------
Parse the bibliography
----------------------

Now use the ``pgdtools`` to parse the library.
This is done in the following way:

.. code-block:: python

    from pgdtools import pds
    pds.bibparser.process_bib_file()

This will create two files in your current working directory:

  - ``key_doi_file.csv``: A file that contains the new keys and DOIs
  - ``pgd_library_olaf.txt``: A text file with information for subsequent manual copying of references into OLAF

........................
Update the OLAF key file
........................

Grains that were added since the last database update should have citation entries
at the bottom of the file ``key_doi_file.csv``.
Compare this file to the file named ``pgd_library_id_doi_olafkey.csv``,
which is in the folder ``pgdtools/data``.
You now need to copy all lines with new PGD IDs from the ``key_doi_file.csv``
into the ``pgd_library_id_doi_olafkey.csv`` file.
Note that these new lines end with a comma and have no OLAF-key yet incorporated.
Leave this file open.

...........................
Import references into OLAF
...........................

Now, the new references need to manually added to OLAF.
The file ``pgd_library_olaf.txt`` will help with this task.
Open the file,
go to OLAF, References, and click on `Create`.
For all new references,
i.e., references that have no OLAF key in ``pgd_library_id_doi_olafkey.csv`` (see above),
you need to copy the references to OLAF and submit them.
The file ``pgd_library_olaf.txt`` has a all lines and information to simply copy/paste into OLAF.
Once a reference is submitted,
copy the key that you receive and add it to the file ``pgd_library_id_doi_olafkey.csv``
after the comma of the respective line.
You have now added a new OLAF key.

----------------------------
Export the complete database
----------------------------

To export the complete, new database as individual, embedded ``csv`` files for subsequent OLAF import,
make sure that your local installation of ``pgdtools.PresolarGrains()`` reads the new database.
Using ``pgdtools``,
you can then create the ``csv`` files automatically as following:

.. code-block:: python

    from pgdtools import pds
    pds.olaf.olaf_export()

This will create a folder in your current working directory
named ``export_olaf_TIMESTAMP``,
where ``TIMESTAMP`` is a ISO formatted time stamp of right now.

This folder will contain a csv file for each presolar grain in the database.
These csv files have metadata embedded.

--------------
Upload to OLAF
--------------

.. warning::

    This part still needs to be written...
