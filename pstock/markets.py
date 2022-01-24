import typing as tp

import httpx
import pandas as pd

from pstock.core import httpx_get
from pstock.schemas import Asset, Assets


async def get_sp500_assets(
    client: tp.Optional[httpx.AsyncClient] = None,
) -> Assets:

    response = await httpx_get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", client=client
    )
    response.raise_for_status()
    sp500 = pd.read_html(response.content)[0]
    # for compatibility with yahoo-finance
    sp500["Symbol"] = sp500["Symbol"].str.replace(".", "-", regex=True)
    return Assets.parse_obj(
        [
            Asset(
                symbol=row["Symbol"],
                name=row["Security"],
                type="EQUITY",
                market="us_market",
                sector=row["GICS Sector"],
                industry=row["GICS Sub-Industry"],
                country="United States",
            )
            for _, row in sp500.iterrows()
        ]
    )


if __name__ == "__main__":
    import logging

    import asyncer
    import httpx_cache

    from pstock.core.log import setup_logging
    from pstock.yahoo_finance import get_assets

    setup_logging(level="DEBUG")
    logger = logging.getLogger()

    sp500 = asyncer.runnify(get_sp500_assets)()
    symbols = list(sp500.df.index)

    async def _main():
        async with httpx_cache.AsyncClient(
            cache=httpx_cache.FileCache(cache_dir=".cache")
        ) as client:
            return await get_assets(symbols, client=client)

    yf_assets = asyncer.runnify(_main)()
    print(sp500.df)
    print(yf_assets.df[["name", "type", "market", "sector", "industry", "country"]])

# def tickers_nasdaq(include_company_data=False):

#     """Downloads list of tickers currently listed in the NASDAQ"""

#     ftp = ftplib.FTP("ftp.nasdaqtrader.com")
#     ftp.login()
#     ftp.cwd("SymbolDirectory")

#     r = io.BytesIO()
#     ftp.retrbinary("RETR nasdaqlisted.txt", r.write)

#     if include_company_data:
#         r.seek(0)
#         data = pd.read_csv(r, sep="|")
#         return data

#     info = r.getvalue().decode()
#     splits = info.split("|")

#     tickers = [x for x in splits if "\r\n" in x]
#     tickers = [x.split("\r\n")[1] for x in tickers if "NASDAQ" not in x != "\r\n"]
#     tickers = [ticker for ticker in tickers if "File" not in ticker]

#     ftp.close()

#     return tickers


# def tickers_other(include_company_data=False):
#     '''Downloads list of tickers currently listed in the "otherlisted.txt"
#     file on "ftp.nasdaqtrader.com"'''
#     ftp = ftplib.FTP("ftp.nasdaqtrader.com")
#     ftp.login()
#     ftp.cwd("SymbolDirectory")

#     r = io.BytesIO()
#     ftp.retrbinary("RETR otherlisted.txt", r.write)

#     if include_company_data:
#         r.seek(0)
#         data = pd.read_csv(r, sep="|")
#         return data

#     info = r.getvalue().decode()
#     splits = info.split("|")

#     tickers = [x for x in splits if "\r\n" in x]
#     tickers = [x.split("\r\n")[1] for x in tickers]
#     tickers = [ticker for ticker in tickers if "File" not in ticker]

#     ftp.close()

#     return tickers
