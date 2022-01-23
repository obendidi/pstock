import typing as tp

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from pstock.schemas.base import BaseDataFrameModel, Computed


def _compute_earnings_status(
    *, estimate: float, actual: float, **kwargs
) -> tp.Literal["UNKNOWN", "Beat", "Missed"]:
    if np.isnan(actual):
        return "UNKNOWN"
    elif actual >= estimate:
        return "Beat"
    else:
        return "Missed"


class Earning(BaseModel):
    quarter: str
    estimate: float
    actual: float
    status: Computed[tp.Literal["UNKNOWN", "Beat", "Missed"]] = Field(
        _compute_earnings_status
    )
    revenue: float
    earnings: float


class Earnings(BaseDataFrameModel):
    __root__: tp.List[Earning]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(index_column="quarter")
            self._df = self._df.sort_index(key=pd.to_datetime)
        return self._df
