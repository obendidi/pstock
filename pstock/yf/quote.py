import logging
import typing as tp
from urllib.parse import urljoin

import anyio
import httpx
from tenacity import (
    TryAgain,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    wait_exponential,
    wait_random,
)

import pstock

from .exceptions import YFSymbolNotFound
from .utils import random_user_agent

logger = logging.getLogger(__name__)


def _compose_uri(symbol: str) -> str:
    return urljoin(pstock.config.yf.QUOTE_URI, symbol.upper())


def _process_response(symbol: str, response: httpx.Response) -> str:
    if response.status_code in pstock.config.yf.QUOTE_NOT_FOUND_STATUS_CODES:
        raise YFSymbolNotFound(symbol)

    if response.status_code in pstock.config.yf.QUOTE_RETRY_STATUS_CODES:
        raise TryAgain(f"{response}, symbol '{symbol}'")
    response.raise_for_status()
    return response.text


@retry(
    reraise=True,
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=4, max=10) + wait_random(0, 2),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def get_yf_quote_summary_content_sync(
    symbol: str, client: tp.Optional[httpx.Client] = None
) -> str:
    """Get raw quote summary content from yahoo-finance.

    If symbol does not exist in yahoo-finance, raise SymbolNotFound.

    This function returns the raw response from yahoo-finance as a string.

    Args:
        symbol (str): Symbol to get from yahoo-finance
        client (tp.Optional[httpx.Client], optional): Defaults to None.

    Returns:
        str: Raw yahoo-finance response content
    """
    response = pstock.get_http_sync(
        _compose_uri(symbol),
        client=client,
        headers={"User-Agent": random_user_agent()},
    )
    return _process_response(symbol, response)


@retry(
    reraise=True,
    sleep=anyio.sleep,
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=4, max=10) + wait_random(0, 2),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def get_yf_quote_summary_content_async(
    symbol: str, client: tp.Optional[httpx.AsyncClient] = None
) -> str:
    """Get raw quote summary content from yahoo-finance.

    If symbol does not exist in yahoo-finance, raise SymbolNotFound.

    This function returns the raw response from yahoo-finance as a string.

    Args:
        symbol (str): Symbol to get from yahoo-finance
        client (tp.Optional[httpx.Client], optional): Defaults to None.

    Returns:
        str: Raw yahoo-finance response content
    """
    response = await pstock.get_http_async(
        _compose_uri(symbol),
        client=client,
        headers={"User-Agent": random_user_agent()},
    )
    return _process_response(symbol, response)
