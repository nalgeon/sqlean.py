// Copyright (c) 2023 Anton Zhiyanov, MIT License
// https://github.com/nalgeon/sqlean.py

// Sqlean extensions bundle.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

// extensions
#include "crypto/extension.h"
#include "define/extension.h"
#include "fileio/extension.h"
#include "fuzzy/extension.h"
#include "ipaddr/extension.h"
#include "math/extension.h"
#include "regexp/extension.h"
#include "stats/extension.h"
#include "text/extension.h"
#include "time/extension.h"
#include "uuid/extension.h"
#include "vsv/extension.h"

// sqlean header
#include "sqlean.h"

// sqlean_version returns the current Sqlean version.
static void sqlean_version(sqlite3_context* context, int argc, sqlite3_value** argv) {
    sqlite3_result_text(context, SQLEAN_VERSION, -1, SQLITE_STATIC);
}

// init_all initializes all extensions.
static int init_all(sqlite3* db) {
    crypto_init(db);
    fileio_init(db);
    fuzzy_init(db);
    ipaddr_init(db);
    math_init(db);
    regexp_init(db);
    stats_init(db);
    text_init(db);
    time_init(db);
    uuid_init(db);
    vsv_init(db);
    // define must go last, so that user-defined functions
    // can call any other sqlean function.
    define_init(db);
    return SQLITE_OK;
}

// init_extension initializes the extension if it's enabled according to the env variable.
static int init_extension(const char* flag, int (*init_fn)(sqlite3* db), sqlite3* db) {
    const char* enabled = getenv(flag);
    if (enabled == NULL || strcmp(enabled, "0") == 0) {
        // disable the extension unless it is explicitly enabled
        return SQLITE_OK;
    }
    return init_fn(db);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
    int sqlite3_sqlean_init(sqlite3* db, char** errmsg_ptr, const sqlite3_api_routines* api) {
    (void)errmsg_ptr;
    SQLITE_EXTENSION_INIT2(api);

    const char* enable_all = getenv("SQLEAN_ENABLE");
    if (enable_all != NULL && strcmp(enable_all, "0") == 0) {
        // SQLEAN_ENABLE == 0, disable all extensions
        return SQLITE_OK;
    }

    static const int flags = SQLITE_UTF8 | SQLITE_INNOCUOUS | SQLITE_DETERMINISTIC;
    sqlite3_create_function(db, "sqlean_version", 0, flags, 0, sqlean_version, 0, 0);

    if (enable_all != NULL) {
        // SQLEAN_ENABLE != 0, enable all extensions
        init_all(db);
        return SQLITE_OK;
    }

    // SQLEAN_ENABLE is not set, enable individual extensions
    init_extension("SQLEAN_ENABLE_CRYPTO", crypto_init, db);
    init_extension("SQLEAN_ENABLE_FILEIO", fileio_init, db);
    init_extension("SQLEAN_ENABLE_FUZZY", fuzzy_init, db);
    init_extension("SQLEAN_ENABLE_IPADDR", ipaddr_init, db);
    init_extension("SQLEAN_ENABLE_MATH", math_init, db);
    init_extension("SQLEAN_ENABLE_REGEXP", regexp_init, db);
    init_extension("SQLEAN_ENABLE_STATS", stats_init, db);
    init_extension("SQLEAN_ENABLE_TEXT", text_init, db);
    init_extension("SQLEAN_ENABLE_TIME", time_init, db);
    init_extension("SQLEAN_ENABLE_UUID", uuid_init, db);
    init_extension("SQLEAN_ENABLE_VSV", vsv_init, db);
    init_extension("SQLEAN_ENABLE_DEFINE", define_init, db);
    return SQLITE_OK;
}
