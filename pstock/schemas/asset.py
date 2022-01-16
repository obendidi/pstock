import typing as tp

from pydantic import BaseModel, Field

from pstock.schemas.base import BaseDataFrameModel


class Earning(BaseModel):
    date: str
    estimate: float
    actual: tp.Optional[float] = None


class Earnings(BaseDataFrameModel):
    __root__: tp.List[Earning]


class Asset(BaseModel):
    symbol: str
    name: str = Field(..., alias="shortName")
    type: tp.Literal["EQUITY", "ETF", "CRYPTOCURRENCY"] = Field(..., alias="quoteType")
    market: tp.Optional[str] = Field(repr=False)
    sector: tp.Optional[str] = Field(repr=False)
    industry: tp.Optional[str] = Field(repr=False)
    country: tp.Optional[str] = Field(repr=False)
    isin: tp.Optional[str] = Field(repr=False)

    class Config:
        allow_population_by_field_name = True
