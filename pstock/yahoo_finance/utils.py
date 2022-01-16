import random
import typing as tp
from datetime import datetime

import pendulum
from pydantic import BaseModel, Field, validator

from pstock.core import TimeStamp, parse_datetime, parse_duration

ValidInterval = tp.Literal[
    "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"
]
AutoValidInterval = tp.Union[tp.Literal["auto"], ValidInterval]
ValidRange = tp.Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]
ValidIntervals = tp.Tuple[ValidInterval, ...]

VALID_INTERVALS: ValidIntervals = tp.get_args(ValidInterval)
MAX_DAYS_TO_VALID_INTERVALS: tp.Dict[float, ValidIntervals] = {
    7: VALID_INTERVALS,  # all
    59.9: VALID_INTERVALS[1:],  # 2m and above
    729.9: VALID_INTERVALS[5:],  # 1h and above
}
# by default smallest always valid interval is 1d
DEFAULT_VALID_INTERVALS: ValidIntervals = VALID_INTERVALS[6:]

USER_AGENT_LIST: tp.List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  # noqa
]


def user_agent_header() -> tp.Dict[str, str]:
    return {"User-Agent": random.choice(USER_AGENT_LIST)}


class YFChartParams(BaseModel):
    interval: ValidInterval
    period: tp.Optional[ValidRange] = Field(alias="range")
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


def get_valid_intervals(
    interval: AutoValidInterval,
    period: tp.Optional[ValidRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
) -> ValidIntervals:
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

    for max_days, valid_intervals in MAX_DAYS_TO_VALID_INTERVALS.items():
        if delta.days <= max_days:
            return valid_intervals
    return DEFAULT_VALID_INTERVALS
