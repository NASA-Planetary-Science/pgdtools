"""Package to interact with the presolar grain database."""

# import the standard modules
from . import data, db, maintainer
from .classify import classify_grain
from .pgdtools import PresolarGrains


__all__ = ["classify_grain", "data", "db", "maintainer", "PresolarGrains"]

print("Really early dev version... user beware!")

# Package information
__version__ = "0.0.1"

__title__ = "pgdtools"
__description__ = "Read and interact with the presolar grain database with python."

__uri__ = "https://pgdtools.readthedocs.io/en/latest/"
__author__ = "Reto Trappitsch"
__email__ = "reto@galactic-forensics.space"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2020-2023, Reto Trappitsch"
