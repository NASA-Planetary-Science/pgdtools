"""Package to interact with the presolar grain database."""

from setuptools_scm import get_version

from . import data, maintainer
from .classify import classify_grain
from .pgdtools import PresolarGrains

__all__ = ["PresolarGrains", "classify_grain", "data", "maintainer"]

print("Really early dev version... user beware!")

# Package information
__version__ = get_version(root="..", relative_to=__file__)

__title__ = "pgdtools"
__description__ = "Read and interact with the presolar grain database with python."

__uri__ = "https://pgdtools.readthedocs.io/en/latest/"
__author__ = "Reto Trappitsch"
__email__ = "reto@galactic-forensics.space"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2020-2023, Reto Trappitsch"
