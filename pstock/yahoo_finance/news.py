import typing as tp
import httpx

from pstock.core import httpx_get
from pstock.yahoo_finance.utils import _user_agent_header
from pstock.schemas import News


_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search?q={symbol}"


async def get_news(symbol: str, client: tp.Optional[httpx.AsyncClient] = None) -> News:
    url = _SEARCH_URL.format(symbol=symbol)

    response = await httpx_get(url, client=client, headers=_user_agent_header())

    response.raise_for_status()
    return News.parse_obj(response.json().get("news", []))


if __name__ == "__main__":
    import logging
    import asyncer

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        news = await get_news(symbol, client=client)
        logger.info(news.df)

    async def _main(symbols):
        async with httpx.AsyncClient() as client:
            async with asyncer.create_task_group() as tg:
                for symbol in symbols:
                    tg.soonify(_worker)(symbol, client=client)

    asyncer.runnify(_main)(
        [
            "TSLA",
            # "AAPL",
            # "GOOG",
            # "AMZN",
            # "AMD",
            # "GME",
            # "SPCE",
        ]
    )
