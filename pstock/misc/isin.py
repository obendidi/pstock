import typing as tp

import httpx
import pstock


def set_params(symbol: str) -> tp.Dict[str, tp.Any]:
    return {
        "max_results": 25,
        "query": symbol.upper(),
    }


def is_valid_symbol(symbol: str) -> bool:
    if "-" in symbol or "^" in symbol:
        return False
    return True


def process_response(symbol: str, response: httpx.Response) -> tp.Optional[str]:
    response.raise_for_status()
    search_str = f'"{symbol.upper()}|'
    if search_str not in response.text:
        return None
    return response.text.split(search_str)[1].split('"')[0].split("|")[0]


async def get_isin_async(
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
    if not is_valid_symbol(symbol):
        return None
    response = await pstock.get_http_async(
        pstock.config.ISIN_URI,
        client=client,
        params=set_params(symbol),
    )
    return process_response(symbol, response)


def get_isin_sync(
    symbol: str, client: tp.Optional[httpx.Client] = None
) -> tp.Optional[str]:
    """Get ISIN of an US stock symbol from
    [https://markets.businessinsider.com](https://markets.businessinsider.com).

    If the isin is not found, returns None.

    By default yahoo-finance sumbols that contain '^' or '-' are not supported.

    Args:
        symbol (str): symbol or ticker of an existing US market stock
        client (tp.Optional[httpx.Client], optional): Defaults to None.

    Returns:
        tp.Optional[str]: isin of the stock if found else None
    """
    if not is_valid_symbol(symbol):
        return None
    response = pstock.get_http_sync(
        pstock.config.ISIN_URI,
        client=client,
        params=set_params(symbol),
    )
    return process_response(symbol, response)
