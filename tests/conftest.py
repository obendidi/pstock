import pickle
import pytest
import pendulum
from pathlib import Path
from httpx import Response
from pytest_cases import case, fixture, parametrize_with_cases


@pytest.fixture
def pendulum_now():
    now = pendulum.now()
    pendulum.set_test_now(now)
    yield now
    pendulum.set_test_now()


class QuoteResponseCases:
    def _load_response(self, filename: str) -> Response:
        with open(Path(__file__).parent / "data" / filename, "rb") as f:
            return pickle.load(f)

    @case(tags=["quote"])
    def case_cryptocurrency_quote(self) -> Response:
        return self._load_response("CRYPTOCURRENCY-quote.obj")

    @case(tags=["financials"])
    def case_cryptocurrency_financials(self) -> Response:
        return self._load_response("CRYPTOCURRENCY-financials.obj")

    @case(tags=["quote"])
    def case_currency_quote(self) -> Response:
        return self._load_response("CURRENCY-quote.obj")

    @case(tags=["financials"])
    def case_currency_financials(self) -> Response:
        return self._load_response("CURRENCY-financials.obj")

    @case(tags=["quote"])
    def case_equity_quote(self) -> Response:
        return self._load_response("EQUITY-quote.obj")

    @case(tags=["financials"])
    def case_equity_financials(self) -> Response:
        return self._load_response("EQUITY-financials.obj")

    @case(tags=["quote"])
    def case_etf_quote(self) -> Response:
        return self._load_response("ETF-quote.obj")

    @case(tags=["financials"])
    def case_etf_financials(self) -> Response:
        return self._load_response("ETF-financials.obj")

    @case(tags=["quote"])
    def case_future_quote(self) -> Response:
        return self._load_response("FUTURE-quote.obj")

    @case(tags=["financials"])
    def case_future_financials(self) -> Response:
        return self._load_response("FUTURE-financials.obj")

    @case(tags=["quote"])
    def case_index_quote(self) -> Response:
        return self._load_response("INDEX-quote.obj")

    @case(tags=["financials"])
    def case_index_financials(self) -> Response:
        return self._load_response("INDEX-financials.obj")


@fixture(scope="session")
@parametrize_with_cases("response", cases=QuoteResponseCases)
def quote_response(response: Response) -> Response:
    return response


@fixture(scope="session")
@parametrize_with_cases("response", cases=QuoteResponseCases, has_tag="quote")
def main_quote_response(response: Response) -> Response:
    return response
