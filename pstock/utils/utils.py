import random
import re
import typing as tp
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta

import httpx
import pendulum
from pydantic.datetime_parse import parse_date as parse_date_pydantic
from pydantic.datetime_parse import parse_datetime as parse_datetime_pydantic
from pydantic.datetime_parse import parse_duration as parse_duration_pydantic
from pydantic.errors import DateError, DateTimeError, DurationError

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
_USER_AGENT_LIST: tp.List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  # noqa
]


def rdm_user_agent_value() -> str:
    return random.choice(_USER_AGENT_LIST)


def parse_datetime(
    value: tp.Union[str, int, float, date, datetime]
) -> pendulum.DateTime:
    errors: tp.List[str] = []

    # try to parse a datetime string, int, bytes
    if not isinstance(value, date):
        try:
            return pendulum.instance(parse_datetime_pydantic(value))
        except (DateTimeError, TypeError) as error:
            errors.append(str(error))

    # if not above, maybe try to parse a date string, int, bytes object.
    try:
        _date = parse_date_pydantic(value)
        return pendulum.datetime(_date.year, _date.month, _date.day)
    except DateError as error:
        errors.append(str(error))
    raise ValueError(f"Couldn't parse to datetime: {value}: {', '.join(errors)}")


def parse_duration(value: tp.Union[str, int, float, timedelta]) -> pendulum.Duration:
    if isinstance(value, timedelta):
        return pendulum.duration(seconds=value.total_seconds())

    try:
        return pendulum.duration(seconds=parse_duration_pydantic(value).total_seconds())
    except DurationError as error:
        assert isinstance(value, str), str(error)

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


@asynccontextmanager
async def httpx_client_manager(
    client: tp.Optional[httpx.AsyncClient] = None,
) -> tp.AsyncGenerator[httpx.AsyncClient, None]:
    _close = False
    if client is None:
        _close = True
        client = httpx.AsyncClient()
    try:
        yield client
    finally:
        if _close:
            await client.aclose()
