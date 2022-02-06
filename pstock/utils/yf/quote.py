import json
import typing as tp
from datetime import date

import numpy as np
import pendulum


def parse_yf_quote_summary_response(
    content: tp.Union[str, bytes]
) -> tp.Dict[str, tp.Any]:
    """Parse a yahoo-finance quote summary response text.

    Takes the raw text of teh response returned by yahoo-finance and returns a dict
    of the QuoteSuammryStore.

    Args:
        content (str | bytes): httpx.Response().text (or equivalent in other http libs)

    Returns:
        tp.Dict[str, tp.Any]
    """
    if isinstance(content, bytes):
        content = content.decode()
    data = json.loads(
        content.split("root.App.main =")[1]
        .split("(this)")[0]
        .split(";\n}")[0]
        .strip()
        .replace("{}", "null")
    )
    return (
        data.get("context", {})
        .get("dispatcher", {})
        .get("stores", {})
        .get("QuoteSummaryStore", {})
    )


def get_yf_quote_summary_earnings(
    *,
    content: tp.Optional[tp.Union[str, bytes]] = None,
    quote_summary: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> tp.List[tp.Dict[str, tp.Union[str, float]]]:
    """Get earnings list from a properly parsed yahoo-finance quote summary.
    Args:
        quote_summary (tp.Dict[str, tp.Any]): parsed yahoo-finance quote summary using
        [pstock.utils.yf.quote.parse_yf_quote_summary_response][]

    Returns:
        tp.List[tp.Dict[str, tp.Union[str, float]]]: Each element of the list
        constitutes earnings for a quarter
    """
    if content is not None:
        quote_summary = parse_yf_quote_summary_response(content)

    if quote_summary is None:
        raise ValueError(
            "Please provide either 'content' or 'quote_summary' from yahoo-finance "
            "quote response."
        )
    earnings = quote_summary.get("earnings")
    if not earnings or not isinstance(earnings, dict):
        return []

    earnings_chart = earnings.get("earningsChart", {})
    quarterly_earnings = earnings_chart.get("quarterly", [])
    quarterly_financial_chart = earnings.get("financialsChart", {}).get("quarterly", [])

    date_to_earnings = {
        e.get("date", ""): {
            "actual": e.get("actual", {}).get("raw", np.nan),
            "estimate": e.get("estimate", {}).get("raw", np.nan),
        }
        for e in quarterly_earnings
        if "date" in e
    }
    date_to_fin_chart = {
        c.get("date", ""): {
            "revenue": c.get("revenue", {}).get("raw", np.nan),
            "earnings": c.get("earnings", {}).get("raw", np.nan),
        }
        for c in quarterly_financial_chart
        if "date" in c
    }
    all_dates = set(list(date_to_earnings.keys()) + list(date_to_fin_chart.keys()))
    passed_earnings = [
        dict(
            quarter=quarter,
            actual=date_to_earnings.get(quarter, {}).get("actual", np.nan),
            estimate=date_to_earnings.get(quarter, {}).get("estimate", np.nan),
            revenue=date_to_fin_chart.get(quarter, {}).get("revenue", np.nan),
            earnings=date_to_fin_chart.get(quarter, {}).get("earnings", np.nan),
        )
        for quarter in all_dates
    ]

    next_earnings = [
        dict(
            quarter=(
                f"{earnings_chart.get('currentQuarterEstimateDate', '')}"
                f"{earnings_chart.get('currentQuarterEstimateYear', '')}"
            ),
            estimate=earnings_chart.get("currentQuarterEstimate", {}).get(
                "raw", np.nan
            ),
            actual=np.nan,
            revenue=np.nan,
            earnings=np.nan,
        )
    ]
    return passed_earnings + next_earnings


def get_yf_quote_summary_trend(
    *,
    content: tp.Optional[tp.Union[str, bytes]] = None,
    quote_summary: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> tp.List[tp.Dict[str, tp.Any]]:
    if content is not None:
        quote_summary = parse_yf_quote_summary_response(content)

    if quote_summary is None:
        raise ValueError(
            "Please provide either 'content' or 'quote_summary' from yahoo-finance "
            "quote response."
        )
    recommendation_trend = quote_summary.get("recommendationTrend", {})
    if not recommendation_trend:
        return []
    trends = recommendation_trend.get("trend", [])
    return [
        {
            "date": date.today() + pendulum.duration(months=int(trend["period"][:-1])),
            "strong_buy": trend.get("strongBuy", 0),
            "buy": trend.get("buy", 0),
            "hold": trend.get("hold", 0),
            "sell": trend.get("sell", 0),
            "strong_sell": trend.get("stronSell", 0),
        }
        for trend in trends
    ]


def get_yf_quote_summary_asset(
    content: tp.Optional[tp.Union[str, bytes]] = None,
    quote_summary: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> tp.Dict[str, tp.Any]:
    if content is not None:
        quote_summary = parse_yf_quote_summary_response(content)

    if quote_summary is None:
        raise ValueError(
            "Please provide either 'content' or 'quote_summary' from yahoo-finance "
            "quote response."
        )
    earnings = get_yf_quote_summary_earnings(quote_summary=quote_summary)
    trends = get_yf_quote_summary_trend(quote_summary=quote_summary)
    quote_profile = quote_summary.get("quoteType", {}) or {}
    summary_profile = quote_summary.get("summaryProfile", {}) or {}
    return {
        **quote_profile,
        **summary_profile,
        "earnings": earnings,
        "trends": trends,
    }
