"""Set up the local path for the database based on OS."""

from pathlib import Path
import sys


def setup_path() -> Path:
    """Set up the path to store data in the user's home directory.

    If the folder already exists, all is good and can continue to function.

    :return: Path to the database folder.
    """
    current_platform = sys.platform
    if current_platform == "win32" or current_platform == "cygwin":
        app_local_path = Path.home().joinpath("AppData/Roaming/pgdtools/")
    else:
        app_local_path = Path.home().joinpath(".config/pgdtools/")

    app_local_path.mkdir(parents=True, exist_ok=True)

    # create csv and config folders
    app_local_path.joinpath("csv").mkdir(parents=True, exist_ok=True)
    app_local_path.joinpath("config").mkdir(parents=True, exist_ok=True)

    return app_local_path
