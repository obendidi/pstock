import random
import typing as tp
from datetime import datetime

import pendulum
from pydantic import BaseModel, Field, validator

from pstock.core import TimeStamp, parse_datetime, parse_duration

_ValidInterval = tp.Literal[
    "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"
]
_AutoValidInterval = tp.Union[tp.Literal["auto"], _ValidInterval]
_ValidRange = tp.Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]
_ValidIntervals = tp.Tuple[_ValidInterval, ...]

_VALID_INTERVALS: _ValidIntervals = tp.get_args(_ValidInterval)
_MAX_DAYS_TO_VALID_INTERVALS: tp.Dict[float, _ValidIntervals] = {
    7: _VALID_INTERVALS,  # all
    59.9: _VALID_INTERVALS[1:],  # 2m and above
    729.9: _VALID_INTERVALS[5:],  # 1h and above
}
# by default smallest always valid interval is 1d
_DEFAULT_VALID_INTERVALS: _ValidIntervals = _VALID_INTERVALS[6:]

_USER_AGENT_LIST: tp.List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  # noqa
]


def _user_agent_header() -> tp.Dict[str, str]:
    return {"User-Agent": random.choice(_USER_AGENT_LIST)}


class _YFChartParams(BaseModel):
    interval: _ValidInterval
    period: tp.Optional[_ValidRange] = Field(alias="range")
    start: tp.Optional[TimeStamp] = Field(alias="period1")
    end: tp.Optional[TimeStamp] = Field(alias="period2")
    include_prepost: bool = Field(default=False, alias="includePrePost")
    events: tp.Literal["div", "split", "div,splits"] = "div,splits"

    @validator("start", always=True)
    def check_start_or_period(
        cls, value: tp.Optional[TimeStamp], values: tp.Dict[str, tp.Any]
    ) -> tp.Optional[TimeStamp]:
        if value is None and values.get("period") is None:
            raise ValueError("Please provide either a 'start' or 'period' value.")
        return value

    @validator("end", always=True)
    def end_value_factory(
        cls, value: tp.Optional[TimeStamp], values: tp.Dict[str, tp.Any]
    ) -> tp.Optional[int]:
        if value is not None:
            return value
        if values.get("start") is not None:
            return TimeStamp.validate(pendulum.now())

        return None

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True


def _get_valid_intervals(
    interval: _AutoValidInterval,
    period: tp.Optional[_ValidRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
) -> _ValidIntervals:
    if interval != "auto":
        return (interval,)
    if period is not None:
        if period == "max":
            return ("3mo",)
        delta = parse_duration(period)
    elif start is not None:
        delta = pendulum.now() - parse_datetime(start)
    else:
        raise ValueError("Please provide either 'start' or 'period'.")

    for max_days, valid_intervals in _MAX_DAYS_TO_VALID_INTERVALS.items():
        if delta.days <= max_days:
            return valid_intervals
    return _DEFAULT_VALID_INTERVALS
