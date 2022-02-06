import typing as tp

import asyncer
import httpx

from pstock.asset import Asset, Assets
from pstock.misc.isin import get_isin_async, get_isin_sync

from .quote import get_yf_quote_summary_content_async, get_yf_quote_summary_content_sync


async def get_asset_async(
    symbol: str, client: tp.Optional[httpx.AsyncClient] = None
) -> Asset:
    """Get [Asset][pstock.schemas.Asset] data from yahoo-finance.

    An [Asset][pstock.schemas.Asset] will at least have it's: symbol, name and type.

    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        client (tp.Optional[httpx.AsyncClient], optional): Defaults to None.

    Returns:
        [pstock.schemas.Asset][]
    """
    async with asyncer.create_task_group() as task_group:
        soon_quote_content = task_group.soonify(get_yf_quote_summary_content_async)(
            symbol, client=client
        )
        soon_isin = task_group.soonify(get_isin_async)(symbol, client=client)

    return Asset.from_yf(content=soon_quote_content.value, isin=soon_isin.value)


async def get_asset_sync(
    symbol: str, client: tp.Optional[httpx.Client] = None
) -> Asset:
    """Get [Asset][pstock.schemas.Asset] data from yahoo-finance.

    An [Asset][pstock.schemas.Asset] will at least have it's: symbol, name and type.

    Args:
        symbol (str): A stock/crypto symbol availlable in yahoo-finance
        client (tp.Optional[httpx.Client], optional): Defaults to None.

    Returns:
        [pstock.schemas.Asset][]
    """
    quote_content = get_yf_quote_summary_content_sync(symbol, client=client)
    isin = get_isin_sync(symbol, client=client)
    return Asset.from_yf(content=quote_content, isin=isin)


async def get_assets_async(
    symbols: tp.List[str], client: tp.Optional[httpx.AsyncClient] = None
) -> Assets:
    close_client = False
    if client is None:
        client = httpx.AsyncClient()
        close_client = True
    try:
        async with asyncer.create_task_group() as tg:
            soon_values = [
                tg.soonify(get_asset_async)(
                    symbol,
                    client=client,
                )
                for symbol in symbols
            ]
    finally:
        if close_client and client:
            await client.aclose()

    return Assets.parse_obj([soon.value for soon in soon_values])
