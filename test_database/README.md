# Database tests

This folder contains tests for the database.
Each new file is automatically tested against the last available version.
These tests check for the following occurances:

- Cell shifts

When a PR for a new database file is created,
these tests will automatically run.
They must pass in order for the new version
to be merged into the main branch.

**It is highly recommended
that database commits are separated from code commits.**
