"""Tests the database integrity tests with mock files."""

from typing import Tuple

from test_database.conftest import *
from test_database import test_integrity as ti


def prepare_databases(
    gh_fname: Path, curr_fname: Path
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Prepare the github and current databases to use for testing the functions.

    These databases are instead of the fixture and we just pass them directly.

    :param gh_fname: Path to use for the `github` file.
    :param curr_fname: Path to use for the `current` file.

    :return: Tuple of dictionaries with github databases and current databases.
    """
    gh_dbs = {"sic": prepare_dataframe(gh_fname.absolute())}
    curr_dbs = {"sic": prepare_dataframe(curr_fname.absolute())}
    return gh_dbs, curr_dbs


# FIXTURES TEST #


def test_gh_download(gh_dbs):
    """Ensure github download results in a pandas dataframe."""
    assert isinstance(gh_dbs["sic.csv"], pd.DataFrame)


# @pytest.mark.curr_path(Path())
def test_curr_dbs(curr_dbs):
    """Ensure that the current database loading results in a pandas dataframe."""
    assert isinstance(curr_dbs["sic.csv"], pd.DataFrame)


# DATABASE TESTS #


@pytest.mark.parametrize(
    "cmp_fname",
    [Path("files/sic_cell_shift.csv"), Path("files/sic_cell_shift_added_data.csv")],
)
def test_db_cell_shift(cmp_fname, curr_path):
    """Raise AssertionError if a cell shift occured."""
    gh_fname = curr_path.joinpath("files/sic_original.csv")
    cmp_fname = curr_path.joinpath(cmp_fname)

    gh_dbs, curr_dbs = prepare_databases(gh_fname, cmp_fname)
    with pytest.raises(AssertionError) as err:
        ti.test_is_subset(gh_dbs, curr_dbs)

    assert "Existing values in the database have changed." == err.value.args[0]


@pytest.mark.parametrize(
    "cmp_fname",
    [
        Path("files/sic_deletion_wo_mod.csv"),
        Path("files/sic_modified_deletion_w_mod.csv"),
    ],
)
def test_db_deletion(cmp_fname, curr_path):
    """Raise Assertion error if an entry has been deleted."""
    gh_fname = curr_path.joinpath("files/sic_original.csv")
    cmp_fname = curr_path.joinpath(cmp_fname)

    gh_dbs, curr_dbs = prepare_databases(gh_fname, cmp_fname)
    with pytest.raises(AssertionError) as err:
        ti.test_is_subset(gh_dbs, curr_dbs)

    assert err.value.args[0] == "New database contains less entries than old one."


def test_db_diff_nof_cols(curr_path):
    """Raise AssertionError if number of columns is different."""
    gh_fname = curr_path.joinpath("files/sic_original.csv")
    cmp_fname = curr_path.joinpath("files/sic_diff_nof_col.csv")

    gh_dbs, curr_dbs = prepare_databases(gh_fname, cmp_fname)
    with pytest.raises(AssertionError) as err:
        ti.test_is_subset(gh_dbs, curr_dbs)

    assert err.value.args[0] == "The databases have different numbers of columns."


def test_db_stays_same(curr_path):
    """Ensure passing test if database stays the same."""
    gh_fname = curr_path.joinpath("files/sic_original.csv")
    cmp_fname = gh_fname

    gh_dbs, curr_dbs = prepare_databases(gh_fname, cmp_fname)
    ti.test_is_subset(gh_dbs, curr_dbs)


def test_db_modified_correct(curr_path):
    """Ensure passing test if db is modified correctly."""
    gh_fname = curr_path.joinpath("files/sic_original.csv")
    cmp_fname = curr_path.joinpath("files/sic_modified_correct.csv")

    gh_dbs, curr_dbs = prepare_databases(gh_fname, cmp_fname)
    ti.test_is_subset(gh_dbs, curr_dbs)
