import typing as tp

import httpx

import pstock
from pstock.schemas.news import News


def _set_params(symbol: str) -> tp.Dict[str, tp.Any]:
    return {"s": symbol.upper(), "region": "US", "lang": "en-US"}


async def get_news_async(
    symbol: str, client: tp.Optional[httpx.AsyncClient] = None
) -> News:
    """Get latest news of a particular symbol from yahoo-finance.

    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.

    Returns:
        [pstock.schemas.News][]
    """
    response = await pstock.get_http_async(
        pstock.config.yf.NEWS_RSS_FEED, client=client, params=_set_params(symbol)
    )
    response.raise_for_status()
    return News.from_yf(response.text)


def get_news_sync(symbol: str, client: tp.Optional[httpx.Client] = None) -> News:
    """Get latest news of a particular symbol from yahoo-finance.

    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        client (tp.Optional[httpx.Client], optional): Defaults to None.

    Returns:
        [pstock.schemas.News][]
    """
    response = pstock.get_http_sync(
        pstock.config.yf.NEWS_RSS_FEED, client=client, params=_set_params(symbol)
    )
    response.raise_for_status()
    return News.from_yf(response.text)


if __name__ == "__main__":
    symbols = [
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

    for _symbol in symbols:
        news = get_news_sync(_symbol)
        print(_symbol)
        print(news.df)
