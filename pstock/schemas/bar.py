import typing as tp
from datetime import datetime, timedelta

import pandas as pd
import pendulum
from pydantic import BaseModel, validator

from pstock.base import BaseDataFrameModel
from pstock.utils.yf.chart import parse_yf_chart_ohlc


class Bar(BaseModel):
    date: datetime
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
            self._df = self._convert_to_df().dropna(
                how="all",
                subset=["open", "high", "low", "close", "adj_close", "volume"],
            )
            if not self._df.empty:
                if self._df["interval"][0] >= timedelta(days=1):
                    self._df["date"] = pd.to_datetime(self._df["date"]).dt.date
                self._df = self._df.set_index("date")
                self._df = self._df.sort_index()
        return self._df

    @classmethod
    def from_yf(
        cls,
        content: tp.Optional[bytes] = None,
        data: tp.Optional[tp.Dict[str, tp.Any]] = None,
    ) -> "Bars":
        return cls.parse_obj(parse_yf_chart_ohlc(content=content, data=data))


class BarsMulti(BaseDataFrameModel):
    __root__: tp.Dict[str, Bars]
