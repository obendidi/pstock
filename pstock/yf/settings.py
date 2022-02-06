import typing as tp

from pydantic import BaseSettings, HttpUrl

YFInterval = tp.Literal["1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"]
YFRange = tp.Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]


class YFConfig(BaseSettings):
    # URI for getting information about an Asset
    QUOTE_URI: HttpUrl = HttpUrl.build(
        scheme="https", host="finance.yahoo.com", path="/quote/"
    )
    QUOTE_RETRY_STATUS_CODES: tp.List[int] = [502]
    QUOTE_NOT_FOUND_STATUS_CODES: tp.List[int] = [404, 302]

    # RSS feed for news
    NEWS_RSS_FEED = HttpUrl.build(
        scheme="https", host="feeds.finance.yahoo.com", path="/rss/2.0/headline"
    )

    # URI for getting chart and bars data
    CHART_URI: HttpUrl = HttpUrl.build(
        scheme="https", host="query2.finance.yahoo.com", path="/v8/finance/chart/"
    )
    CHART_INTERVALS: tp.Tuple[YFInterval, ...] = tp.get_args(YFInterval)
    CHART_RANGES: tp.Tuple[YFRange, ...] = tp.get_args(YFRange)
    CHART_INTERVALS_MAPPING: tp.Dict[str, tp.Tuple[YFInterval, ...]] = {
        "7d": ("1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"),
        "60d": ("2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"),
        "730d": ("1h", "1d", "5d", "1mo", "3mo"),
    }
    CHART_INTERVALS_MAPPING_DEFAULT: tp.Tuple[YFInterval, ...] = (
        "1d",
        "5d",
        "1mo",
        "3mo",
    )
    CHART_INTERVALS_MAPPING_MAX: tp.Tuple[YFInterval, ...] = ("3mo",)

    class Config:
        case_sensitive = True
        env_prefix = "PSTOCK_YF_"


if __name__ == "__main__":
    config = YFConfig()
    print(config.json(indent=2))
