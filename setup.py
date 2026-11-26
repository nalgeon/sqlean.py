# Originally by Gerhard Häring, zlib license
# https://github.com/ghaering/pysqlite

# Modified by Charles Leifer
# https://github.com/coleifer/pysqlite3

# Modified by Anton Zhiyanov
# https://github.com/nalgeon/sqlean.py

# SQLite Python wrapper bundled with Sqlean extensions.

import glob
import logging
import os
from pathlib import Path
import setuptools
import sys

from setuptools.command.build_ext import build_ext
from setuptools import Extension

log = logging.getLogger(__name__)

PACKAGE_NAME = "sqlean"
SQLEAN_VERSION = "0.29.0"
VERSION = "3.54.1.0"

SHORT_DESCRIPTION = "sqlite3 with extensions"
LONG_DESCRIPTION = Path("README.md").read_text()


# Module sources
sources = [
    os.path.join("src", source)
    for source in [
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
    ]
]

# Packages
packages = [PACKAGE_NAME]

# Sqlean extensions bundled into the package,
# vendored into sqlite/<name> by `make download-sqlean`.
SQLEAN_MODULES = (
    "crypto",
    "define",
    "fileio",
    "fuzzy",
    "ipaddr",
    "math",
    "regexp",
    "stats",
    "text",
    "time",
    "uuid",
    "vsv",
)

IS_MSVC = sys.platform == "win32"

define_macros = [("MODULE_NAME", '"%s.dbapi2"' % PACKAGE_NAME)]


class Builder(build_ext):
    description = "Builds a C extension using a sqlite3 amalgamation"

    amalgamation_root = "sqlite"

    def build_extension(self, ext):
        log.info(self.description)

        if IS_MSVC:
            ext.extra_compile_args.append("/O2")
            # sqlean uses C11 (_Static_assert, _Alignof, restrict),
            # which MSVC only accepts in C11 mode or later.
            ext.extra_compile_args.append("/std:c11")
        else:
            ext.extra_compile_args.append("-O2")
            # Python's sysconfig may pass flags the compiler doesn't use.
            if sys.platform == "darwin":
                ext.extra_compile_args.append("-Qunused-arguments")

        self._setup_defines(ext)
        self._setup_sources(ext)

        if not IS_MSVC:
            # Include math library, required for fts5.
            ext.extra_link_args.append("-lm")

        build_ext.build_extension(self, ext)

    def _setup_defines(self, ext):
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
        for feature in features:
            ext.define_macros.append(("SQLITE_%s" % feature, "1"))

        # Increase the maximum number of "host parameters" which SQLite will accept
        ext.define_macros.append(("SQLITE_MAX_VARIABLE_NUMBER", "250000"))

        # Increase maximum allowed memory-map size to 1TB
        ext.define_macros.append(("SQLITE_MAX_MMAP_SIZE", str(2**40)))

        # Auto-load sqlean extensions
        ext.define_macros.append(("SQLITE_EXTRA_INIT", "core_init"))
        ext.define_macros.append(("SQLEAN_VERSION", '"%s"' % SQLEAN_VERSION))

        # PCRE2 build constants (sqlean's regexp/constants.h)
        ext.define_macros.append(("PCRE2_CODE_UNIT_WIDTH", "8"))
        ext.define_macros.append(("LINK_SIZE", "2"))
        ext.define_macros.append(("HAVE_CONFIG_H", "1"))
        ext.define_macros.append(("SUPPORT_UNICODE", "1"))
        if sys.platform == "win32":
            ext.define_macros.append(("PCRE2_STATIC", "1"))

    def _setup_sources(self, ext):
        root = self.amalgamation_root
        ext.include_dirs.append(root)
        ext.sources.append(os.path.join(root, "sqlite3.c"))
        # Each sqlean source file is a separate translation unit.
        for module in SQLEAN_MODULES:
            pattern = os.path.join(root, module, "**", "*.c")
            files = sorted(glob.glob(pattern, recursive=True))
            if not files:
                raise RuntimeError(
                    f"no sources for sqlean module '{module}', run `make download-sqlean`"
                )
            ext.sources.extend(files)
        ext.sources.append(os.path.join("src", "sqlean.c"))

    def __setattr__(self, k, v):
        # Make sure we don't link against the SQLite
        # library, no matter what setup.cfg says
        if k == "libraries":
            v = None
        self.__dict__[k] = v


def get_setup_args():
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
        python_requires=">=3.10",
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
