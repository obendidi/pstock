import random
import typing as tp
from datetime import datetime

import pendulum
from pydantic import BaseModel, Field, validator

import pstock

from .settings import YFInterval, YFRange

USER_AGENT_LIST: tp.List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  # noqa
]


def random_user_agent() -> str:
    return random.choice(USER_AGENT_LIST)


class YFParams(BaseModel):
    interval: YFInterval
    start: tp.Optional[pstock.TimeStamp] = Field(alias="period1")
    end: tp.Optional[pstock.TimeStamp] = Field(alias="period2")
    period: tp.Optional[YFRange] = Field(alias="range")
    include_prepost: bool = Field(default=False, alias="includePrePost")
    events: tp.Literal["div", "split", "div,splits"] = "div,splits"

    @validator("period", always=True)
    def check_start_or_period(
        cls, value: tp.Optional[YFRange], values: tp.Dict[str, tp.Any]
    ) -> tp.Optional[YFRange]:
        if value is None and values.get("start") is None:
            return "max"
        return value

    @validator("end", always=True)
    def end_value_factory(
        cls, value: tp.Optional[pstock.TimeStamp], values: tp.Dict[str, tp.Any]
    ) -> tp.Optional[int]:
        if value is not None:
            return value
        if values.get("start") is not None:
            return pstock.TimeStamp.validate(pendulum.now())

        return None

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True


def get_valid_intervals(
    interval: tp.Union[tp.Literal["auto"], YFInterval],
    period: tp.Optional[YFRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
) -> tp.Tuple[YFInterval, ...]:
    if interval != "auto":
        return (interval,)
    if period == "max" or (period is None and start is None):
        return pstock.config.yf.CHART_INTERVALS_MAPPING_MAX
    if period is not None:
        delta = pstock.parse_duration(period)
    elif start is not None:
        delta = pendulum.now() - pstock.parse_datetime(start)

    for max_days, valid_intervals in pstock.config.yf.CHART_INTERVALS_MAPPING.items():
        if delta <= pstock.parse_duration(max_days):
            return valid_intervals
    return pstock.config.yf.CHART_INTERVALS_MAPPING_DEFAULT
