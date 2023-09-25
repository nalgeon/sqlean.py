# sqlean.py

This package provides an SQLite Python wrapper bundled with [`sqlean`](https://github.com/nalgeon/sqlean) extensions. It's a drop-in replacement for the standard library's [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) module.

```
pip install sqlean.py
```

```python
import sqlean

# enable all extensions
sqlean.extensions.enable_all()

# has the same API as the default `sqlite3` module
conn = sqlean.connect(":memory:")
conn.execute("create table employees(id, name)")

# and comes with the `sqlean` extensions
cur = conn.execute("select median(value) from generate_series(1, 99)")
print(cur.fetchone())
# (50.0,)

conn.close()
```

## Extensions

`sqlean.py` contains 12 essential SQLite extensions:

| Extension | Description | Safety concerns<br>*Last update: 2023-09-25* |
|-----------|-------------|----------------------------------------------|
| [crypto](https://github.com/nalgeon/sqlean/blob/main/docs/crypto.md) | Hashing, encoding and decoding data | Safe |
| [define](https://github.com/nalgeon/sqlean/blob/main/docs/define.md) | User-defined functions and dynamic SQL | Safe |
| [fileio](https://github.com/nalgeon/sqlean/blob/main/docs/fileio.md) | Reading and writing files | **Unsafe**: allows arbitrary file reading and writing. |
| [fuzzy](https://github.com/nalgeon/sqlean/blob/main/docs/fuzzy.md) | Fuzzy string matching and phonetics | Safe |
| [ipaddr](https://github.com/nalgeon/sqlean/blob/main/docs/ipaddr.md) | IP address manipulation | Safe |
| [math](https://github.com/nalgeon/sqlean/blob/main/docs/math.md) | Math functions | Safe |
| [regexp](https://github.com/nalgeon/sqlean/blob/main/docs/regexp.md) | Regular expressions | **Unsafe**: allows DOS attacks due to the non-linear behavior of some functions. |
| [stats](https://github.com/nalgeon/sqlean/blob/main/docs/stats.md) | Math statistics | Safe |
| [text](https://github.com/nalgeon/sqlean/blob/main/docs/text.md) | String functions | Safe |
| [unicode](https://github.com/nalgeon/sqlean/blob/main/docs/unicode.md) | Unicode support | Safe |
| [uuid](https://github.com/nalgeon/sqlean/blob/main/docs/uuid.md) | Universally Unique IDentifiers | Safe |
| [vsv](https://github.com/nalgeon/sqlean/blob/main/docs/vsv.md) | CSV files as virtual tables | **Unsafe**: allows arbitrary file reading and writing. |

Additionally, `sqlean.py` activates commonly used compile-time SQLite extensions and features, as specified in the `_setup_defines` function within the [`setup.py`](https://github.com/nalgeon/sqlean.py/blob/main/setup.py) script.

## Installation

A binary package (wheel) is available for the following operating systems:

-   Windows (64-bit)
-   Linux (64-bit)
-   macOS (both Intel and Apple processors)

```
pip install sqlean.py
```

Note that the package name is `sqlean.py`, while the code imports are just `sqlean`. The `sqlean` package name was taken by some zomby project and the author seemed to be unavailable, so I had to add the `.py` suffix.

## Usage

All extensions are disabled by default. You can still use `sqlean` as a drop-in replacement for `sqlite3`:

```python
import sqlean as sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.execute("select 'sql is awesome'")
print(cur.fetchone())
conn.close()
```

To enable all extensions, call `sqlean.extensions.enable_all()` before calling `connect()`:

```python
import sqlean

sqlean.extensions.enable_all()

conn = sqlean.connect(":memory:")
cur = conn.execute("select median(value) from generate_series(1, 99)")
print(cur.fetchone())
conn.close()
```

To enable specific extensions, call `sqlean.extensions.enable()`:

```python
import sqlean

sqlean.extensions.enable("stats", "text")

conn = sqlean.connect(":memory:")
cur = conn.execute("select median(value) from generate_series(1, 99)")
print(cur.fetchone())
conn.close()
```

## Building from source

For development purposes only.

Prepare source files:

```
make prepare-src
make download-sqlite
make download-sqlean
```

Build and test the package:

```
make clean
python setup.py build_ext -i
python -m test
python -m pip wheel . -w dist
```

## Credits

Based on the [pysqlite3](https://github.com/coleifer/pysqlite3) project. Available under the [Zlib license](LICENSE).

## Stay tuned

[**Subscribe**](https://antonz.org/subscribe/) to stay on top of new features 🚀
