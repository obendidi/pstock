from datetime import date, datetime, timedelta
import pendulum

import pytest
from dateutil import tz
from pydantic import DurationError, BaseModel, ValidationError

from pstock.core import parse_datetime, parse_duration, TimeStamp

datetime_testcases = [
    (1346887571, 1346887571),
    ("1346887571", 1346887571),
    (1346887571.123789, 1346887571),
    ("2012-04-23T11:05:00-25:00", ValueError),
    (datetime(2022, 1, 1, hour=1, minute=30, tzinfo=None), 1641000600),
    (datetime(2022, 1, 1, hour=1, minute=30, tzinfo=tz.UTC), 1641000600),
    (
        datetime(2022, 1, 1, hour=1, minute=30, tzinfo=tz.gettz("America/New_York")),
        1641018600,
    ),
    (date(2022, 1, 1), 1640995200),
    ("2022-01-01", 1640995200),
]
datetime_ids = [
    "int",
    "str",
    "float",
    "datetime-error",
    "datetime-no-timezone",
    "datetime-utc",
    "datetime-tz",
    "date-object",
    "date-str",
]


@pytest.mark.parametrize("value,expected", datetime_testcases, ids=datetime_ids)
def test_parse_datetime(value, expected):
    if type(expected) == type and issubclass(expected, BaseException):
        with pytest.raises(expected):
            parse_datetime(value)
    else:
        assert parse_datetime(value).int_timestamp == expected


duration_testcases = [
    (timedelta(days=3.5), pendulum.duration(days=3.5)),
    (pendulum.duration(days=3.5), pendulum.duration(days=3.5)),
    (datetime(2022, 1, 1, hour=1), TypeError),
    ("1m", pendulum.duration(minutes=1)),
    ("2m", pendulum.duration(minutes=2)),
    ("5m", pendulum.duration(minutes=5)),
    ("15m", pendulum.duration(minutes=15)),
    ("30m", pendulum.duration(minutes=30)),
    ("1h", pendulum.duration(hours=1)),
    ("1d", pendulum.duration(days=1)),
    ("5d", pendulum.duration(days=5)),
    ("1mo", pendulum.duration(months=1)),
    ("3mo", pendulum.duration(months=3)),
    ("1y", pendulum.duration(years=1)),
    ("ytd", pendulum.duration(years=1)),
    ("mtd", pendulum.duration(months=1)),
    ("1d 1mo 1d", pendulum.duration(months=1, days=2)),
    ("3mo2.5d33m", pendulum.duration(months=3, days=2.5, minutes=33)),
    ("3Days 5Hours", pendulum.duration(days=3, hours=5)),
    ("3 Days", DurationError),
    ("5k", DurationError),
    ("str", DurationError),
]
duration_ids = [
    "timedelta",
    "pendulum.duration",
    "datetime",
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "1h",
    "1d",
    "5d",
    "1mo",
    "3mo",
    "1y",
    "ytd",
    "mtd",
    "1d 1mo 1d",
    "3mo2.5d33m",
    "3Days 5Hours",
    "3 Days-durationError",
    "5k-durationError",
    "str-durationError",
]


@pytest.mark.parametrize("value,expected", duration_testcases, ids=duration_ids)
def test_parse_duration(value, expected):
    if type(expected) == type and issubclass(expected, BaseException):
        with pytest.raises(expected):
            parse_duration(value)
    else:
        assert parse_duration(value) == expected


class _TestModel(BaseModel):
    value: TimeStamp


@pytest.mark.parametrize("value,expected", datetime_testcases, ids=datetime_ids)
def test_TimeStamp_in_pydantic_BaseModel(value, expected):
    if type(expected) == type and issubclass(expected, BaseException):
        with pytest.raises(ValidationError):
            _TestModel(value=value)
    else:
        assert _TestModel(value=value).value == expected
