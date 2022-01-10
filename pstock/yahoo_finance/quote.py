import typing as tp

import httpx
import json
import logging
from pstock.core import httpx_get, httpx_aget

from pstock.yahoo_finance.config import YF_QUOTE_URI, user_agent_header

__all__ = ("get_quote_summary", "aget_quote_summary")

logger = logging.getLogger(__name__)


def _parse_quote_summary_response(
    ticker: str, response: httpx.Response
) -> tp.Dict[str, tp.Any]:
    if response.status_code == 302:
        logger.error(
            f"Ticker '{ticker}' not found in yahoo-finance, it may be "
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


def get_quote_summary(
    ticker: str, client: tp.Optional[httpx.Client] = None
) -> tp.Dict[str, tp.Any]:

    url = YF_QUOTE_URI.format(ticker=ticker)

    response = httpx_get(
        url, client=client, headers=user_agent_header(), retry_status_codes=[502]
    )
    return _parse_quote_summary_response(ticker, response)


async def aget_quote_summary(
    ticker: str, client: tp.Optional[httpx.AsyncClient] = None
) -> tp.Dict[str, tp.Any]:

    url = YF_QUOTE_URI.format(ticker=ticker)

    response = await httpx_aget(
        url, client=client, headers=user_agent_header(), retry_status_codes=[502]
    )

    return _parse_quote_summary_response(ticker, response)


if __name__ == "__main__":
    tickers = ["TSLA", "AAPL", "GM", "GOOG", "FB", "AMZN", "AMD", "NVDA", "GME", "SPCE"]
    for ticker in tickers:
        summary = get_quote_summary(ticker)
        with open(f"{ticker}.json", "w") as f:
            json.dump(summary, f, indent=2)
