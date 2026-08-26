"""Package to interact with the presolar grain database."""

from . import data, db, maintainer
from .classify import classify_sic_grain
from .pgdtools import PresolarGrains

_pgd: PresolarGrains | None = None


def __getattr__(name: str):
    """Lazily initialize module attributes."""
    if name == "pgd":
        global _pgd
        if _pgd is None:
            _pgd = PresolarGrains()
        return _pgd
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "PresolarGrains",
    "classify_sic_grain",
    "data",
    "db",
    "maintainer",
    "pgd",
]
