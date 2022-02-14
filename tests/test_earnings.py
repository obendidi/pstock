import httpx
import pandas as pd

from pstock.earnings import Earnings


def test_earnings(main_quote_response: httpx.Response, snapshot):
    earnings = Earnings.load(response=main_quote_response)
    assert earnings.dict() == snapshot(name="pydantic-model")
    assert isinstance(earnings.df, pd.DataFrame)
    assert earnings.df.to_dict() == snapshot(name="pandas-dataframe")
