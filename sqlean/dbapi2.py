# Copyright (C) 2004-2005 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
"""DB-API 2.0 interface for SQLite databases."""

# Future Imports
from __future__ import annotations

# Standard Library Imports
import collections.abc
import datetime
import time
from typing import Union

# Third-Party Imports
from sqlean._sqlite3 import *

apilevel: str = "2.0"
paramstyle: str = "qmark"
threadsafety: int = 1

Date = datetime.date
Time = datetime.time
Binary = memoryview
Timestamp = datetime.datetime


def DateFromTicks(ticks: Union[int, float]) -> Date:
    """Convert the supplied `ticks` to the equivalent local date."""
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks: Union[int, float]) -> Time:
    """Convert the supplied `ticks` to the equivalent local time."""
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks: Union[int, float]) -> Timestamp:
    """Convert the supplied `ticks` to the equivalent local datetime."""
    return Timestamp(*time.localtime(ticks)[:6])


version_info = tuple(map(int, version.split(".")))
sqlite_version_info = tuple(map(int, sqlite_version.split(".")))
register_sequence_type = getattr(collections.abc.Sequence, "register", None)


if callable(register_sequence_type):
    register_sequence_type(Row)


def register_adapters_and_converters() -> None:
    """Register converter and adapter functions for the date/time types sqlite
    doesn't handle natively."""

    def adapt_date(value: datetime.date) -> str:
        """Convert the supplied `value` to the equivalent iso-formatted
        string."""
        return value.isoformat()

    def adapt_datetime(value: datetime.datetime) -> str:
        """Convert the supplied `value` to the equivalent iso-formatted
        string."""
        return value.isoformat(" ")

    def convert_date(value: bytes) -> Date:
        """Convert the supplied raw `value` to a Python-native date object."""
        return Date(*map(int, value.split(b"-")))

    def convert_timestamp(value: bytes) -> Timestamp:
        """Convert the supplied raw `value` to a Python-native datetime
        object."""

        date_part, time_part = value.split(b" ")
        year, month, day = map(int, date_part.split(b"-"))
        time_part_full = time_part.split(b".")
        hours, minutes, seconds = map(int, time_part_full[0].split(b":"))

        if len(time_part_full) == 2:
            microseconds = int("{:0<6.6}".format(time_part_full[1].decode()))
        else:
            microseconds = 0

        value = Timestamp(year, month, day, hours, minutes, seconds, microseconds)

        return value

    register_adapter(Date, adapt_date)
    register_adapter(Timestamp, adapt_datetime)
    register_converter("date", convert_date)
    register_converter("timestamp", convert_timestamp)


register_adapters_and_converters()

# Clean up namespace
del register_sequence_type, register_adapters_and_converters
