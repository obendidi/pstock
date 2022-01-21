import json
import typing as tp

import asyncer
import httpx

from pstock import Asset, get_isin
from pstock.yahoo_finance.earnings import _parse_earnings_from_quote_summary
from pstock.yahoo_finance.quote import get_quote_summary
from pstock.yahoo_finance.trend import _parse_trends_from_quote_summary

__all__ = "get_asset"


def _parse_asset_from_quote(
    symbol: str, quote_summary: tp.Dict[str, tp.Any], isin: tp.Optional[str] = None
) -> Asset:
    with open(f"data/{symbol}.json", "w") as f:
        json.dump(quote_summary, f, indent=2)
    earnings, next_earnings_date = _parse_earnings_from_quote_summary(quote_summary)
    trends = _parse_trends_from_quote_summary(quote_summary)
    data = {
        "symbol": symbol,
        **quote_summary.get("quoteType", {}),
        **quote_summary.get("summaryProfile", {}),
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


if __name__ == "__main__":
    import logging

    from pstock.core.log import setup_logging

    setup_logging(level="INFO")
    logger = logging.getLogger()

    async def _worker(symbol: str, client: httpx.AsyncClient) -> None:
        asset = await get_asset(symbol, client=client)
        logger.info(asset)
        logger.info(asset.earnings.df)
        logger.info(asset.trends.df)

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
        ]
    )
