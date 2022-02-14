import typing as tp
from datetime import date

import numpy as np
import pendulum


def get_latest_price_from_quote(price_data: tp.Dict[str, tp.Any]) -> float:
    if not price_data:
        raise ValueError("No price data found.")

    # regular market price
    regular_market_price = price_data["regularMarketPrice"]["raw"]
    regular_market_time = pendulum.from_timestamp(price_data["regularMarketTime"])

    prices = {"regular": (regular_market_time, regular_market_price)}

    # pre-market price
    pre_market_price = (
        price_data.get("preMarketPrice", {}).get("raw")
        if price_data.get("preMarketPrice", {}) is not None
        else None
    )
    if pre_market_price is not None:
        prices["pre"] = (
            pendulum.from_timestamp(price_data["preMarketTime"]),
            pre_market_price,
        )

    # post-market price
    post_market_price = (
        price_data.get("postMarketPrice", {}).get("raw")
        if price_data.get("postMarketPrice", {}) is not None
        else None
    )
    if post_market_price is not None:
        prices["post"] = (
            pendulum.from_timestamp(price_data["postMarketTime"]),
            post_market_price,
        )

    _, (_, price) = min(prices.items(), key=lambda x: abs(pendulum.now() - x[1][0]))

    return price


def get_asset_data_from_quote(quote: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Any]:
    profile = quote.get("summaryProfile", {}) or {}
    quote_type = quote.get("quoteType", {}) or {}
    price_data = quote.get("price", {}) or {}

    symbol = quote.get("symbol") or quote_type.get("symbol") or price_data.get("symbol")
    name = quote_type.get("longName", price_data.get("longName")) or quote_type.get(
        "shortName", price_data.get("shortName")
    )
    asset_type = quote_type.get("quoteType") or price_data.get("quoteType")
    currency = price_data.get("currency")
    latest_price = get_latest_price_from_quote(price_data)
    sector = profile.get("sector")
    industry = profile.get("industry")

    return {
        "symbol": symbol,
        "name": name,
        "asset_type": asset_type,
        "currency": currency,
        "latest_price": latest_price,
        "sector": sector,
        "industry": industry,
    }


def get_earnings_data_from_quote(
    quote: tp.Dict[str, tp.Any]
) -> tp.List[tp.Dict[str, tp.Union[str, float]]]:

    earnings = quote.get("earnings")
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


def get_trends_data_from_quote(
    quote: tp.Dict[str, tp.Any]
) -> tp.List[tp.Dict[str, tp.Any]]:

    if not quote:
        return []
    recommendation_trend = quote.get("recommendationTrend", {})
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
