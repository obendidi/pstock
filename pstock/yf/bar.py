import logging
import typing as tp
from datetime import datetime
from urllib.parse import urljoin

import anyio
import asyncer
import httpx

import pstock
from pstock.schemas.bar import Bars, BarsMulti
from pstock.yf.exceptions import YFUnprocessableEntity
from pstock.yf.settings import YFInterval, YFRange
from pstock.yf.utils import YFParams, get_valid_intervals, random_user_agent

logger = logging.getLogger(__name__)


def _compose_uri(symbol: str) -> str:
    return urljoin(pstock.config.yf.CHART_URI, symbol.upper())


def _process_response(symbol: str, response: httpx.Response) -> Bars:
    if response.status_code == 422:
        raise YFUnprocessableEntity(symbol, response)
    response.raise_for_status()
    return Bars.from_yf(data=response.json())


def _prep_for_request(
    symbol: str,
    interval: tp.Union[tp.Literal["auto"], YFInterval] = "auto",
    period: tp.Optional[YFRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
) -> tp.Tuple[YFParams, tp.Tuple[YFInterval, ...]]:
    valid_intervals = get_valid_intervals(interval, period=period, start=start)

    params = YFParams(
        interval=valid_intervals[0],
        period=period,
        start=start,
        end=end,
        include_prepost=include_prepost,
        events=events,
    )
    if interval == "auto":
        logger.debug(
            f"[{symbol}] Updating interval from '{interval}' to "
            f"'{params.interval}'."
        )
    return params, valid_intervals


def _set_interval_param(
    symbol: str, params: YFParams, interval: YFInterval
) -> YFParams:
    if interval != params.interval:
        logger.debug(
            f"[{symbol}] Updating interval from '{params.interval}' to "
            f"'{interval}'."
        )
    params.interval = interval
    return params


def get_bars_sync(
    symbol: str,
    interval: tp.Union[tp.Literal["auto"], YFInterval] = "auto",
    period: tp.Optional[YFRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.Client] = None,
) -> Bars:

    params, valid_intervals = _prep_for_request(
        symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        events=events,
        include_prepost=include_prepost,
    )
    errors: tp.List[BaseException] = []
    for valid_interval in valid_intervals:
        params = _set_interval_param(symbol, params, valid_interval)
        response = pstock.get_http_sync(
            url=_compose_uri(symbol),
            client=client,
            params=params.dict(exclude_none=True, by_alias=True),
            headers={"User-Agent": random_user_agent()},
        )
        try:
            return _process_response(symbol, response)
        except YFUnprocessableEntity as error:
            logger.warning(error)
            errors.append(error)
    raise anyio.ExceptionGroup(*errors)


async def get_bars_async(
    symbol: str,
    interval: tp.Union[tp.Literal["auto"], YFInterval] = "auto",
    period: tp.Optional[YFRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.AsyncClient] = None,
) -> Bars:
    params, valid_intervals = _prep_for_request(
        symbol,
        interval=interval,
        period=period,
        start=start,
        end=end,
        events=events,
        include_prepost=include_prepost,
    )
    errors: tp.List[BaseException] = []
    for valid_interval in valid_intervals:
        params = _set_interval_param(symbol, params, valid_interval)
        response = await pstock.get_http_async(
            url=_compose_uri(symbol),
            client=client,
            params=params.dict(exclude_none=True, by_alias=True),
            headers={"User-Agent": random_user_agent()},
        )
        try:
            return _process_response(symbol, response)
        except YFUnprocessableEntity as error:
            logger.warning(error)
            errors.append(error)
    raise anyio.ExceptionGroup(*errors)


async def get_bars_multi_async(
    symbols: tp.List[str],
    interval: tp.Union[tp.Literal["auto"], YFInterval] = "auto",
    period: tp.Optional[YFRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.AsyncClient] = None,
) -> BarsMulti:

    close_client = False
    if client is None:
        client = httpx.AsyncClient()
        close_client = True
    try:
        async with asyncer.create_task_group() as tg:
            soon_values = [
                tg.soonify(get_bars_async)(
                    symbol,
                    interval=interval,
                    period=period,
                    start=start,
                    end=end,
                    include_prepost=include_prepost,
                    events=events,
                    client=client,
                )
                for symbol in symbols
            ]
    finally:
        if close_client and client:
            await client.aclose()

    data = {
        symbol: soon_value.value for symbol, soon_value in zip(symbols, soon_values)
    }
    return BarsMulti.parse_obj(data)


def get_bars_multi_sync(
    symbols: tp.List[str],
    interval: tp.Union[tp.Literal["auto"], YFInterval] = "auto",
    period: tp.Optional[YFRange] = None,
    start: tp.Union[None, str, int, float, datetime] = None,
    end: tp.Union[None, str, int, float, datetime] = None,
    include_prepost: bool = False,
    events: tp.Literal["div", "split", "div,splits"] = "div,splits",
    client: tp.Optional[httpx.Client] = None,
) -> BarsMulti:

    close_client = False
    if client is None:
        client = httpx.Client()
        close_client = True
    try:
        async with asyncer.create_task_group() as tg:
            soon_values = [
                tg.soonify(get_bars_async)(
                    symbol,
                    interval=interval,
                    period=period,
                    start=start,
                    end=end,
                    include_prepost=include_prepost,
                    events=events,
                    client=client,
                )
                for symbol in symbols
            ]
        data = {
            symbol: get_bars_sync(
                symbol,
                interval=interval,
                period=period,
                start=start,
                end=end,
                include_prepost=include_prepost,
                events=events,
                client=client,
            )
            for symbol, soon_value in zip(symbols, soon_values)
        }
    finally:
        if close_client and client:
            client.close()

    data = {
        symbol: soon_value.value for symbol, soon_value in zip(symbols, soon_values)
    }
    return BarsMulti.parse_obj(data)


if __name__ == "__main__":
    bars = get_bars_sync("TSLA", period="ytd")
    print(bars.df)
