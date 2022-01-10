import inspect
import httpx
from pstock.core import httpx_aget, httpx_get
import pytest

pytestmark = pytest.mark.anyio


def test_httpx_get_signature():
    client = httpx.Client()
    httpx_get_signature = inspect.signature(httpx_get)
    client_get_signature = inspect.signature(client.get)

    httpx_get_parameters = dict(httpx_get_signature.parameters)
    httpx_get_parameters.pop("client")  # throw error if not exist
    httpx_get_parameters.pop("retry_status_codes")

    assert httpx_get_parameters == dict(client_get_signature.parameters)
    assert (
        httpx_get_signature.return_annotation == client_get_signature.return_annotation
    )
    client.close()


async def test_httpx_aget_signature():
    client = httpx.AsyncClient()
    httpx_get_signature = inspect.signature(httpx_aget)
    client_get_signature = inspect.signature(client.get)

    httpx_get_parameters = dict(httpx_get_signature.parameters)
    httpx_get_parameters.pop("client")  # throw error if not exist
    httpx_get_parameters.pop("retry_status_codes")

    assert httpx_get_parameters == dict(client_get_signature.parameters)
    assert (
        httpx_get_signature.return_annotation == client_get_signature.return_annotation
    )
    await client.aclose()


def test_httpx_get(respx_mock):
    route = respx_mock.get("https://testurl/")

    response = httpx_get("https://testurl/")
    assert route.called
    assert response.status_code == 200


def test_httpx_get_with_client(respx_mock):
    route = respx_mock.get("https://testurl/")
    client = httpx.Client()

    response = httpx_get("https://testurl/", client=client)
    assert route.called
    assert response.status_code == 200

    assert not client.is_closed
    client.close()


async def test_httpx_aget(respx_mock):
    route = respx_mock.get("https://testurl/")

    response = await httpx_aget("https://testurl/")
    assert route.called
    assert response.status_code == 200


async def test_httpx_aget_with_client(respx_mock):
    route = respx_mock.get("https://testurl/")
    client = httpx.AsyncClient()

    response = await httpx_aget("https://testurl/", client=client)
    assert route.called
    assert response.status_code == 200

    assert not client.is_closed
    await client.aclose()
