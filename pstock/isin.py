import typing as tp

import httpx

from pstock.core import httpx_get

_ISIN_URI = "https://markets.businessinsider.com/ajax/SearchController_Suggest"
_MAX_RESULTS = 25

__all__ = "get_isin"


def _is_valid_symbol(symbol: str) -> bool:
    if "-" in symbol or "^" in symbol:
        return False
    return True


def _parse_insin_response(symbol: str, response: httpx.Response) -> tp.Optional[str]:
    response.raise_for_status()
    search_str = f'"{symbol}|'
    if search_str not in response.text:
        return None
    return response.text.split(search_str)[1].split('"')[0].split("|")[0]


async def get_isin(
    symbol: str, client: tp.Optional[httpx.AsyncClient] = None
) -> tp.Optional[str]:
    """Get ISIN of an US stock symbol from
    [https://markets.businessinsider.com](https://markets.businessinsider.com).

    If the isin is not found, returns None.

    By default yahoo-finance sumbols that contain '^' or '-' are not supported.

    Args:
        symbol (str): symbol or ticker of an existing US market stock
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.

    Returns:
        tp.Optional[str]: isin of the stock if found else None
    """
    if not _is_valid_symbol(symbol):
        return None
    response = await httpx_get(
        _ISIN_URI,
        client=client,
        params={
            "max_results": _MAX_RESULTS,
            "query": symbol,
        },
    )
    return _parse_insin_response(symbol, response)


if __name__ == "__main__":
    import logging

    import asyncer

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        isin = await get_isin(symbol, client=client)
        logger.info(f"{symbol}: '{isin}'")

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
