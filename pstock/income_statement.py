import typing as tp
from datetime import date

import pandas as pd

from pstock.base import BaseModel, BaseModelSequence
from pstock.quote import QuoteSummary
from pstock.utils.financials_quote import (
    get_income_statement_data_from_financials_quote,
)


class IncomeStatement(BaseModel):
    date: date
    ebit: float
    total_revenue: float
    gross_profit: float


class BaseIncomeStatements(BaseModelSequence[IncomeStatement], QuoteSummary):
    __root__: tp.List[IncomeStatement]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        if not df.empty:
            df = df.set_index("date").sort_index()
        return df


class IncomeStatements(BaseIncomeStatements):
    @classmethod
    def process_financials_quote(
        cls, financials_quote: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        return {
            "__root__": get_income_statement_data_from_financials_quote(
                financials_quote, key="incomeStatementHistory"
            )
        }

    @property
    def revenue_compound_annual_growth_rate(self) -> float:
        """Revenue CAGR.

        https://www.investopedia.com/terms/c/cagr.asp

        Returns:
            float: Revenue CAGR based
        """
        latest_revenue = self.df.max()["total_revenue"]
        earliest_revenue = self.df.min()["total_revenue"]
        num_years = len(self.df) - 1
        return (latest_revenue / earliest_revenue) ** (1 / num_years) - 1


class QuarterlyIncomeStatements(BaseIncomeStatements):
    @classmethod
    def process_financials_quote(
        cls, financials_quote: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        return {
            "__root__": get_income_statement_data_from_financials_quote(
                financials_quote, key="incomeStatementHistoryQuarterly"
            )
        }

    @property
    def revenue_compound_annual_growth_rate(self) -> float:
        raise NotImplementedError()
