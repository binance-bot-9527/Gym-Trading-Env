下载市场数据
==========

加密货币市场数据
--------------

支持的交易所 ...
^^^^^^^^^^^^^^^^^

该包提供了一种简便的方法来下载加密货币市场数据（基于 CCTX 并使用 asyncio 实现快速下载）。

例如，以下代码从 Binance、Bitfinex 和 Huobi 三个交易所下载 ``BTC/USDT`` 和 ``ETH/USDT`` 交易对的1小时时间框架的市场数据：

.. code-block:: python

  from gym_trading_env.downloader import download
  import datetime

  download(
      exchange_names = ["binance", "bitfinex2", "huobi"],
      symbols= ["BTC/USDT", "ETH/USDT"],
      timeframe= "1h",
      dir = "data",
      since= datetime.datetime(year= 2019, month= 1, day=1),
      until = datetime.datetime(year= 2023, month= 1, day=1),
  )

输出：

.. code-block:: bash

  BTC/USDT 从 binance 下载并存储于 data/binance-BTCUSDT-1h.pkl
  BTC/USDT 从 huobi 下载并存储于 data/huobi-BTCUSDT-1h.pkl
  ETH/USDT 从 binance 下载并存储于 data/binance-ETHUSDT-1h.pkl
  ETH/USDT 从 huobi 下载并存储于 data/huobi-ETHUSDT-1h.pkl
  BTC/USDT 从 bitfinex2 下载并存储于 data/bitfinex2-BTCUSDT-1h.pkl
  ETH/USDT 从 bitfinex2 下载并存储于 data/bitfinex2-ETHUSDT-1h.pkl

该函数使用 pickle 格式保存 OHLCV 数据。你需要使用 ``pd.read_pickle('... .pkl')`` 导入数据集。该函数支持交易所名称 ``binance``、``bitfinex2``（API v2）和 ``huobi``。

更多交易所 ...
^^^^^^^^^^^^^^^


可以添加 ccxt 中支持的其他交易所。

为此，你需要更新 ``EXCHANGE_LIMIT_RATES`` 变量：

* 从 ccxt 的交易所列表中获取交易所的 ``id``（`可在此处查看 <https://github.com/ccxt/ccxt/tree/master/python#certified-cryptocurrency-exchanges>`_）。
* 检查该交易所的 API 限速和查询策略，填写 ``limit``、``pause_every`` 和 ``pause`` 参数。请善待 API，避免被封禁。

以 **Bybit**（ccxt id：``bybit``）为例：

.. code-block:: python
  
  from gym_trading_env.downloader import download, EXCHANGE_LIMIT_RATES
  import datetime

  EXCHANGE_LIMIT_RATES["bybit"] = {
      "limit" : 200, # 每次请求查询200个数据点（即K线）。
      "pause_every" : 120, # 每120次请求暂停一次。
      "pause" : 2, # 暂停持续2秒。
  }
  download(
      exchange_names = ["binance", "bitfinex2", "huobi", "bybit"],
      symbols= ["BTC/USDT", "ETH/USDT"],
      timeframe= "1h",
      dir = "examples/data",
      since= datetime.datetime(year= 2023, month= 1, day=1),
  )


股票市场数据
-----------

敬请期待 ...
