from datetime import date, datetime

import pytest
from dateutil import tz
from pydantic import DateTimeError

from pstock.core import TimeStamp

timestamp_testcases = [
    (1346887571, 1346887571),
    ("1346887571", 1346887571),
    (1346887571.123789, 1346887571),
    ("2012-04-23T11:05:00-25:00", DateTimeError),
    (datetime(2022, 1, 1, hour=1, minute=30, tzinfo=None), 1641000600),
    (datetime(2022, 1, 1, hour=1, minute=30, tzinfo=tz.UTC), 1641000600),
    (
        datetime(2022, 1, 1, hour=1, minute=30, tzinfo=tz.gettz("America/New_York")),
        1641018600,
    ),
    (date(2022, 1, 1), TypeError),
]
timestamp_ids = [
    "int",
    "str",
    "float",
    "datetime-error",
    "datetime-no-timezone",
    "datetime-utc",
    "datetime-tz",
    "date-error",
]


@pytest.mark.parametrize("value,expected", timestamp_testcases, ids=timestamp_ids)
def test_timestamp_validate(value, expected):
    if type(expected) == type and issubclass(expected, Exception):
        with pytest.raises(expected):
            TimeStamp.validate(value)
    else:
        assert TimeStamp.validate(value) == expected
