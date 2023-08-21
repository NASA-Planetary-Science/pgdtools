========
Overview
========

As a database maintainer,
you should have the ``pgdtools`` installed with extra requirements.
To do so, please run

.. code-block:: bash

    pip install pgdtools[maintainer]

Creating a new release of the database requires the following step:

- A new release archive has been created, e.g., on Zenodo.
- The reference BibTeX and ``json`` file used in ``pgdtools`` must be updated.
- The file ``db.json``, which contains the information on all database versions must be updated.
- The file ``techniques.json``, which contains an overview of all measurement techniques, must be updated.

New releases of the database / new archives can be created either after a release on Zenodo
or after a archiving event, e.g., archiving of the whole database in Astromat.
While Zenodo releases are created manually,
Astromat submissions of the presolar database can be prepared by ``pgdtools`` from a given local database.

.. note::
    In this whole paragraph, we will talk about a new database.
    You want to have the new database available locally.
    You want to have the ``xlsx`` Excel as well as the ``csv`` file available.
    Depending on the routine, one or the other file is required.
