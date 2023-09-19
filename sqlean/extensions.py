"""Extension management."""

# Future Imports
from __future__ import annotations

# Standard Library Imports
import os
from typing import Set

_known_extensions: Set[str] = {
    "CRYPTO",
    "DEFINE",
    "FILEIO",
    "FUZZY",
    "IPADDR",
    "REGEXP",
    "STATS",
    "TEXT",
    "UNICODE",
    "UUID",
    "VSV",
}


def enable_all() -> None:
    """Enables all extensions."""
    os.environ["SQLEAN_ENABLE"] = "1"


def disable_all() -> None:
    """Disables all extensions."""
    os.environ["SQLEAN_ENABLE"] = "0"


def enable(*names: str) -> None:
    """Enables specific extensions."""

    _clear_flags()

    for name in _known_extensions.intersection(map(str.upper, names)):
        os.environ[f"SQLEAN_ENABLE_{name}"] = "1"


def disable(*names: str) -> None:
    """Disable the specified extension(s)."""

    _clear_flags()

    for name in _known_extensions.intersection(map(str.upper, names)):
        os.environ[f"SQLEAN_ENABLE_{name}"] = "0"


def _clear_flags():
    """Clears 'enabled' flags for all extensions."""
    for flag in (
        "SQLEAN_ENABLE",
        *map(
            "SQLEAN_ENABLE_%s".__mod__,
            _known_extensions,
        ),
    ):
        os.environ.pop(flag, None)
