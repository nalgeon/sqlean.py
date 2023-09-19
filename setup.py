# Originally by Gerhard Häring, zlib license
# https://github.com/ghaering/pysqlite

# Modified by Charles Leifer
# https://github.com/coleifer/pysqlite3

# Modified by Anton Zhiyanov
# https://github.com/nalgeon/sqlean.py
"""SQLite Python wrapper bundled with Sqlean extensions."""

# Future Imports
from __future__ import annotations

# Standard Library Imports
import logging
import os
import sys
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    TypeVar,
)

# Third-Party Imports
import setuptools
from setuptools import Extension
from setuptools.command.build_ext import build_ext

log = logging.getLogger(__name__)
SetupArg = TypeVar("SetupArg")


PACKAGE_NAME: str = "sqlean"
SQLEAN_VERSION: str = "0.21.8"
VERSION: str = f"{SQLEAN_VERSION}.3"

SHORT_DESCRIPTION: str = "sqlite3 with extensions"
LONG_DESCRIPTION: str = Path("README.md").read_text()


# Module sources
sources = [
    os.path.join("src", source)
    for source in (
        "module.c",
        "connection.c",
        "cursor.c",
        "cache.c",
        "microprotocols.c",
        "prepare_protocol.c",
        "statement.c",
        "util.c",
        "row.c",
        "blob.c",
    )
]

# Packages
packages = [PACKAGE_NAME]

# Work around clang raising hard error for unused arguments
if sys.platform == "darwin":
    os.environ["CFLAGS"] = "-Qunused-arguments"
    log.info("CFLAGS: " + os.environ["CFLAGS"])


def quote_argument(arg: str) -> str:
    """Apply the correct platform-specific quotes to the supplied argument."""
    q = '\\"' if sys.platform == "win32" and sys.version_info < (3, 7) else '"'
    return q + arg + q


define_macros: List[Tuple[str, ...]] = [
    ("MODULE_NAME", quote_argument(PACKAGE_NAME + ".dbapi2")),
]


class Builder(build_ext):
    """Custom C-extension builder."""

    description: str = "Builds a C extension using a sqlite3 amalgamation"
    amalgamation_root: str = "sqlite"

    def __setattr__(self, key: str, value: Any) -> None:
        # Make sure we don't link against the SQLite
        # library, no matter what setup.cfg says
        self.__dict__[key] = value if key != "libraries" else None

    def build_extension(self, ext: Extension) -> None:
        """Build the specified extension."""
        breakpoint()
        log.info(self.description)

        # gcc optimization level
        ext.extra_compile_args.append("-O1")

        # disable sign-comparison warning
        ext.extra_compile_args.append("-Wsign-compare")

        self._setup_defines(ext)
        self._setup_sources(ext)

        if sys.platform != "win32":
            # Include math library, required for fts5.
            ext.extra_link_args.append("-lm")

        build_ext.build_extension(self, ext)

    @staticmethod
    def _setup_defines(ext: Extension) -> None:
        """Set up the extensions macro definitions."""

        # sqlite options
        features = (
            "ENABLE_DBPAGE_VTAB",
            "ENABLE_DBSTAT_VTAB",
            "ENABLE_EXPLAIN_COMMENTS",
            "ENABLE_FTS4",
            "ENABLE_FTS5",
            "ENABLE_GEOPOLY",
            "ENABLE_JSON1",
            "ENABLE_MATH_FUNCTIONS",
            "ENABLE_RTREE",
            "ENABLE_STAT4",
            "ENABLE_STMTVTAB",
            "LIKE_DOESNT_MATCH_BLOBS",
            "USE_URI",
        )

        ext.define_macros.extend((("SQLITE_%s" % feature, "1") for feature in features))

        # Always use memory for temp store.
        ext.define_macros.append(("SQLITE_TEMP_STORE", "3"))

        # Increase the maximum number of "host parameters" which SQLite will accept
        ext.define_macros.append(("SQLITE_MAX_VARIABLE_NUMBER", "250000"))

        # Increase maximum allowed memory-map size to 1TB
        ext.define_macros.append(("SQLITE_MAX_MMAP_SIZE", str(2**40)))

        # Auto-load sqlean extensions
        ext.define_macros.append(("SQLITE_EXTRA_INIT", "core_init"))
        ext.define_macros.append(("SQLEAN_VERSION", quote_argument(SQLEAN_VERSION)))

        # Extension-specific flags
        ext.define_macros.append(("PCRE2_CODE_UNIT_WIDTH", "8"))
        ext.define_macros.append(("LINK_SIZE", "2"))
        ext.define_macros.append(("HAVE_CONFIG_H", "1"))
        ext.define_macros.append(("SUPPORT_UNICODE", "1"))

        if sys.platform == "win32":
            ext.define_macros.append(("BYTE_ORDER", "LITTLE_ENDIAN"))
            ext.define_macros.append(("PCRE2_STATIC", "1"))

    def _setup_sources(self, ext: Extension):
        """Set up the extensions source directories."""

        ext.include_dirs.append(self.amalgamation_root)

        ext.sources.extend(
            (
                os.path.join(self.amalgamation_root, "sqlite3.c"),
                os.path.join(self.amalgamation_root, "sqlean-crypto.c"),
                os.path.join(self.amalgamation_root, "sqlean-define.c"),
                os.path.join(self.amalgamation_root, "sqlean-fileio.c"),
                os.path.join(self.amalgamation_root, "sqlean-fuzzy.c"),
            )
        )

        if sys.platform != "win32":
            ext.sources.append(os.path.join(self.amalgamation_root, "sqlean-ipaddr.c"))

        ext.sources.extend(
            (
                os.path.join(self.amalgamation_root, "sqlean-regexp.c"),
                os.path.join(self.amalgamation_root, "sqlean-stats.c"),
                os.path.join(self.amalgamation_root, "sqlean-text.c"),
                os.path.join(self.amalgamation_root, "sqlean-unicode.c"),
                os.path.join(self.amalgamation_root, "sqlean-uuid.c"),
                os.path.join(self.amalgamation_root, "sqlean-vsv.c"),
                os.path.join("src", "sqlean.c"),
            )
        )


def get_setup_args() -> Dict[str, SetupArg]:
    """Construct a dictionary of the necessary setup arguments."""
    return dict(
        name=f"{PACKAGE_NAME}.py",
        version=VERSION,
        description=SHORT_DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        author="Anton Zhiyanov",
        author_email="m@antonz.org",
        license="zlib/libpng",
        platforms="ALL",
        url="https://github.com/nalgeon/sqlean.py",
        package_dir={PACKAGE_NAME: PACKAGE_NAME},
        packages=packages,
        ext_modules=[
            Extension(
                name=f"{PACKAGE_NAME}._sqlite3",
                sources=sources,
                define_macros=define_macros,
            )
        ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: zlib/libpng License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: C",
            "Programming Language :: Python",
            "Topic :: Database :: Database Engines/Servers",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        cmdclass={"build_ext": Builder},
    )


if __name__ == "__main__":
    setuptools.setup(**get_setup_args())
