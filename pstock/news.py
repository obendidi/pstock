from __future__ import annotations

import datetime
import time
import typing as tp
from urllib.parse import urlencode

import feedparser
import httpx
import pandas as pd

from pstock.base import BaseModel, BaseModelSequence
from pstock.types import ReadableResponse
from pstock.utils.utils import httpx_client_manager


class Publication(BaseModel):
    date: datetime.datetime
    title: str
    url: str
    summary: tp.Optional[str]


class News(BaseModelSequence):
    __root__: tp.List[Publication]

    def gen_df(self) -> pd.DataFrame:
        df = super().gen_df()
        if not df.empty:
            df = df.set_index("date").sort_index()
        return df

    @staticmethod
    def base_uri() -> str:
        return "https://feeds.finance.yahoo.com/rss/2.0/headline"

    @staticmethod
    def params(symbol: str) -> tp.Dict[str, str]:
        return {"s": symbol.upper(), "region": "US", "lang": "en-US"}

    @classmethod
    def uri(cls, symbol: str) -> str:
        return f"{cls.base_uri()}?{urlencode(cls.params(symbol))}"

    @classmethod
    def load(
        cls,
        *,
        symbol: tp.Optional[str] = None,
        response: tp.Union[None, str, bytes, ReadableResponse] = None,
    ) -> News:
        if symbol is not None and response is None:
            # feedparser can take a uri as input, and get data over http
            response = cls.uri(symbol)
            print(response)

        if response is None:
            raise ValueError(
                "Please provide either a symbol or or a readeable response."
            )

        feed = feedparser.parse(response)
        return cls.parse_obj(
            [
                {
                    **entry,
                    "date": time.mktime(entry["published_parsed"]),
                    "url": entry["link"],
                }
                for entry in feed.entries
            ]
        )

    @classmethod
    async def get(
        cls,
        symbol: str,
        *,
        client: tp.Optional[httpx.AsyncClient] = None,
    ) -> News:
        async with httpx_client_manager(client=client) as _client:
            response = await _client.get(cls.base_uri(), params=cls.params(symbol))

        return cls.load(response=response)
