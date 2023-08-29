"""Local database management for various PGD versions."""

from pgdtools.data import BIBFILE, DB_JSON, REFERENCES_JSON, TECHNIQUES_JSON
from . import setup_local
from .config import DataBases
from .management import current, set_current, update

LOCAL_PATH = setup_local.setup_path()  # where to store data

LOCAL_CURRENT = LOCAL_PATH.joinpath("current.json")  # current configuration

LOCAL_BIB = LOCAL_PATH.joinpath(f"config/{BIBFILE.split('/')[-1]}")
LOCAL_DB_JSON = LOCAL_PATH.joinpath(f"config/{DB_JSON.split('/')[-1]}")
LOCAL_REF_JSON = LOCAL_PATH.joinpath(f"config/{REFERENCES_JSON.split('/')[-1]}")
LOCAL_TECH_JSON = LOCAL_PATH.joinpath(f"config/{TECHNIQUES_JSON.split('/')[-1]}")

__all__ = ["current", "DataBases", "set_current", "update"]
