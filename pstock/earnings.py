import typing as tp

import numpy as np
import pandas as pd
from pydantic import validator

from pstock.base import BaseModel, BaseModelSequence
from pstock.quote import QuoteSummary
from pstock.utils.quote import get_earnings_data_from_quote


class Earning(BaseModel):
    quarter: str
    estimate: float
    actual: float
    status: tp.Literal[None, "Beat", "Missed"] = None
    revenue: float
    earnings: float

    @validator("status", always=True)
    def set_status(
        cls, value: tp.Any, values: tp.Dict[str, tp.Any]
    ) -> tp.Literal[None, "Beat", "Missed"]:
        if value is not None:
            return value
        estimate = values.get("estimate")
        actual = values.get("actual")
        if actual is None or np.isnan(actual) or estimate is None or np.isnan(estimate):
            return None
        return "Beat" if actual >= estimate else "Missed"


class Earnings(BaseModelSequence[Earning], QuoteSummary):
    __root__: tp.List[Earning]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        if not df.empty:
            df = df.set_index("quarter").sort_index(key=pd.to_datetime)
        return df

    @validator("__root__")
    def sort_earnings(cls, value: tp.List[Earning]) -> tp.List[Earning]:
        if not value:
            return value
        return sorted(value, key=lambda earning: pd.to_datetime(earning.quarter))

    @classmethod
    def process_quote(cls, quote: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Any]:
        return {"__root__": get_earnings_data_from_quote(quote)}
