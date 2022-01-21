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
    _AutoValidInterval,
    _get_valid_intervals,
    _user_agent_header,
    _ValidInterval,
    _ValidRange,
    _YFChartParams,
)

__all__ = "get_bars"

logger = logging.getLogger(__name__)

_YF_CHART_URI = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"


class UnprocessableEntity(Exception):
    """Exception for when yahoo-finance returns a status 422.

    It usually means that the interval provided is not valid for provided range or
    start time.
    """

    ...


def _parse_yf_chart_response(
    response: httpx.Response, interval: _ValidInterval
) -> Bars:
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
    interval: _AutoValidInterval = "auto",
    period: tp.Optional[_ValidRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.AsyncClient] = None,
) -> Bars:
    """Get symbol [Bars][pstock.schemas.Bars] from yahoo-finance.

    Each bar contains: datetime (UTC), open, hight, low, close, adj_close and interval

    The generated [Bars][pstock.schemas.Bars] can be viewed as a pd.DataFrame,
    using the property `.df`.

    Either the `period` or `start` time should at least be provided.

    If the provided interval is not valid relative to period or start time,
    an [UnprocessableEntity][pstock.yahoo_finance.bar.UnprocessableEntity] error will
    be raised (as a response from yahoo-finance).

    You can also provide an `interval="auto"` (default), so that pstock can
    automatically infer from your provided `period` or `start` value the minimum
    `interval` usable.

    When interval is set to `auto`, we try a list of valid intervals from lowest
    supported to largest.

    Example:
        >>> from pstock.yahoo_finance import get_bars
        >>>
        >>> bars = await get_bars("MSFT", interval="1h", period="1d")
        >>> print(bars) # will print a pydantic model
        >>> print(bars.df.head()) # will print a pd.DataFrame

    Args:
        symbol (str): ticker for a stock/crypto/ETF availlable in yahoo-finance.
        interval (tp.Literal["auto", "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d",
            "1mo", "3mo"]): Interval to use when getting [Bars][pstock.schemas.Bars].
        period (tp.Optional[tp.Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y",
            "5y", "10y", "ytd", "max"]], optional): Range/Period to use for getting
            market data. Period is relative to `datetime.now()` and open market days.
            Either Use `period` parameter or use `start` and `end`.
        start (tp.Union[None, str, int, float, datetime], optional): Download start
            date, ideally an UTC `datetime` object, but also accepts int/float
            timestamps or str datetime supported by
            [pydantic](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types)
        end (tp.Union[None, str, int, float, datetime], optional): Download end
            date, ideally an UTC `datetime` object, but also accepts int/float
            timestamps or str datetime supported by
            [pydantic](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types).
            If not provided and `start` is provided, defaults to `datetime.utcnow()`
        include_prepost (bool, optional): Include Pre and Post market data in
            [Bars][pstock.schemas.Bars].
        events (tp.Literal["div", "split", "div,splits"], optional): events to include
            with response..
        client (tp.Optional[httpx.AsyncClient], optional): Optional instance of
            [httpx.AsyncClient](python-httpx.org/advanced/#client-instances).

    Raises:
        anyio.ExceptionGroup: group of
            [UnprocessableEntity][pstock.yahoo_finance.bar.UnprocessableEntity] errors.

    Returns:
        [pstock.schemas.Bars][]
    """
    valid_intervals = _get_valid_intervals(interval, period=period, start=start)

    params = _YFChartParams(
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
            url=_YF_CHART_URI.format(symbol=symbol),
            client=client,
            params=params.dict(exclude_none=True, by_alias=True),
            headers=_user_agent_header(),
        )
        try:
            return _parse_yf_chart_response(response, params.interval)
        except UnprocessableEntity as error:
            logger.error(error)
            errors.append(error)
    raise anyio.ExceptionGroup(*errors)


async def get_bars_multi(
    symbols: tp.List[str],
    interval: _AutoValidInterval = "auto",
    period: tp.Optional[_ValidRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.AsyncClient] = None,
) -> BarsMulti:
    """Get [Bars][pstock.schemas.Bars] for multiple symbols from yahoo-finance.

    Works exactly the same as [get_bars][pstock.yahoo_finance.bar.get_bars], but with a
    list of symbols as input.

    This function returns an instance of [BarsMulti][pstock.schemas.BarsMulti], wich is
    simply a mapping `str` -> [Bars][pstock.schemas.Bars].

    Accessings bars for each symbol can be done the same as a Mapping/Dict.

    Example:
        >>> from pstock.yahoo_finance import get_bars_multi
        >>>
        >>> bars = await get_bars_multi(["MSFT", "TSLA", "AAPL"], period="1d")
        >>> print(bars) # will print all bars of all symbols as a pydantic model.
        >>> print(bars["MSFT"]) # will print bars specific to symbol `MSFT`
        >>> print(bars.df.head()) # will print a pd.DataFrame of all symbols
        >>> print(bars["MSFT"].df) # will print only pd.DataFrame for `MSFT` bars.

    Args:
        symbols (tp.List[str]): List fo symbols availlable in yahoo-finance (it is
            possible to mix stock and crypto symbols, but not ideal)
        interval (tp.Literal["auto", "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d",
            "1mo", "3mo"]): Interval to use when getting [Bars][pstock.schemas.Bars].
        period (tp.Optional[tp.Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y",
            "5y", "10y", "ytd", "max"]], optional): Range/Period to use for getting
            market data. Period is relative to `datetime.now()` and open market days.
            Either Use `period` parameter or use `start` and `end`.
        start (tp.Union[None, str, int, float, datetime], optional): Download start
            date, ideally an UTC `datetime` object, but also accepts int/float
            timestamps or str datetime supported by
            [pydantic](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types)
        end (tp.Union[None, str, int, float, datetime], optional): Download end
            date, ideally an UTC `datetime` object, but also accepts int/float
            timestamps or str datetime supported by
            [pydantic](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types).
            If not provided and `start` is provided, defaults to `datetime.utcnow()`
        include_prepost (bool, optional): Include Pre and Post market data in
            [Bars][pstock.schemas.Bars].
        events (tp.Literal["div", "split", "div,splits"], optional): events to include
            with response..
        client (tp.Optional[httpx.AsyncClient], optional): Optional instance of
            [httpx.AsyncClient](python-httpx.org/advanced/#client-instances).

    Returns:
        [pstock.schemas.BarsMulti][]
    """

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
        bars = await get_bars(symbol, period="1d", client=client, interval="1h")
        logger.info(symbol)
        logger.info(bars.df)

    async def _main(symbols):
        async with httpx.AsyncClient() as client:
            async with asyncer.create_task_group() as tg:
                for symbol in symbols:
                    tg.soonify(_worker)(symbol, client=client)

    _symbols = [
        "TSLA",
        "AAPL",
        # "GOOG",
        # "AMZN",
        # "AMD",
        # "GME",
        # "SPCE",
        # "^QQQ",
        # "ETH-USD",
        # "BTC-EUR",
    ]
    # asyncer.runnify(_main)(_symbols)
    multi_bars = asyncer.runnify(get_bars_multi)(_symbols, period="1d", interval="1h")
    logger.info(multi_bars.df)
