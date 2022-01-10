import typing as tp

import httpx

from pstock.core import httpx_get, httpx_aget

ISIN_URI = "https://markets.businessinsider.com/ajax/SearchController_Suggest"
MAX_RESULTS = 25


def _is_valid_ticker(ticker: str) -> bool:
    if "-" in ticker or "^" in ticker:
        return False
    return True


def _parse_insin_response(ticker: str, response: httpx.Response) -> tp.Optional[str]:
    response.raise_for_status()
    search_str = f'"{ticker}|'
    if search_str not in response.text:
        return None
    return response.text.split(search_str)[1].split('"')[0].split("|")[0]


def get_isin(ticker: str, client: tp.Optional[httpx.Client] = None) -> tp.Optional[str]:
    if not _is_valid_ticker(ticker):
        return None
    response = httpx_get(
        ISIN_URI,
        client=client,
        params={
            "max_results": MAX_RESULTS,
            "query": ticker,
        },
    )
    return _parse_insin_response(ticker, response)


async def aget_isin(
    ticker: str, client: tp.Optional[httpx.AsyncClient] = None
) -> tp.Optional[str]:
    if not _is_valid_ticker(ticker):
        return None
    response = await httpx_aget(
        ISIN_URI,
        client=client,
        params={
            "max_results": MAX_RESULTS,
            "query": ticker,
        },
    )
    return _parse_insin_response(ticker, response)


if __name__ == "__main__":
    import time

    import anyio

    tickers = ["TSLA", "AAPL", "GM", "GOOG", "FB", "AMZN", "AMD", "NVDA", "GME", "SPCE"]
    data = {}
    with httpx.Client() as client:
        start = time.perf_counter()
        for ticker in tickers:
            data[ticker] = get_isin(ticker, client=client)
        print(f"Client: Finished in {time.perf_counter() - start:.2f} seconds.")
        for ticker, isin in data.items():
            print(f"\t{ticker} => {isin}")

    async def _main():
        data = {}

        async with httpx.AsyncClient() as client:

            async def _worker(ticker):
                isin = await aget_isin(ticker, client=client)
                data[ticker] = isin

            start = time.perf_counter()
            async with anyio.create_task_group() as tg:
                for ticker in tickers:
                    tg.start_soon(_worker, ticker)
            print(
                f"AsyncClient: Finished in {time.perf_counter() - start:.2f} seconds."
            )
            for ticker, isin in data.items():
                print(f"\t{ticker} => {isin}")

    anyio.run(_main)
