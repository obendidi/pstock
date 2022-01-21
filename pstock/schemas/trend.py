import typing as tp
from datetime import date

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from pstock.schemas.base import BaseDataFrameModel, Computed


def _compute_trend_score(
    *, strong_buy: int, buy: int, hold: int, sell: int, strong_sell: int, **kwargs
) -> float:
    numerator = strong_buy + buy * 2 + hold * 3 + sell * 4 + strong_sell * 5
    denominator = strong_buy + buy + hold + sell + strong_sell
    if denominator == 0:
        return np.nan
    return round(numerator / denominator, 2)


def _compute_trend_recomendation(
    *, score: float, **kwargs
) -> tp.Literal["UNKNOWN", "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]:
    if np.isnan(score):
        return "UNKNOWN"
    elif score >= 4.5:
        return "STRONG_SELL"
    elif score >= 3.5:
        return "SELL"
    elif score >= 2.5:
        return "HOLD"
    elif score >= 1.5:
        return "BUY"
    else:
        return "STRONG_BUY"


class Trend(BaseModel):
    date: date
    strong_buy: int = 0
    buy: int = 0
    hold: int = 0
    sell: int = 0
    strong_sell: int = 0
    score: Computed[float] = Field(_compute_trend_score)
    recomendation: Computed[
        tp.Literal["UNKNOWN", "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    ] = Field(_compute_trend_recomendation)


class Trends(BaseDataFrameModel):
    __root__: tp.List[Trend]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(index_column="date", sort_index=True)
        return self._df


if __name__ == "__main__":

    trend = Trend(date=date.today())
    print(trend)
