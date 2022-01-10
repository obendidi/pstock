import typing as tp
import random

YF_CHART_URI = "https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
YF_QUOTE_URI = "https://finance.yahoo.com/quote/{ticker}"

ValidInterval = tp.Literal[
    "1m", "2m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo"
]
ValidRange = tp.Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd"]

USER_AGENT_LIST: tp.List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  # noqa
]


def user_agent_header() -> tp.Dict[str, str]:
    return {"User-Agent": random.choice(USER_AGENT_LIST)}
