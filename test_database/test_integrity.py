"""These routines test the database integrity."""

import pandas as pd


def test_is_subset(gh_dbs, curr_dbs):
    """Ensure that the old database is a subset of the new one."""
    for key in curr_dbs:
        curr_db = curr_dbs[key]
        gh_db = gh_dbs[key]

        # new dataset has less entries than the old one
        if curr_db.shape[0] < gh_db.shape[0]:
            raise AssertionError("New database contains less entries than old one.")

        # Different numbers of columns
        elif curr_db.shape[1] != gh_db.shape[1]:
            raise AssertionError("The databases have different numbers of columns.")

        # same rows and columns
        elif gh_db.shape == curr_db.shape:
            pd.testing.assert_frame_equal(curr_db, gh_db)

        # subset test
        else:
            subset = curr_db.loc[gh_db.index]
            pd.testing.assert_frame_equal(subset, gh_db)
