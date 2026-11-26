# Copyright (c) 2023 Anton Zhiyanov, MIT License
# https://github.com/nalgeon/sqlite

.PHONY: build

SQLITE_RELEASE_YEAR := 2026
SQLITE_VERSION := 3540100
SQLEAN_VERSION := 0.29.0

prepare-src:
	mkdir -p sqlite
	rm -rf sqlite/*

download-sqlite:
	curl -L https://sqlite.org/$(SQLITE_RELEASE_YEAR)/sqlite-amalgamation-$(SQLITE_VERSION).zip --output sqlite.zip
	unzip -q sqlite.zip
	mv sqlite-amalgamation-$(SQLITE_VERSION)/* sqlite
	rmdir sqlite-amalgamation-$(SQLITE_VERSION)
	rm -f sqlite.zip

# Extensions bundled into the package (sqlean's src/<name> directories).
SQLEAN_MODULES := crypto define fileio fuzzy ipaddr math regexp stats text time uuid vsv

download-sqlean:
	curl -L https://github.com/nalgeon/sqlean/archive/refs/tags/$(SQLEAN_VERSION).zip --output sqlean.zip
	unzip -q sqlean.zip
	mv sqlean-$(SQLEAN_VERSION) sqlean-src
	# Fixes for MSVC, until they are upstream.
	for p in patches/*.patch; do patch -d sqlean-src -p1 --forward < $$p || exit 1; done
	# Copy each module directory as is: every .c file is compiled
	# as a separate translation unit (see setup.py), the same way
	# sqlean itself builds them. Never concatenate them.
	for m in $(SQLEAN_MODULES); do cp -R sqlean-src/src/$$m sqlite/; done
	cp sqlean-src/src/*.h sqlite/
	cat src/init.c >> sqlite/sqlite3.c
	cp src/init.h sqlite
	rm -rf sqlean-src
	rm -f sqlean.zip

clean:
	rm -rf build/*
	rm -f dist/*
	rm -rf sqlean/*.so
	rm -rf sqlean.py.egg-info

build:
	python -m pip install --upgrade setuptools wheel
	python setup.py build_ext -i
	python -m tests
	python -m pip wheel . -w dist
