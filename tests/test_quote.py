import httpx
import pytest

from pstock.quote import QuoteSummary


@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("TSLA", "https://finance.yahoo.com/quote/TSLA"),
        ("tsla", "https://finance.yahoo.com/quote/TSLA"),
    ],
)
def test_quote_summary_uri(symbol: str, expected: str):
    assert QuoteSummary.uri(symbol) == expected


@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("TSLA", "https://finance.yahoo.com/quote/TSLA/financials?p=TSLA"),
        ("tsla", "https://finance.yahoo.com/quote/TSLA/financials?p=TSLA"),
    ],
)
def test_quote_summary_financials_uri(symbol: str, expected: str):
    assert QuoteSummary.financials_uri(symbol) == expected


def test_quote_summary_parse_quote(quote_response: httpx.Response, snapshot):
    assert QuoteSummary.parse_quote(quote_response) == snapshot


def test_quote_summary_process_quote():
    assert QuoteSummary.process_quote({"some": "data"}) == {}


def test_quote_summary_process_financials_quote():
    assert QuoteSummary.process_financials_quote({"some": "data"}) == {}
