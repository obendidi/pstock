import logging
import typing as tp
from datetime import datetime

import httpx
import pendulum

from pstock.core.times import parse_datetime, parse_duration
from pstock.schemas.bar import Bar
from pstock.yf.bar import get_bars
from pstock.yf.quote import get_quote_summary

logger = logging.getLogger(__name__)


async def get_latest_price(
    symbol: str,
    include_prepost: bool = True,
    client: tp.Optional[httpx.AsyncClient] = None,
) -> float:
    """Get latest price of symbol from yahoo-finance.

    The price is extracted from yahoo-finance quote-summary

    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        include_prepost (bool, optional): Include pre-post data when getting latest
            price, if False will return only latest regular market price. Defaults to
            True.
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.

    Raises:
        NotImplementedError: If quote_summary is empty or contains no valid price data.

    Returns:
        float: latest price for symbol.
    """

    quote_summary = await get_quote_summary(symbol, client=client)
    price_data = quote_summary.get("price", {})
    if not price_data:
        raise NotImplementedError(
            f"Found no price data (in quote_summary) for symbol {symbol} in "
            "yahoo-finance, maybe try getting prices using "
            "'pstock.yahoo_finance.get_bars'"
        )

    # regular market price
    regular_market_price = price_data["regularMarketPrice"]["raw"]
    # return last regular market price if we don't care about prepost
    if not include_prepost:
        logger.debug(
            f"Getting latest price for symbol '{symbol}' from regular market data."
        )
        return regular_market_price
    regular_market_time = pendulum.from_timestamp(price_data["regularMarketTime"])

    prices = {"regular": (regular_market_time, regular_market_price)}

    # pre-market price
    pre_market_price = (
        price_data.get("preMarketPrice", {}).get("raw")
        if price_data.get("preMarketPrice", {}) is not None
        else None
    )
    if pre_market_price is not None:
        prices["pre"] = (
            pendulum.from_timestamp(price_data["preMarketTime"]),
            pre_market_price,
        )

    # post-market price
    post_market_price = (
        price_data.get("postMarketPrice", {}).get("raw")
        if price_data.get("postMarketPrice", {}) is not None
        else None
    )
    if post_market_price is not None:
        prices["post"] = (
            pendulum.from_timestamp(price_data["postMarketTime"]),
            post_market_price,
        )

    name, (price_date, price) = min(
        prices.items(), key=lambda x: abs(pendulum.now() - x[1][0])
    )

    logger.debug(f"Getting latest price for symbol '{symbol}' from {name} market data.")
    return price


async def get_price_at_timestamp(
    symbol: str,
    timestamp: tp.Union[str, int, float, datetime],
    client: tp.Optional[httpx.AsyncClient] = None,
    warn_inaccurate: bool = True,
) -> float:
    """Get an apprx price of symbol at timestamp.

    The price found is an approx since it's only based on historical bars from
    yahoo-finance. Yahoo-finance restricts intervals based on how old requested data is.


    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        timestamp (tp.Union[str, int, float, datetime]): timestamp to get symbol price
            at, should be a valid datetime that can be parsed using pydantic.
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.
        warn_inaccurate (bool, optional): enable/disable warning for inncurate data when
            interval > 1Min. Defaults to True.

    Returns:
        float: approximate price for symbol at timestamp.
    """

    timestamp = parse_datetime(timestamp)

    # we don't set end value, since interval is auto-set
    # end is always datetime.now()
    bars = await get_bars(
        symbol, client=client, start=timestamp.replace(second=0), include_prepost=True
    )
    # first bar is always the bar we want
    bar: Bar = bars[0]

    # convert it to pendulum.Duration object
    interval = parse_duration(bar.interval)

    # print warning when interval > 1minute
    # 1m is still inaccurate, but still the best we can get
    if interval.total_seconds() > 60 and warn_inaccurate:
        logger.warning(
            f"Price for symbol '{symbol}' at {timestamp} may be inaccurate,"
            f" since the bars used to find price have an interval of {interval}."
        )

    # simple if-else to return open or close price
    bar_open_date = bar.date
    bar_close_date = bar_open_date + interval
    open_delta = timestamp - bar_open_date
    close_delta = bar_close_date - timestamp
    if open_delta < close_delta:
        return bar.open
    return bar.close


if __name__ == "__main__":
    import logging

    import asyncer

    from pstock.core.log import setup_logging

    setup_logging(level="DEBUG")
    logger = logging.getLogger()

    timestamp = pendulum.datetime(2021, 1, 21, hour=16, minute=44, second=30)

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        price = await get_price_at_timestamp(symbol, client=client, timestamp=timestamp)
        logger.info(f"{symbol}: {price}")

    async def _main(symbols):
        async with httpx.AsyncClient() as client:
            async with asyncer.create_task_group() as tg:
                for symbol in symbols:
                    tg.soonify(_worker)(symbol, client=client)

    asyncer.runnify(_main)(
        [
            "TSLA",
            "AAPL",
            "GOOG",
            "AMZN",
            "AMD",
            "GME",
            "SPCE",
            "^QQQ",
            "ETH-USD",
            "BTC-EUR",
        ]
    )
