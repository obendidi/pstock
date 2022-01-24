import typing as tp
from datetime import datetime

import pandas as pd
from pydantic import BaseModel, Field

from pstock.schemas.base import BaseDataFrameModel
from pstock.schemas.earnings import Earnings
from pstock.schemas.trend import Trends


class Asset(BaseModel, allow_population_by_field_name=True):
    symbol: str
    name: str = Field(..., alias="shortName")
    type: tp.Literal["EQUITY", "ETF", "CRYPTOCURRENCY"] = Field(..., alias="quoteType")
    trends: tp.Optional[Trends] = Field(repr=False)
    earnings: tp.Optional[Earnings] = Field(repr=False)
    next_earnings_date: tp.Optional[datetime] = Field(repr=False)
    market: tp.Optional[str] = Field(repr=False)
    sector: tp.Optional[str] = Field(repr=False)
    industry: tp.Optional[str] = Field(repr=False)
    country: tp.Optional[str] = Field(repr=False)
    isin: tp.Optional[str] = Field(repr=False)


class Assets(BaseDataFrameModel):
    __root__: tp.List[Asset]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(
                index_column="symbol", sort_index=True
            ).dropna(axis=1, how="all")
        return self._df
