import typing as tp
from datetime import datetime, timedelta

import pandas as pd
from pydantic import BaseModel

from pstock.schemas.base import BaseDataFrameModel


class Bar(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float
    interval: timedelta


class Bars(BaseDataFrameModel):
    __root__: tp.List[Bar]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(
                index_column="datetime", sort_index=True
            ).dropna(
                how="all",
                subset=["open", "high", "low", "close", "adj_close", "volume"],
            )
        return self._df


class BarsMulti(BaseDataFrameModel):
    __root__: tp.Dict[str, Bars]
