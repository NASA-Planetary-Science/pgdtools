"""These routines test the database integrity."""

import numpy as np
import pandas as pd


def test_is_subset(gh_dbs, curr_dbs):
    """Ensure that the old database is a subset of the new one."""
    for key in curr_dbs:
        curr_db = curr_dbs[key]
        gh_db = gh_dbs[key]

        # some entries have been deleted
        if np.array([index not in curr_db.index for index in gh_db.index]).any():
            raise AssertionError("New database contains less entries than old one.")

        # Different numbers of columns
        elif curr_db.shape[1] != gh_db.shape[1]:
            raise AssertionError("The databases have different numbers of columns.")

        # same rows and columns
        elif gh_db.shape == curr_db.shape:
            try:
                pd.testing.assert_frame_equal(curr_db, gh_db)
            except AssertionError as err:
                raise AssertionError(
                    "Existing values in the database have changed."
                ) from err

        # subset test
        else:
            subset = curr_db.loc[gh_db.index]
            try:
                pd.testing.assert_frame_equal(subset, gh_db)
            except AssertionError as err:
                raise AssertionError(
                    "Existing values in the database have changed."
                ) from err
