# sqlean.py

This package provides an SQLite Python wrapper bundled with [`sqlean`](https://github.com/nalgeon/sqlean) extensions. It's a drop-in replacement for the standard library's [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) module.

```python
import sqlean as sqlite3

# has the same API as the default `sqlite3` module
conn = sqlite3.connect(":memory:")
conn.execute("create table employees(id, name)")

# and comes with the `sqlean` extensions
cur = conn.execute("select median(value) from generate_series(1, 99)")
print(cur.fetchone())
# (50.0,)

conn.close()
```

## Installation

A binary package (wheel) is available for the following operating systems:

-   Windows (64-bit)
-   Ubuntu (and other Debian-based distributions)
-   macOS (both Intel and Apple processors)

```
pip install sqlean.py
```

Note that the package name is `sqlean.py`, while the code imports are just `sqlean`. The `sqlean` package name was taken by some zomby project and the author seemed to be unavailable, so I had to add the `.py` suffix.

## Usage

```python
import sqlean as sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.execute("select median(value) from generate_series(1, 99)")
print(cur.fetchone())
conn.close()
```

## Building from source

For development purposes only.

```
python setup.py build_ext -i
python -m test
python -m pip wheel . -w dist
```

## License

Based on the [pysqlite3](https://github.com/coleifer/pysqlite3) project. Available under the [Zlib license](LICENSE).

## Stay tuned

Follow [**@ohmypy**](https://twitter.com/ohmypy) on Twitter to keep up with new features 🚀
