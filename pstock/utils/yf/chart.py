import json
import logging
import typing as tp
from datetime import datetime, timedelta

import numpy as np

import pstock

logger = logging.getLogger(__name__)


def parse_yf_chart_ohlc(
    *,
    content: tp.Optional[bytes] = None,
    data: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> tp.List[tp.Dict[str, tp.Union[datetime, float, timedelta]]]:
    if content is not None:
        data = json.loads(content)

    if data is None:
        raise ValueError(
            "Please provide either 'content' or 'data' from yahoo-finance chart "
            "response."
        )

    result = data.get("chart", {}).get("result")
    if not result:
        raise ValueError(
            "Got invalid value for result field in yahoo-finance chart "
            f"response: {result}"
        )

    result = result[0]
    meta = result["meta"]

    interval = pstock.parse_duration(meta["dataGranularity"])
    symbol = meta["symbol"]

    # Empty chart
    if "timestamp" not in result:
        logger.warning(
            f"Yahoo-finance returned an empty chart for symbol '{symbol}'. "
            "Please make sure that provided params are valid (for example that "
            "start/end times are valid UTC market times)."
        )
        return []

    timestamps = result["timestamp"]
    indicators = result["indicators"]
    ohlc = indicators["quote"][0]
    volumes = ohlc["volume"]
    opens = ohlc["open"]
    closes = ohlc["close"]
    lows = ohlc["low"]
    highs = ohlc["high"]

    if "adjclose" in indicators:
        adj_closes = indicators["adjclose"][0]["adjclose"]
    else:
        adj_closes = closes

    return [
        {
            "date": timestamp,
            "close": close if close is not None else np.nan,
            "adj_close": adj_close if adj_close is not None else np.nan,
            "high": high if high is not None else np.nan,
            "low": low if low is not None else np.nan,
            "open": open if open is not None else np.nan,
            "volume": volume if volume is not None else np.nan,
            "interval": interval,
        }
        for timestamp, volume, open, close, adj_close, low, high in zip(
            timestamps, volumes, opens, closes, adj_closes, lows, highs
        )
    ]
