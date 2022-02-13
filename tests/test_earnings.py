import httpx
from pstock.earnings import Earnings
import pandas as pd


def test_earnings(main_quote_response: httpx.Response, snapshot):
    earnings = Earnings.load(quote_response=main_quote_response)
    assert earnings.dict() == snapshot(name="pydantic-model")
    assert isinstance(earnings.df, pd.DataFrame)
    assert earnings.df.to_dict() == snapshot(name="pandas-dataframe")
