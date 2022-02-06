from __future__ import annotations

import typing as tp

import pandas as pd
import numpy as np
from pydantic import Field, validator

from pstock.base import BaseModelSequence
from pstock.quote import QuoteSummary
from pstock.yahoo_finance.quote import get_asset_data_from_quote
from pstock.income_statement import IncomeStatements
from pstock.earnings import Earnings


class Asset(QuoteSummary):
    symbol: str = Field(..., repr=True)
    name: str = Field(..., repr=False)
    asset_type: str = Field(..., repr=False)
    currency: str = Field(..., repr=False)
    latest_price: tp.Optional[float] = Field(default=np.nan, repr=False)
    sector: tp.Optional[str] = Field(repr=False)
    industry: tp.Optional[str] = Field(repr=False)
    income_statement: tp.Optional[IncomeStatements] = Field(repr=False)
    earnings: tp.Optional[Earnings] = Field(repr=False)

    @validator("symbol")
    def symbol_upper(cls, symbol: str) -> str:
        return symbol.upper()

    @classmethod
    def process_quote(cls, quote: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Any]:
        data = get_asset_data_from_quote(quote)
        earnings = Earnings.process_quote(quote)
        return {**data, "earnings": earnings}

    @classmethod
    def process_financials_quote(
        cls, financials_quote: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        return {
            "income_statement": IncomeStatements.process_financials_quote(
                financials_quote
            )
        }


class Assets(BaseModelSequence[Asset]):
    __root__: tp.List[Asset]

    def _gen_df(self) -> pd.DataFrame:
        df = super()._gen_df()
        return df.set_index("symbol").sort_index().dropna(axis=1, how="all")
