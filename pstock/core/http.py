import logging
import typing as tp

import anyio
import httpx
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    TimeoutTypes,
    URLTypes,
)
from tenacity import (
    TryAgain,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    wait_exponential,
    wait_random,
)

__all__ = "httpx_get"

logger = logging.getLogger(__name__)


def _check_retry_status(
    response: httpx.Response,
    retry_status_codes: tp.Optional[tp.List[int]] = None,
) -> None:
    if retry_status_codes and response.status_code in retry_status_codes:
        raise TryAgain()


async def _aget_with_client(
    url: URLTypes, client: httpx.AsyncClient, **kwargs: tp.Any
) -> httpx.Response:
    return await client.get(url, **kwargs)


async def _aget_without_client(url: URLTypes, **kwargs: tp.Any) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await _aget_with_client(url, client, **kwargs)


@retry(
    reraise=True,
    sleep=anyio.sleep,
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=4, max=10) + wait_random(0, 2),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def httpx_get(
    url: URLTypes,
    *,
    client: tp.Optional[httpx.AsyncClient] = None,
    retry_status_codes: tp.Optional[tp.List[int]] = None,
    params: QueryParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: tp.Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: tp.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: tp.Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: dict = None,
) -> httpx.Response:
    if client is None:
        response = await _aget_without_client(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
    else:
        response = await _aget_with_client(
            url,
            client,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
    _check_retry_status(response, retry_status_codes=retry_status_codes)
    return response
