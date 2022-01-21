import typing as tp

import pandas as pd
from pydantic import BaseModel

from pstock.schemas.base import BaseDataFrameModel


class Earning(BaseModel):
    quarter: str
    estimate: float
    actual: float
    revenue: float
    earnings: float


class Earnings(BaseDataFrameModel):
    __root__: tp.List[Earning]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(index_column="quarter")
        return self._df
