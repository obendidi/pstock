import logging
import typing as tp
from datetime import datetime

import anyio
import asyncer
import httpx
import numpy as np

from pstock.core import httpx_get, parse_duration
from pstock.schemas.bar import Bars, BarsMulti
from pstock.yahoo_finance.utils import (
    AutoValidInterval,
    ValidInterval,
    ValidRange,
    YFChartParams,
    get_valid_intervals,
    user_agent_header,
)

__all__ = "get_bars"

logger = logging.getLogger(__name__)

YF_CHART_URI = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"


class UnprocessableEntity(Exception):
    ...


def _parse_yf_chart_response(response: httpx.Response, interval: ValidInterval) -> Bars:
    data = response.json()

    result = data.get("chart", {}).get("result")
    error = data.get("chart", {}).get("error")

    if error:
        raise UnprocessableEntity(error)

    response.raise_for_status()

    timestamps = result[0]["timestamp"]
    indicators = result[0]["indicators"]
    ohlc = indicators["quote"][0]
    volumes = ohlc["volume"]
    opens = ohlc["open"]
    closes = ohlc["close"]
    lows = ohlc["low"]
    highs = ohlc["high"]

    if "adjclose" in indicators:
        adj_closes = indicators["adjclose"][0]["adjclose"]
    else:
        adj_closes = closes

    return Bars.parse_obj(
        [
            {
                "datetime": timestamp,
                "close": close if close is not None else np.nan,
                "adj_close": adj_close if adj_close is not None else np.nan,
                "high": high if high is not None else np.nan,
                "low": low if low is not None else np.nan,
                "open": open if open is not None else np.nan,
                "volume": volume if volume is not None else np.nan,
                "interval": parse_duration(interval),
            }
            for timestamp, volume, open, close, adj_close, low, high in zip(
                timestamps, volumes, opens, closes, adj_closes, lows, highs
            )
        ]
    )


async def get_bars(
    symbol: str,
    interval: AutoValidInterval = "auto",
    period: tp.Optional[ValidRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.AsyncClient] = None,
) -> Bars:
    valid_intervals = get_valid_intervals(interval, period=period, start=start)

    params = YFChartParams(
        interval=valid_intervals[0],
        period=period,
        start=start,
        end=end,
        include_prepost=include_prepost,
        events=events,
    )
    if interval == "auto":
        logger.debug(
            f"[{symbol}] Updating interval from '{interval}' to "
            f"'{params.interval}'."
        )
    errors: tp.List[BaseException] = []
    for valid_interval in valid_intervals:
        if valid_interval != params.interval:
            logger.debug(
                f"[{symbol}] Updating interval from '{params.interval}' to "
                f"'{valid_interval}'."
            )
        params.interval = valid_interval
        response = await httpx_get(
            url=YF_CHART_URI.format(symbol=symbol),
            client=client,
            params=params.dict(exclude_none=True, by_alias=True),
            headers=user_agent_header(),
        )
        try:
            return _parse_yf_chart_response(response, params.interval)
        except UnprocessableEntity as error:
            logger.error(error)
            errors.append(error)
    raise anyio.ExceptionGroup(*errors)


async def get_bars_multi(
    symbols: tp.List[str],
    interval: AutoValidInterval = "auto",
    period: tp.Optional[ValidRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.AsyncClient] = None,
) -> BarsMulti:
    close_client = False
    if client is None:
        client = httpx.AsyncClient()
        close_client = True

    async with asyncer.create_task_group() as tg:
        soon_values = [
            tg.soonify(get_bars)(
                symbol,
                interval=interval,
                period=period,
                start=start,
                end=end,
                include_prepost=include_prepost,
                events=events,
                client=client,
            )
            for symbol in symbols
        ]

    if close_client:
        await client.aclose()

    data = {
        symbol: soon_value.value for symbol, soon_value in zip(symbols, soon_values)
    }
    return BarsMulti.parse_obj(data)


if __name__ == "__main__":
    import logging

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        bars = await get_bars(symbol, period="1d", client=client)
        logger.info(symbol)
        logger.info(bars.df)

    async def _main(symbols):
        async with httpx.AsyncClient() as client:
            async with asyncer.create_task_group() as tg:
                for symbol in symbols:
                    tg.soonify(_worker)(symbol, client=client)

    _symbols = [
        # "TSLA",
        # "AAPL",
        # "GOOG",
        # "AMZN",
        # "AMD",
        # "GME",
        # "SPCE",
        # "^QQQ",
        "ETH-USD",
        "BTC-EUR",
    ]
    # asyncer.runnify(_main)(_symbols)
    multi_bars = asyncer.runnify(get_bars_multi)(_symbols, period="1d", interval="15m")
    logger.info(multi_bars.df)
