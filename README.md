# Pstock

## Disclaimer

**You should refer to Yahoo!'s terms of use**
([here](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm),
[here](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html), and
[here](https://policies.yahoo.com/us/en/yahoo/terms/index.htm)) **for
details on your rights to use the actual data downloaded. Remember - the
project is intended for personal use only.**

**Pstock** is an open source tool/project that is not affiliated in any way to yahoo-finance. Nothing in this project should be considered investment advice.

---
[![codecov](https://codecov.io/gh/obendidi/pstock/branch/main/graph/badge.svg?token=WU1E3ISBDK)](https://codecov.io/gh/obendidi/pstock)
<a target="new" href="https://pypi.python.org/pypi/pstock-python"><img border=0 src="https://img.shields.io/badge/python-3.8+-blue.svg?style=flat" alt="Python version"></a>
<a href="https://pypi.org/project/pstock-python" target="_blank">
<img src="https://img.shields.io/pypi/pyversions/pstock-python.svg?color=%2334D058" alt="Supported Python versions"></a>
<a target="new" href="https://pypi.python.org/pypi/pstock-python"><img border=0 src="https://img.shields.io/pypi/status/pstock-python.svg?maxAge=60" alt="PyPi status"></a>
<a target="new" href="https://pypi.python.org/pypi/pstock-python"><img border=0 src="https://img.shields.io/pypi/dm/pstock-python.svg?maxAge=2592000&label=installs&color=%2327B1FF" alt="PyPi downloads"></a>
![example workflow](https://github.com/obendidi/pstock/actions/workflows/test.yml/badge.svg)
![example workflow](https://github.com/obendidi/pstock/actions/workflows/docs.yml/badge.svg)

---

**Documentation**: <a href="https://obendidi.github.io/pstock" target="_blank">https://obendidi.github.io/pstock</a>

**Source Code**: <a href="https://github.com/obendidi/pstock" target="_blank">https://github.com/obendidi/pstock</a>


- [Pstock](#pstock)
  - [Disclaimer](#disclaimer)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quickstart](#quickstart)
  - [User Guide](#user-guide)
    - [Assets](#assets)
    - [Trends](#trends)
    - [Earnings](#earnings)
    - [Income Statement](#income-statement)
    - [News](#news)
    - [Bars (Historical price data)](#bars-historical-price-data)
    - [BarsMulti](#barsmulti)
  - [Sans-I/O protocol](#sans-io-protocol)
  - [Contributors](#contributors)

---

**Pstock** is *yet* another python unoficial API for getting yahoo-finance data.

The key features are:

- Async first
- Data validation using pydantic
- Fully typed, with great editor support
- Easily extensible: Parse the yahoo-finance quote dict and extract any type of info you want.
- Follows the Sans-IO design pattern: Use your favourite http library (sync/async) and let `pstock` parse your response to get `Assets` or `Bars`

## Requirements

Python 3.8+ (support for 3.6/3.7 may be added later, contributions are welcome)

Pstock depends mainly on:

- [pydantic](https://pydantic-docs.helpmanual.io/): For data validation
- [pandas](https://pandas.pydata.org/docs/): For structuring data in nice dataframes
- [httpx](https://www.python-httpx.org/): For the main async IO interface

## Installation

<div class="termy">

```console
$ pip install pstock-python

---> 100%
```

</div>

## Quickstart

- Download an asset:

```Python
import asyncio
from pstock import Asset

asset = asyncio.run(Asset.get("TSLA"))
print(asset)
# symbol='TSLA' name='Tesla, Inc.' asset_type='EQUITY' currency='USD' latest_price=920.0 sector='Consumer Cyclical' industry='Auto Manufacturers'
```

- Download a list of assets:

```Python
import asyncio
from pstock import Asset

assets = asyncio.run(Assets.get(["TSLA", "AAPL", "GME"]))
print(assets)
# __root__=[Asset(symbol='TSLA', name='Tesla, Inc.', asset_type='EQUITY', currency='USD', latest_price=918.97, sector='Consumer Cyclical', industry='Auto Manufacturers'), Asset(symbol='AAPL', name='Apple Inc.', asset_type='EQUITY', currency='USD', latest_price=172.345, sector='Technology', industry='Consumer Electronics'), Asset(symbol='GME', name='GameStop Corp.', asset_type='EQUITY', currency='USD', latest_price=125.0, sector='Consumer Cyclical', industry='Specialty Retail')]

print(assets[0])
# Asset(symbol='TSLA', name='Tesla, Inc.', asset_type='EQUITY', currency='USD', latest_price=918.97, sector='Consumer Cyclical', industry='Auto Manufacturers')

print(assets.df)
                  name asset_type currency  ...                                           earnings                                             trends                                   income_statement
symbol                                      ...
AAPL        Apple Inc.     EQUITY      USD  ...  [{'quarter': '1Q2021', 'estimate': 0.99, 'actu...  [{'date': 2021-11-17, 'strong_buy': 13, 'buy':...  [{'date': 2021-09-25, 'ebit': 108949000000.0, ...
GME     GameStop Corp.     EQUITY      USD  ...  [{'quarter': '1Q2021', 'estimate': 1.35, 'actu...  [{'date': 2021-11-17, 'strong_buy': 2, 'buy': ...  [{'date': 2021-01-30, 'ebit': -249300000.0, 't...
TSLA       Tesla, Inc.     EQUITY      USD  ...  [{'quarter': '1Q2021', 'estimate': 0.79, 'actu...  [{'date': 2021-11-17, 'strong_buy': 4, 'buy': ...  [{'date': 2021-12-31, 'ebit': 6523000000.0, 't...
```

- Download historical bars:

```Python
import asyncio
from pstock import Bars

bars = asyncio.run(Bars.get("TSLA"))
print(bars)
# __root__=[Bar(date=datetime.datetime(2010, 7, 1, 4, 0, tzinfo=datetime.timezone.utc), open=5.0, high=5.184000015258789, low=2.996000051498413, close=3.98799991607666, adj_close=3.98799991607666, volume=322879000.0, interval=Duration(months=1)), Bar(date=datetime.datetime(2010, 8, 1, 4, 0, tzinfo=datetime.timezone.utc), open=4.099999904632568, high=4.435999870300293, low=3.4779999256134033, close=3.8959999084472656, adj_close=3.8959999084472656, volume=75191000.0, interval=Duration(months=1)), Bar(date=datetime.datetime(2010, 9, 1, 4, 0, tzinfo=datetime.timezone.utc), open=3.9240000247955322, high=4.631999969482422, low=3.9000000953674316, close=4.081999778747559, adj_close=4.081999778747559, volume=90229500.0, interval=Duration(months=1)), Bar(date=datetime.datetime(2010, 10, 1, 4, 0, tzinfo=datetime.timezone.utc), open=4.138000011444092, high=4.374000072479248, low=4.0, close=4.368000030517578, adj_close=4.368000030517578, volume=32739000.0, interval=Duration(months=1)), ....]

print(bars.df)
                   open         high         low        close    adj_close       volume interval
date
2010-07-01     5.000000     5.184000    2.996000     3.988000     3.988000  322879000.0  30 days
2010-08-01     4.100000     4.436000    3.478000     3.896000     3.896000   75191000.0  30 days
2010-09-01     3.924000     4.632000    3.900000     4.082000     4.082000   90229500.0  30 days
2010-10-01     4.138000     4.374000    4.000000     4.368000     4.368000   32739000.0  30 days
2010-11-01     4.388000     7.200000    4.210000     7.066000     7.066000  141575500.0  30 days
...                 ...          ...         ...          ...          ...          ...      ...
2021-11-01  1145.000000  1243.489990  978.599976  1144.760010  1144.760010  648671800.0  30 days
2021-12-01  1160.699951  1172.839966  886.119995  1056.780029  1056.780029  509945100.0  30 days
2022-01-01  1147.750000  1208.000000  792.010010   936.719971   936.719971  638471400.0  30 days
2022-02-01   935.210022   947.770020  850.700012   875.760010   875.760010  223112600.0  30 days
2022-02-15   900.000000   923.000000  893.377380   922.429993   922.429993   19085243.0  30 days

[141 rows x 7 columns]
```

- Download stock news:

```Python
import asyncio
from pstock import News

news = asyncio.run(News.get("TSLA"))
print(news.df)
                                                                       title                                            url                                            summary
date
2022-02-15 12:11:46+00:00  Retail investor: 'I'm being careful just in ca...  https://finance.yahoo.com/news/retail-investor...  Some retail investors are being more cautious ...
2022-02-15 12:23:00+00:00  Tesla’s Elon Musk Gave Away $5.7 Billion. But ...  https://finance.yahoo.com/m/d342cd56-d5bb-3957...  Tesla CEO Elon Musk gave away more than 5 mill...
2022-02-15 13:07:02+00:00                      Company News for Feb 15, 2022  https://finance.yahoo.com/news/company-news-fe...    Companies In The News Are: IFS, OLK, THS, TSLA.
....
2022-02-15 19:23:43+00:00  Australia's Syrah Resources to expand Louisian...  https://finance.yahoo.com/news/australias-syra...  Australian industrial materials firm Syrah Res...
2022-02-15 20:31:30+00:00       Biggest Companies in the World by Market Cap  https://finance.yahoo.com/m/8aead0a5-ef35-3d90...  The world's biggest companies by market cap op...
```

## User Guide

### Assets

An `Asset` in `pstock` terms is any ticker symbol supported by yahoo-finance. If the asset exists in yahoo-finance, you should be able to get it's quote summary  using `pstock`.

```Python
import asyncio
from pstock import Asset

asset = asyncio.run(Asset.get("TSLA"))
print(asset)
# symbol='TSLA' name='Tesla, Inc.' asset_type='EQUITY' currency='USD' latest_price=920.0 sector='Consumer Cyclical' industry='Auto Manufacturers'
```

An `Asset` will always have a:

- `symbol`: The ticker symbol of the asset
- `name`: The long/short name of the asset (depending on which is found, the long name takes priority)
- `asset_type`: Type of the asset, can be one of: `EQUITY`, `CURRENCY`, `CRYPTOCURRENCY`, `ETF`, `FUTURE`, `INDEX`
- `currency`: Currency of the asset, `USD` for US stocks
- `latest_price`: Latest price of the asset known by yahoo-finance, takes into account the pre-post market prices. Can be `numpy.nan` if no proce data is found.

> _Note: if an `asset_type` exists in yahoo-finance but is not one of the above, feel free to open an issue or PR. In the meantime you can subclass the `Asset` object and override the type of `asset_type` and add the missing asset type_

The other fields are optional and can be filled depending on the `asset_type`, currently there are only fields for the `EQUITY` (stocks) asset_type:

- `sector`
- `industry`
- [trends](#trends)
- [earnings](#earnings)
- [income_statement](#income-statement)

In addition to getting data about a single `Asset`, there is also the possibily to query multiple assets at the same time using `Assets`. The main benefit is that it provides the ability to directly convert the resulting list of assets into a pandas dataframe.

```Python
import asyncio
from pstock import Asset

assets = asyncio.run(Assets.get(["TSLA", "AAPL", "GME"]))

print(assets.df)
                  name asset_type currency  ...                                           earnings                                             trends                                   income_statement
symbol                                      ...
AAPL        Apple Inc.     EQUITY      USD  ...  [{'quarter': '1Q2021', 'estimate': 0.99, 'actu...  [{'date': 2021-11-17, 'strong_buy': 13, 'buy':...  [{'date': 2021-09-25, 'ebit': 108949000000.0, ...
GME     GameStop Corp.     EQUITY      USD  ...  [{'quarter': '1Q2021', 'estimate': 1.35, 'actu...  [{'date': 2021-11-17, 'strong_buy': 2, 'buy': ...  [{'date': 2021-01-30, 'ebit': -249300000.0, 't...
TSLA       Tesla, Inc.     EQUITY      USD  ...  [{'quarter': '1Q2021', 'estimate': 0.79, 'actu...  [{'date': 2021-11-17, 'strong_buy': 4, 'buy': ...  [{'date': 2021-12-31, 'ebit': 6523000000.0, 't...
```

> _Note 1: `Assets` is also a pydantic model that will validate data that it pulls from yahoo-finance._

> _Note 2: The generated pandas Dataframe is cached into a private `._df` attribute and is computed only the first time it is accessed via the property `.df`._

> _Note 3: Most if not all data objects in `pstock` have a `.df` property, and it's the recommended way to view and manipulate data when possible._

> _Note 4: `Assets`, `Bars`, `Earnings`, `News`, ... can also be iterated over and support indexing and behave like a `typing.List[Asset]`, `typing.List[Bar]`, ..._
### Trends

There are 2 ways to get the trends of a symbol.

- via `Asset`:

```Python
import asyncio
from pstock import Asset

asset = asyncio.run(Asset.get("TSLA"))
print(asset.trends.df)

            strong_buy  buy  hold  sell  strong_sell  score recomendation
date
2021-11-17           4    4     8     6            0   2.73          HOLD
2021-12-17          11    6    13     6            0   2.39           BUY
2022-01-16          11    6    13     6            0   2.39           BUY
2022-02-15           4    4     8     6            0   2.73          HOLD
```

- Directly via `Trends`

```Python
import asyncio
from pstock import Trends

trends = asyncio.run(Trends.get("TSLA"))
print(trends.df)

            strong_buy  buy  hold  sell  strong_sell  score recomendation
date
2021-11-17           4    4     8     6            0   2.73          HOLD
2021-12-17          11    6    13     6            0   2.39           BUY
2022-01-16          11    6    13     6            0   2.39           BUY
2022-02-15           4    4     8     6            0   2.73          HOLD
```

### Earnings

There are 2 ways to get the earnings of a symbol.

- via `Asset`:

```Python
import asyncio
from pstock import Asset

asset = asyncio.run(Asset.get("TSLA"))
print(asset.earnings.df)

         estimate  actual status       revenue      earnings
quarter
1Q2021       0.79    0.93   Beat  1.038900e+10  4.380000e+08
2Q2021       0.98    1.45   Beat  1.195800e+10  1.142000e+09
3Q2021       1.59    1.86   Beat  1.375700e+10  1.618000e+09
4Q2021       2.37    2.54   Beat  1.771900e+10  2.321000e+09
1Q2022       2.25     NaN   None           NaN           NaN
```

- Directly via `Earnings`

```Python
import asyncio
from pstock import Earnings

earnings = asyncio.run(Earnings.get("TSLA"))
print(earnings.df)

         estimate  actual status       revenue      earnings
quarter
1Q2021       0.79    0.93   Beat  1.038900e+10  4.380000e+08
2Q2021       0.98    1.45   Beat  1.195800e+10  1.142000e+09
3Q2021       1.59    1.86   Beat  1.375700e+10  1.618000e+09
4Q2021       2.37    2.54   Beat  1.771900e+10  2.321000e+09
1Q2022       2.25     NaN   None           NaN           NaN
```

> _Note: The last earning have `NaN`/`None` values since we only have analysts estimates and revenue isn't reported yet. The specific earnings call date can be extracted from the `QuoteSummary`._

### Income Statement

There are 2 ways to get the income statement of a symbol.

> _Note: The current extracted statement is very limited/minimaliste, contributions are welcome to extract more data from the `QuoteSummary`._

- via `Asset`:

```Python
import asyncio
from pstock import Asset

asset = asyncio.run(Asset.get("TSLA"))
print(asset.income_statement.df)

                    ebit  total_revenue  gross_profit
date
2018-12-31 -2.530000e+08   2.146100e+10  4.042000e+09
2019-12-31  8.000000e+07   2.457800e+10  4.069000e+09
2020-12-31  1.951000e+09   3.153600e+10  6.630000e+09
2021-12-31  6.523000e+09   5.382300e+10  1.360600e+10
```

> _Note: `asset.income_statement` can be `None` for all assets that are not of type `EQUITY`._

- Directly via `IncomeStatements`

```Python
import asyncio
from pstock import IncomeStatements

income_statement = asyncio.run(IncomeStatements.get("TSLA"))
print(income_statement.df)

                    ebit  total_revenue  gross_profit
date
2018-12-31 -2.530000e+08   2.146100e+10  4.042000e+09
2019-12-31  8.000000e+07   2.457800e+10  4.069000e+09
2020-12-31  1.951000e+09   3.153600e+10  6.630000e+09
2021-12-31  6.523000e+09   5.382300e+10  1.360600e+10
```

> _Note: You can also use `QuarterlyIncomeStatements` for (as the name says) quarterly income stamenets_.

### News

Gettings yahoo-finance news about a symbol also follows the same pattern.

```Python
import asyncio
from pstock import News

news = asyncio.run(News.get("TSLA"))
print(news.df)
                                                                       title                                            url                                            summary
date
2022-02-15 12:11:46+00:00  Retail investor: 'I'm being careful just in ca...  https://finance.yahoo.com/news/retail-investor...  Some retail investors are being more cautious ...
2022-02-15 12:23:00+00:00  Tesla’s Elon Musk Gave Away $5.7 Billion. But ...  https://finance.yahoo.com/m/d342cd56-d5bb-3957...  Tesla CEO Elon Musk gave away more than 5 mill...
2022-02-15 13:07:02+00:00                      Company News for Feb 15, 2022  https://finance.yahoo.com/news/company-news-fe...    Companies In The News Are: IFS, OLK, THS, TSLA.
....
2022-02-15 19:23:43+00:00  Australia's Syrah Resources to expand Louisian...  https://finance.yahoo.com/news/australias-syra...  Australian industrial materials firm Syrah Res...
2022-02-15 20:31:30+00:00       Biggest Companies in the World by Market Cap  https://finance.yahoo.com/m/8aead0a5-ef35-3d90...  The world's biggest companies by market cap op...
```

### Bars (Historical price data)

A `Bar` in `pstock` is a pydantic model with the following fields:

```Python
class Bar(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float
    interval: timedelta
```

> _Note: The `interval` is the time between bar `open` and `close`._

To get `Bars` there are a couple of arguments that can be specified:

- `interval`: one of `1m`, `2m`, `5m`, `15m`, `30m`, `1h`, `1d`, `5d`, `1mo`, `3mo`, defaults to `None`
- `period`: one of `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`, defaults to `None`
- `start`: Any `date`/`datetime` [supported by pydnatic](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types), defaults to `None`
- `end`: Any `date`/`datetime` [supported by pydnatic](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types), defaults to `None`
- `events`: one of `div`, `split`, `div,splits`, defaults to `div,splits`
- `include_prepost`: Bool, include Pre and Post market bars, default to `False`


By default, if no argument is provided, the `period` is set to `max` and the interval to `3mo`, example:

> _**Note**: It is possible for yahoo-finance to return bars of different interval than what was specified in the request (example below, requested `3mo` interval bars, got an interval of `1mo` because `TSLA` is a relatively new stock and it's max period is around ~10 years by the time of writing)._

```Python
import asyncio
from pstock import Bars

bars = asyncio.run(Bars.get("TSLA"))
print(bars.df)

                   open         high         low        close    adj_close       volume interval
date
2010-07-01     5.000000     5.184000    2.996000     3.988000     3.988000  322879000.0  30 days
2010-08-01     4.100000     4.436000    3.478000     3.896000     3.896000   75191000.0  30 days
2010-09-01     3.924000     4.632000    3.900000     4.082000     4.082000   90229500.0  30 days
2010-10-01     4.138000     4.374000    4.000000     4.368000     4.368000   32739000.0  30 days
2010-11-01     4.388000     7.200000    4.210000     7.066000     7.066000  141575500.0  30 days
...                 ...          ...         ...          ...          ...          ...      ...
2021-11-01  1145.000000  1243.489990  978.599976  1144.760010  1144.760010  648671800.0  30 days
2021-12-01  1160.699951  1172.839966  886.119995  1056.780029  1056.780029  509945100.0  30 days
2022-01-01  1147.750000  1208.000000  792.010010   936.719971   936.719971  638471400.0  30 days
2022-02-01   935.210022   947.770020  850.700012   875.760010   875.760010  223112600.0  30 days
2022-02-15   900.000000   923.000000  893.377380   922.429993   922.429993   19085243.0  30 days

[141 rows x 7 columns]
```

> _**Note 1**: Yahoo-finance limits the `interval` of data we can fetch based on how old the data is. For example we can't get `1m` bars for a period (or start/end) older than 7 days._

<details markdown="1">
<summary>Example of an interval error ...</summary>

```Python
import asyncio
from pstock import Bars

bars = asyncio.run(Bars.get("TSLA", period="1mo", interval="1m"))
print(bars.df)

Traceback (most recent call last):
  File "pstock/bar.py", line 243, in <module>
    bars = asyncio.run(Bars.get("TSLA", period="1mo", interval="1m"))
  File "user/.pyenv/versions/3.8.12/lib/python3.8/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "user/.pyenv/versions/3.8.12/lib/python3.8/asyncio/base_events.py", line 616, in run_until_complete
    return future.result()
  File "pstock/bar.py", line 196, in get
    return cls.load(response=response)
  File "pstock/bar.py", line 169, in load
    return cls.parse_obj(get_ohlc_from_chart(data))
  File "user/git/pstock/pstock/utils/chart.py", line 18, in get_ohlc_from_chart
    raise ValueError(f"Yahoo-finance responded with an error:\n{error}")
ValueError: Yahoo-finance responded with an error:
{'code': 'Unprocessable Entity', 'description': '1m data not available for startTime=1642289894 and endTime=1644968294. Only 7 days worth of 1m granularity data are allowed to be fetched per request.'}
```
> </details>

> _**Note2** By leaving the `interval` parameter empty (=`None`), `pstock` automatically tries to find the lowest `interval` possible based on how old the data requested is._

```Python
import asyncio
from pstock import Bars

bars = asyncio.run(Bars.get("TSLA", period="1mo"))
print(bars.df)

# Automatically finds that the lowest interval for a period of `1mo` is `2m`

                                  open         high          low        close    adj_close     volume        interval
date
2022-01-18 14:30:00+00:00  1028.000000  1030.000000  1023.000000  1023.983582  1023.983582  1125597.0 0 days 00:02:00
2022-01-18 14:32:00+00:00  1023.230103  1032.000000  1023.230103  1029.807983  1029.807983   228889.0 0 days 00:02:00
2022-01-18 14:34:00+00:00  1029.949951  1029.949951  1023.700012  1025.000000  1025.000000   248188.0 0 days 00:02:00
2022-01-18 14:36:00+00:00  1024.319946  1025.999878  1018.000000  1021.000000  1021.000000   289773.0 0 days 00:02:00
2022-01-18 14:38:00+00:00  1021.669922  1024.000000  1018.440002  1020.150024  1020.150024   183713.0 0 days 00:02:00
...                                ...          ...          ...          ...          ...        ...             ...
2022-02-15 20:52:00+00:00   919.640015   920.989990   919.171570   919.179993   919.179993   189152.0 0 days 00:02:00
2022-02-15 20:54:00+00:00   919.320007   920.770020   918.869995   920.075012   920.075012   178398.0 0 days 00:02:00
2022-02-15 20:56:00+00:00   920.010010   921.000000   919.859985   920.940002   920.940002   207078.0 0 days 00:02:00
2022-02-15 20:58:00+00:00   920.900024   923.000000   920.750000   922.260010   922.260010   382232.0 0 days 00:02:00
2022-02-15 21:00:00+00:00   922.429993   922.429993   922.429993   922.429993   922.429993        0.0 0 days 00:02:00

[4093 rows x 7 columns]
```

> _**Note3** Instead of using `period` it is also possible to set a specific `start` and optioally `end` value. If `end` is not set, it defaults to current UTC time._

### BarsMulti

Sometimes we'll want to get bars for multiple symbols at the same time.

```Python
import asyncio
from pstock import BarsMulti

bars = asyncio.run(BarsMulti.get(["TSLA", "AAPL"], period="5d", interval="1d"))
print(bars.df)

                  TSLA                                                                             AAPL
                  open        high         low       close   adj_close      volume interval        open        high         low       close   adj_close      volume interval
date
2022-02-09  935.000000  946.270020  920.000000  932.000000  932.000000  17419800.0   1 days  176.050003  176.649994  174.899994  176.279999  176.279999  71285000.0   1 days
2022-02-10  908.369995  943.809998  896.700012  904.549988  904.549988  22042300.0   1 days  174.139999  175.479996  171.550003  172.119995  172.119995  90865900.0   1 days
2022-02-11  909.630005  915.960022  850.700012  860.000000  860.000000  26492700.0   1 days  172.330002  173.080002  168.039993  168.639999  168.639999  98566000.0   1 days
2022-02-14  861.570007  898.880005  853.150024  875.760010  875.760010  22515100.0   1 days  167.369995  169.580002  166.559998  168.880005  168.880005  86062800.0   1 days
2022-02-15  900.000000  923.000000  893.377380  922.429993  922.429993  19085243.0   1 days  170.970001  172.949997  170.250000  172.789993  172.789993  62512704.0   1 days
```

> _**Note** Bars of a specific symbol can be accessed by using the sumbol as key:
> `bars["TSLA"].df == bars.df["TSLA"] == Bars.get("TSLA").df`_

## Sans-I/O protocol

> An I/O-free protocol implementation (colloquially referred to as a “sans-IO” implementation) is an implementation of a network protocol that contains no code that does any form of network I/O or any form of asynchronous flow control. Put another way, a sans-IO protocol implementation is one that is defined entirely in terms of synchronous functions returning synchronous results, and that does not block or wait for any form of I/O.
> ............
> By keeping async flow control and I/O out of your protocol implementation, it provides the ability to use that implementation across all forms of flow control. This means that the core of the protocol implementation is divorced entirely from the way I/O is done or the way the API is designed.

-> [https://sans-io.readthedocs.io](https://sans-io.readthedocs.io/)

Although `pstock` provides an async IO interface to get data from yahoo-finance, It is still extremly easy to use it with other http libraries or other ways to get data.

A simple example is using the popular `requests` library:

```python
import requests
from pstock import Asset, rdm_user_agent_value

url = Asset.uri("TSLA")
headers = {"User-Agent": rdm_user_agent_value()}

response = requests.get(url, headers=headers)

asset = Asset.load(response=response)
```

The `response` object can be an `str` or `bytes` content of the response. Or it can even be the whole response object (should have a `.read()` method that returns content).

The same can be done for generating `Bars`

```python
import requests
from pstock import Bars, rdm_user_agent_value

url = Bars.uri("TSLA", interval="1m", period="1d")
headers = {"User-Agent": rdm_user_agent_value()}

response = requests.get(url, headers=headers)

bars = Bars.load(response=response)
```



## Contributors

Feel free to contribute !

<a href = "https://github.com/obendidi/pstock/graphs/contributors">
<img src = "https://contrib.rocks/image?repo=obendidi/pstock"/>
</a>
