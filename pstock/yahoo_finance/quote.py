import json
import typing as tp

import httpx

from pstock.core import httpx_get
from pstock.yahoo_finance.utils import _user_agent_header

__all__ = "get_quote_summary"


_YF_QUOTE_URI = "https://finance.yahoo.com/quote/{symbol}"


def _parse_quote_summary_response(
    symbol: str, response: httpx.Response
) -> tp.Dict[str, tp.Any]:
    if response.status_code == 302:
        logger.error(
            f"symbol '{symbol}' not found in yahoo-finance, it may be "
            "delisted or renamed."
        )
        return {}
    response.raise_for_status()
    data = json.loads(
        response.text.split("root.App.main =")[1]
        .split("(this)")[0]
        .split(";\n}")[0]
        .strip()
        .replace("{}", "null")
    )
    return (
        data.get("context", {})
        .get("dispatcher", {})
        .get("stores", {})
        .get("QuoteSummaryStore")
    )


async def get_quote_summary(
    symbol: str, client: tp.Optional[httpx.AsyncClient] = None
) -> tp.Dict[str, tp.Any]:
    """Get symbol quote summary from yahoo-finance.

    Returns a dictionnary with alla data that we can possibly get fromt yahoo-finance
    about a symbol.

    The schemas of dictionnary differs based on wether the symbol is a stock, ETF or
    crypto.

    The result of this function is used to parse [Assets][pstock.schemas.Asset] and
    [Earnings][pstock.schemas.Earnings], among others ...

    Args:
        symbol (str): Symbol or ticker in yahoo-finance, ex: TSLA, ETH-USD, ^QQQ, ...
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.

    Returns:
        Parsed quote dict.
    """

    url = _YF_QUOTE_URI.format(symbol=symbol)

    response = await httpx_get(
        url, client=client, headers=_user_agent_header(), retry_status_codes=[502]
    )

    return _parse_quote_summary_response(symbol, response)


if __name__ == "__main__":
    import logging

    import asyncer

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        quote = await get_quote_summary(symbol, client=client)
        logger.info(f"{symbol}: '{quote}'")

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
