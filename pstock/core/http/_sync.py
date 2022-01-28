import typing as tp

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


def _with_client(
    url: URLTypes, client: httpx.Client, **kwargs: tp.Any
) -> httpx.Response:
    return client.get(url, **kwargs)


def _without_client(url: URLTypes, **kwargs: tp.Any) -> httpx.Response:
    with httpx.Client() as client:
        return _with_client(url, client, **kwargs)


def get_http_sync(
    url: URLTypes,
    *,
    client: tp.Optional[httpx.Client] = None,
    params: QueryParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: tp.Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    follow_redirects: tp.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    timeout: tp.Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    extensions: dict = None,
) -> httpx.Response:
    if client is None:
        return _without_client(
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
        return _with_client(
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
