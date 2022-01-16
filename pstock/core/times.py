import re
import typing as tp
from datetime import datetime, timedelta

import pendulum
from pydantic.datetime_parse import parse_datetime as parse_datetime_pydantic
from pydantic.datetime_parse import parse_duration as parse_duration_pydantic
from pydantic.errors import DurationError

__all__ = ("TimeStamp", "parse_duration", "parse_datetime")

_UNITS_REGEX = r"(?P<val>\d+(\.\d+)?)(?P<unit>(mo|s|m|h|d|w|y)?)"
_UNITS = {
    "s": ("seconds", float),
    "m": ("minutes", float),
    "h": ("hours", float),
    "d": ("days", float),
    "w": ("weeks", float),
    "mo": ("months", int),
    "y": ("years", int),
}


class TimeStamp(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: tp.Union[str, int, float, datetime]) -> int:
        return parse_datetime(value).int_timestamp


def parse_datetime(value: tp.Union[str, int, float, datetime]) -> pendulum.DateTime:
    return pendulum.instance(parse_datetime_pydantic(value))


def parse_duration(value: tp.Union[str, int, float, timedelta]) -> pendulum.Duration:
    if isinstance(value, timedelta):
        return pendulum.duration(seconds=value.total_seconds())

    try:
        return pendulum.duration(seconds=parse_duration_pydantic(value).total_seconds())
    except DurationError as error:
        if not isinstance(value, str):
            raise TypeError(
                "Pydantic couldn't parse provided duration, only 'str' type"
                " is supported for custom parsing"
            ) from error

    if value.lower() == "mtd":
        return pendulum.duration(months=1)
    if value.lower() == "ytd":
        return pendulum.duration(years=1)

    kwargs: tp.Dict[str, float] = {}
    for match in re.finditer(_UNITS_REGEX, value, flags=re.I):
        unit = match.group("unit").lower()
        val = match.group("val")
        if unit not in _UNITS:
            raise DurationError()
        name, _type = _UNITS[unit]
        if name in kwargs:
            kwargs[name] += _type(val)
        else:
            kwargs[name] = _type(val)

    if not kwargs:
        raise DurationError()
    return pendulum.duration(**kwargs)
