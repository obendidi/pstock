import json
import re
import typing as tp

from bs4 import BeautifulSoup

from pstock.base import BaseModel
from pstock.types import ReadableResponse

T = tp.TypeVar("T", bound="QuoteSummary")


class QuoteSummary(BaseModel):
    @staticmethod
    def uri(symbol: str) -> str:
        return f"https://finance.yahoo.com/quote/{symbol.upper()}"

    @staticmethod
    def financials_uri(symbol: str) -> str:
        return (
            f"https://finance.yahoo.com/quote/{symbol.upper()}/"
            f"financials?p={symbol.upper()}"
        )

    @staticmethod
    def parse_quote(
        response: tp.Union[ReadableResponse, str, bytes]
    ) -> tp.Dict[str, tp.Any]:

        content = response if isinstance(response, (str, bytes)) else response.read()

        soup = BeautifulSoup(content, "html.parser")

        script = soup.find("script", text=re.compile(r"root.App.main"))
        if script is None:
            return {}
        match = re.search(r"root.App.main\s+=\s+(\{.*\})", script.text)

        if match is None:
            return {}

        data: tp.Dict[str, tp.Any] = json.loads(match.group(1))
        return (
            data.get("context", {})
            .get("dispatcher", {})
            .get("stores", {})
            .get("QuoteSummaryStore", {})
        )

    @classmethod
    def process_quote(
        cls: tp.Type[T], quote: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        return {}

    @classmethod
    def process_financials_quote(
        cls: tp.Type[T], financials_quote: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        return {}

    @classmethod
    def load(
        cls: tp.Type[T],
        *,
        response: tp.Union[ReadableResponse, str, bytes, None] = None,
        financials_response: tp.Union[ReadableResponse, str, bytes, None] = None,
    ) -> T:

        data = {}
        _quote = None
        _financials_quote = None

        if response is not None:
            _quote = cls.parse_quote(response)
            if _quote:
                data.update(cls.process_quote(_quote))

        if financials_response is not None:
            _financials_quote = cls.parse_quote(financials_response)
            if _financials_quote:
                data.update(cls.process_financials_quote(_financials_quote))

        return cls(**data)
