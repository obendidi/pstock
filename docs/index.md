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
## Contributors

Feel free to contribute !

<a href = "https://github.com/obendidi/pstock/graphs/contributors">
<img src = "https://contrib.rocks/image?repo=obendidi/pstock"/>
</a>
