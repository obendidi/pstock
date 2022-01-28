import inspect

import httpx
import pytest

import pstock

pytestmark = pytest.mark.anyio


def test_get_http_signature():
    with httpx.Client() as client:
        httpx_get_signature = inspect.signature(pstock.get_http_sync)
        client_get_signature = inspect.signature(client.get)

        httpx_get_parameters = dict(httpx_get_signature.parameters)
        httpx_get_parameters.pop("client")  # throw error if not exist

        assert httpx_get_parameters == dict(client_get_signature.parameters)
        assert (
            httpx_get_signature.return_annotation
            == client_get_signature.return_annotation
        )


async def test_get_http_async_signature():
    async with httpx.AsyncClient() as client:
        httpx_get_signature = inspect.signature(pstock.get_http_async)
        client_get_signature = inspect.signature(client.get)

        httpx_get_parameters = dict(httpx_get_signature.parameters)
        httpx_get_parameters.pop("client")  # throw error if not exist

        assert httpx_get_parameters == dict(client_get_signature.parameters)
        assert (
            httpx_get_signature.return_annotation
            == client_get_signature.return_annotation
        )


async def test_get_http_async(respx_mock):
    route = respx_mock.get("https://testurl/")
    response = await pstock.get_http_async("https://testurl/")
    assert route.called
    assert response.status_code == 200


def test_get_http_sync(respx_mock):
    route = respx_mock.get("https://testurl/")
    response = pstock.get_http_sync("https://testurl/")
    assert route.called
    assert response.status_code == 200


async def test_get_http_async_with_client(respx_mock):
    route = respx_mock.get("https://testurl/")
    async with httpx.AsyncClient() as client:
        response = await pstock.get_http_async("https://testurl/", client=client)
        assert route.called
        assert response.status_code == 200
        assert not client.is_closed


def test_get_http_sync_with_client(respx_mock):
    route = respx_mock.get("https://testurl/")
    with httpx.Client() as client:
        response = pstock.get_http_sync("https://testurl/", client=client)
        assert route.called
        assert response.status_code == 200
        assert not client.is_closed
