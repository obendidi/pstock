from pstock.schemas.asset import Asset
import typing as tp

from pstock.isin import get_isin, aget_isin
from pstock.yahoo_finance.quote import aget_quote_summary, get_quote_summary

import httpx
import asyncio


def get_asset(ticker: str, client: tp.Optional[httpx.Client] = None) -> Asset:
    quote = get_quote_summary(ticker, client=client)
    isin = get_isin(ticker, client=client)
    return Asset(ticker=ticker, isin=isin)


async def aget_asset(
    ticker: str, client: tp.Optional[httpx.AsyncClient] = None
) -> Asset:
    quote, isin = await asyncio.gather(
        aget_quote_summary(ticker, client=client), aget_isin(ticker, client=client)
    )
    return Asset(ticker=ticker, isin=isin)
