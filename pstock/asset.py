from __future__ import annotations

import typing as tp

import asyncer
import httpx
import numpy as np
import pandas as pd
from pydantic import Field, validator

from pstock.base import BaseModelSequence
from pstock.earnings import Earnings
from pstock.income_statement import IncomeStatements
from pstock.quote import QuoteSummary
from pstock.trend import Trends
from pstock.utils.quote import get_asset_data_from_quote
from pstock.utils.utils import httpx_client_manager


class Asset(QuoteSummary):
    symbol: str
    name: str
    asset_type: tp.Literal[
        "EQUITY", "CURRENCY", "CRYPTOCURRENCY", "ETF", "FUTURE", "INDEX"
    ]
    currency: str
    latest_price: float = np.nan
    sector: tp.Optional[str]
    industry: tp.Optional[str]
    earnings: Earnings = Field(repr=False)
    trends: Trends = Field(repr=False)
    income_statement: tp.Optional[IncomeStatements] = Field(repr=False)

    @validator("symbol")
    def symbol_upper(cls, symbol: str) -> str:
        return symbol.upper()

    @classmethod
    def process_quote(cls, quote: tp.Dict[str, tp.Any]) -> tp.Dict[str, tp.Any]:
        data = get_asset_data_from_quote(quote)
        earnings = Earnings.process_quote(quote)
        trends = Trends.process_quote(quote)
        return {**data, "earnings": earnings, "trends": trends}

    @classmethod
    def process_financials_quote(
        cls, financials_quote: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        income_statement = IncomeStatements.process_financials_quote(financials_quote)
        return {"income_statement": income_statement}


class Assets(BaseModelSequence[Asset]):
    __root__: tp.List[Asset]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        df["earnings"] = df["earnings"].apply(lambda v: None if len(v) == 0 else v)
        df["trends"] = df["trends"].apply(lambda v: None if len(v) == 0 else v)
        return df.set_index("symbol").sort_index().dropna(axis=1, how="all")

    @classmethod
    async def get(
        cls,
        symbols: tp.List[str],
        *,
        client: tp.Optional[httpx.AsyncClient] = None,
    ):
        async with httpx_client_manager(client=client) as _client:
            async with asyncer.create_task_group() as tg:
                soon_values = [
                    tg.soonify(Asset.get)(symbol, client=_client) for symbol in symbols
                ]
        return cls.parse_obj([soon.value for soon in soon_values])
