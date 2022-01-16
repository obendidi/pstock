import typing as tp
from datetime import datetime, timedelta

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
    def df(self):
        if self._df is None:
            super().df
            self._df = self._df.set_index("datetime")
            self._df = self._df.dropna(
                how="all",
                subset=["open", "high", "low", "close", "adj_close", "volume"],
            )
        return self._df


class BarsMulti(BaseDataFrameModel):
    __root__: tp.Dict[str, Bars]
