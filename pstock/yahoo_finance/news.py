import time
import typing as tp

import feedparser
import httpx

from pstock.core import httpx_get
from pstock.schemas import News

_RSS_URL = (
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
)


async def get_news(symbol: str, client: tp.Optional[httpx.AsyncClient] = None) -> News:
    """Get latest news of a particular symbol from yahoo-finance.

    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.

    Returns:
        [pstock.schemas.News][]
    """
    url = _RSS_URL.format(symbol=symbol)
    response = await httpx_get(url, client=client)
    response.raise_for_status()
    feed = feedparser.parse(response.text)
    return News.parse_obj(
        [
            {**entry, "date": time.mktime(entry["published_parsed"])}
            for entry in feed.entries
        ]
    )


if __name__ == "__main__":
    import logging

    import asyncer

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        news = await get_news(symbol, client=client)
        logger.info(symbol)
        logger.info(news.df)

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
