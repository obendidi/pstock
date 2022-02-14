import datetime
import typing as tp

import numpy as np
import pandas as pd
from pydantic import validator

from pstock.base import BaseModel, BaseModelSequence
from pstock.quote import QuoteSummary
from pstock.utils.quote import get_trends_data_from_quote


class Trend(BaseModel):
    date: datetime.date
    strong_buy: int = 0
    buy: int = 0
    hold: int = 0
    sell: int = 0
    strong_sell: int = 0
    score: tp.Optional[float] = None
    recomendation: tp.Literal[
        None, "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"
    ] = None

    @validator("score", always=True)
    def compute_score(
        cls, value: tp.Optional[float], values: tp.Dict[str, tp.Any]
    ) -> float:
        if value is not None:
            return value
        numerator = (
            values["strong_buy"]
            + values["buy"] * 2
            + values["hold"] * 3
            + values["sell"] * 4
            + values["strong_sell"] * 5
        )
        denominator = (
            values["strong_buy"]
            + values["buy"]
            + values["hold"]
            + values["sell"]
            + values["strong_sell"]
        )
        if denominator == 0:
            return np.nan
        return round(numerator / denominator, 2)

    @validator("recomendation", always=True)
    def compute_recomendation(
        cls, value: tp.Optional[float], values: tp.Dict[str, tp.Any]
    ):
        if value is not None:
            return value
        score = values["score"]
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


class Trends(BaseModelSequence[Trend], QuoteSummary):
    __root__: tp.List[Trend]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        if not df.empty:
            df = df.set_index("date").sort_index()
        return df

    @validator("__root__")
    def sort_trends(cls, value: tp.List[Trend]) -> tp.List[Trend]:
        if not value:
            return value
        return sorted(value, key=lambda trend: pd.to_datetime(trend.date))

    @classmethod
    def process_quote(cls, quote: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Any]:
        return {"__root__": get_trends_data_from_quote(quote)}
