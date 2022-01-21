import typing as tp
from datetime import datetime

from pydantic import BaseModel, Field

from pstock.schemas.earnings import Earnings
from pstock.schemas.trend import Trends


class Asset(BaseModel):
    symbol: str
    name: str = Field(..., alias="shortName")
    type: tp.Literal["EQUITY", "ETF", "CRYPTOCURRENCY"] = Field(..., alias="quoteType")
    trends: Trends = Field(repr=False)
    earnings: Earnings = Field(repr=False)
    next_earnings_date: tp.Optional[datetime] = Field(repr=False)
    market: tp.Optional[str] = Field(repr=False)
    sector: tp.Optional[str] = Field(repr=False)
    industry: tp.Optional[str] = Field(repr=False)
    country: tp.Optional[str] = Field(repr=False)
    isin: tp.Optional[str] = Field(repr=False)

    class Config:
        allow_population_by_field_name = True
