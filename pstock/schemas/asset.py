import typing as tp

from pydantic import BaseModel, Field


class Asset(BaseModel):
    ticker: str
    name: tp.Optional[str] = Field(repr=False)
    isin: tp.Optional[str] = Field(repr=False)
