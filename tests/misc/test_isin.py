import pickle
from pathlib import Path
from unittest import mock

import httpx
import pytest

import pstock
from pstock.misc.isin import get_isin_async, get_isin_sync

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def tsla_isin_response(data_dir) -> httpx.Response:
    with open(data_dir / "isin-tsla.obj", "rb") as f:
        return pickle.load(f)


@pytest.fixture
def invalid_isin_response(data_dir) -> httpx.Response:
    with open(data_dir / "isin-invalid.obj", "rb") as f:
        return pickle.load(f)


@pytest.mark.parametrize("symbol,isin", [("BTC-USD", None), ("^QQQ", None)])
def test_get_isin_sync_invalid_symbol(symbol, isin):
    assert get_isin_sync(symbol) == isin


@pytest.mark.parametrize("symbol,isin", [("BTC-USD", None), ("^QQQ", None)])
async def test_get_isin_async_invalid_symbol(symbol, isin):
    assert await get_isin_async(symbol) == isin


@pytest.mark.parametrize("client", [None, httpx.Client()])
def test_get_isin_sync_tsla(client: httpx.Client, tsla_isin_response):
    with mock.patch("pstock.get_http_sync", return_value=tsla_isin_response) as mocked:
        assert get_isin_sync("tsla", client=client) == "US88160R1014"
        mocked.assert_called_once_with(
            pstock.config.ISIN_URI,
            client=client,
            params={
                "max_results": 25,
                "query": "TSLA",
            },
        )
        if client is not None:
            assert not client.is_closed
            client.close()


@pytest.mark.parametrize("client", [None, httpx.AsyncClient()])
async def test_get_isin_async_tsla(client: httpx.AsyncClient, tsla_isin_response):
    with mock.patch("pstock.get_http_async", return_value=tsla_isin_response) as mocked:
        assert await get_isin_async("tsla", client=client) == "US88160R1014"
        mocked.assert_awaited_once_with(
            pstock.config.ISIN_URI,
            client=client,
            params={
                "max_results": 25,
                "query": "TSLA",
            },
        )
        if client is not None:
            assert not client.is_closed
            await client.aclose()


@pytest.mark.parametrize("client", [None, httpx.Client()])
def test_get_isin_sync_invalid(client: httpx.Client, invalid_isin_response):
    with mock.patch(
        "pstock.get_http_sync", return_value=invalid_isin_response
    ) as mocked:
        assert get_isin_sync("tsla", client=client) is None
        mocked.assert_called_once_with(
            pstock.config.ISIN_URI,
            client=client,
            params={
                "max_results": 25,
                "query": "TSLA",
            },
        )
        if client is not None:
            assert not client.is_closed
            client.close()


@pytest.mark.parametrize("client", [None, httpx.AsyncClient()])
async def test_get_isin_async_invalid(client: httpx.AsyncClient, invalid_isin_response):
    with mock.patch(
        "pstock.get_http_async", return_value=invalid_isin_response
    ) as mocked:
        assert await get_isin_async("tsla", client=client) is None
        mocked.assert_awaited_once_with(
            pstock.config.ISIN_URI,
            client=client,
            params={
                "max_results": 25,
                "query": "TSLA",
            },
        )
        if client is not None:
            assert not client.is_closed
            await client.aclose()
