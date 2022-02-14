from __future__ import annotations

import json
import typing as tp
from datetime import datetime, timedelta
from urllib.parse import urlencode

import asyncer
import httpx
import pandas as pd
import pendulum
from pydantic import validate_arguments

from pstock.base import BaseModel, BaseModelMapping, BaseModelSequence
from pstock.types import ReadableResponse, Timestamp
from pstock.utils.chart import get_ohlc_from_chart
from pstock.utils.utils import httpx_client_manager, parse_datetime, parse_duration

IntervalParam = tp.Literal[
    "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"
]
PeriodParam = tp.Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]
EventParam = tp.Literal["div", "split", "div,splits"]


def _get_lowest_valid_interval(
    *, period: tp.Optional[PeriodParam], start: tp.Optional[Timestamp]
) -> IntervalParam:
    if period == "max":
        return "3mo"

    if period is not None:
        delta = parse_duration(period)
    elif start is not None:
        delta = pendulum.now() - parse_datetime(start)
    else:
        raise ValueError(f"period={period}, start={start}")

    if delta <= pendulum.duration(days=7):
        return "1m"
    elif delta <= pendulum.duration(days=60):
        return "2m"
    elif delta <= pendulum.duration(days=730):
        return "1h"
    else:
        return "1d"


def _get_largest_valid_period(
    interval: tp.Optional[IntervalParam] = None,
) -> PeriodParam:
    if interval is None:
        return "max"
    delta = parse_duration(interval)
    if delta <= pendulum.duration(minutes=1):
        return "5d"
    elif delta <= pendulum.duration(minutes=2):
        return "1mo"
    elif delta <= pendulum.duration(hours=1):
        return "2y"
    elif delta <= pendulum.duration(days=1):
        return "10y"
    else:
        return "max"


class Bar(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float
    interval: timedelta


class _BarMixin:
    @staticmethod
    def base_uri(symbol: str) -> str:
        return f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol.upper()}"

    @staticmethod
    @validate_arguments
    def params(
        interval: tp.Optional[IntervalParam] = None,
        period: tp.Optional[PeriodParam] = None,
        start: tp.Optional[Timestamp] = None,
        end: tp.Optional[Timestamp] = None,
        events: EventParam = "div,splits",
        include_prepost: bool = False,
    ) -> tp.Dict[str, tp.Any]:
        if period is None and start is None:
            period = _get_largest_valid_period(interval=interval)

        if end is None and start is not None:
            end = pendulum.now().int_timestamp

        if interval is None:
            interval = _get_lowest_valid_interval(period=period, start=start)

        _params: tp.Dict[str, tp.Any] = {
            "interval": interval,
            "events": events,
            "includePrePost": include_prepost,
        }
        if period is not None:
            _params["range"] = period
        if start is not None:
            _params["period1"] = start
        if end is not None:
            _params["period2"] = end

        return _params

    @classmethod
    def uri(
        cls,
        symbol: str,
        *,
        interval: tp.Optional[IntervalParam] = None,
        period: tp.Optional[PeriodParam] = None,
        start: tp.Optional[Timestamp] = None,
        end: tp.Optional[Timestamp] = None,
        events: EventParam = "div,splits",
        include_prepost: bool = False,
    ) -> str:
        params = cls.params(
            interval=interval,
            period=period,
            start=start,
            end=end,
            events=events,
            include_prepost=include_prepost,
        )
        return f"{cls.base_uri(symbol)}?{urlencode(params)}"


class Bars(BaseModelSequence[Bar], _BarMixin):
    __root__: tp.List[Bar]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        if not df.empty:
            df = df.dropna(
                how="all",
                subset=["open", "high", "low", "close", "adj_close", "volume"],
            )
            if df["interval"][0] >= timedelta(days=1):
                df["date"] = pd.to_datetime(pd.to_datetime(df["date"]).dt.date)
            df = df.set_index("date").sort_index()
        return df

    @classmethod
    def load(
        cls,
        *,
        response: tp.Union[ReadableResponse, str, bytes, dict],
    ) -> Bars:
        if isinstance(response, dict):
            data = response
        elif isinstance(response, (str, bytes)):
            data = json.loads(response)
        else:
            data = json.loads(response.read())

        return cls.parse_obj(get_ohlc_from_chart(data))

    @classmethod
    async def get(
        cls,
        symbol: str,
        *,
        interval: tp.Optional[IntervalParam] = None,
        period: tp.Optional[PeriodParam] = None,
        start: tp.Optional[Timestamp] = None,
        end: tp.Optional[Timestamp] = None,
        events: EventParam = "div,splits",
        include_prepost: bool = False,
        client: tp.Optional[httpx.AsyncClient] = None,
    ):
        url = cls.base_uri(symbol)
        params = cls.params(
            interval=interval,
            period=period,
            start=start,
            end=end,
            events=events,
            include_prepost=include_prepost,
        )
        async with httpx_client_manager(client=client) as _client:
            response = await _client.get(url, params=params)

        return cls.load(response=response)


class BarsMulti(BaseModelMapping[Bars], _BarMixin):
    __root__: tp.Dict[str, Bars]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        return df.sort_index()

    @classmethod
    async def get(
        cls,
        symbols: tp.List[str],
        *,
        interval: tp.Optional[IntervalParam] = None,
        period: tp.Optional[PeriodParam] = None,
        start: tp.Optional[Timestamp] = None,
        end: tp.Optional[Timestamp] = None,
        events: EventParam = "div,splits",
        include_prepost: bool = False,
        client: tp.Optional[httpx.AsyncClient] = None,
    ):
        async with httpx_client_manager(client=client) as _client:
            async with asyncer.create_task_group() as tg:
                soon_values = [
                    tg.soonify(Bars.get)(
                        symbol,
                        interval=interval,
                        period=period,
                        start=start,
                        end=end,
                        include_prepost=include_prepost,
                        events=events,
                        client=_client,
                    )
                    for symbol in symbols
                ]
        data = {
            symbol: soon_value.value for symbol, soon_value in zip(symbols, soon_values)
        }
        return cls.parse_obj(data)
