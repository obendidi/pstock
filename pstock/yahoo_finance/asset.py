import typing as tp

import asyncer
import httpx

from pstock import get_isin
from pstock.schemas.asset import Asset, Assets
from pstock.yahoo_finance.earnings import _parse_earnings_from_quote_summary
from pstock.yahoo_finance.quote import get_quote_summary
from pstock.yahoo_finance.trend import _parse_trends_from_quote_summary

__all__ = "get_asset"


def _parse_asset_from_quote(
    symbol: str, quote_summary: tp.Dict[str, tp.Any], isin: tp.Optional[str] = None
) -> Asset:
    earnings, next_earnings_date = _parse_earnings_from_quote_summary(quote_summary)
    trends = _parse_trends_from_quote_summary(quote_summary)
    quote_profile = quote_summary.get("quoteType", {}) or {}
    summary_profile = quote_summary.get("summaryProfile", {}) or {}
    data = {
        "symbol": symbol,
        **quote_profile,
        **summary_profile,
        "isin": isin,
        "earnings": earnings,
        "trends": trends,
        "next_earnings_date": next_earnings_date,
    }
    return Asset(**data)


async def get_asset(
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
        soon_quote_summary = task_group.soonify(get_quote_summary)(
            symbol, client=client
        )
        soon_isin = task_group.soonify(get_isin)(symbol, client=client)

    return _parse_asset_from_quote(
        symbol, soon_quote_summary.value, isin=soon_isin.value
    )


async def get_assets(
    symbols: tp.List[str], client: tp.Optional[httpx.AsyncClient] = None
) -> Assets:
    close_client = False
    if client is None:
        client = httpx.AsyncClient()
        close_client = True
    try:
        async with asyncer.create_task_group() as tg:
            soon_values = [
                tg.soonify(get_asset)(
                    symbol,
                    client=client,
                )
                for symbol in symbols
            ]
    finally:
        if close_client and client:
            await client.aclose()

    return Assets.parse_obj([soon.value for soon in soon_values])


if __name__ == "__main__":
    import logging

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    assets = asyncer.runnify(get_assets)(
        [
            "TSLA",
            "AAPL",
            "GOOG",
            "AMZN",
            "AMD",
            "GME",
            "SPCE",
        ]
    )
    print(assets.df)
