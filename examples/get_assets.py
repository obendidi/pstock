import typing as tp

import asyncer

from pstock import Assets


async def main(symbols: tp.List[str]) -> None:
    print(f"Getting asset data from yahoo-finance for '{symbols}' ...")
    assets = await Assets.get(symbols)
    print(f"... got the {len(assets)} assets.")

    print("\n=> Dataframe with all the assets:")
    print(assets.df)

    print("\nThe Dataframe is indexing by the symbols:")
    print(f"assets.df.loc['TSLA']:\n{assets.df.loc['TSLA']}")

    print("\n=> Per-Asset:")
    for asset in assets:
        print(f"{asset} Earnings:\n{asset.earnings.df}")
        print(f"{asset} Trends:\n{asset.trends.df}")
        print(f"{asset} Income Statement:\n{asset.income_statement.df}")
        print()


if __name__ == "__main__":
    asyncer.runnify(main)(["TSLA", "AAPL", "GOOG", "AMZN", "NFLX", "FB"])
