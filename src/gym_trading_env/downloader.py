import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import datetime
import numpy as np
import nest_asyncio
nest_asyncio.apply()
import sys 
if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
EXCHANGE_LIMIT_RATES = {
    # 交易所请求限制速率配置
    # limit: 每批次请求的数据量
    # pause_every: 每隔多少批次暂停一次
    # pause: 暂停时长（秒）
    "bitfinex2": {
        "limit":10_000,
        "pause_every": 1,
        "pause" : 3, #seconds
    },
    "binance": {
        "limit":1_000,
        "pause_every": 10,
        "pause" : 1, #seconds
    },
    "huobi": {
        "limit":1_000,
        "pause_every": 10,
        "pause" : 1, #seconds
    }
}

async def _ohlcv(exchange, symbol, timeframe, limit, step_since, timedelta):
    # 异步获取OHLCV（开盘价、最高价、最低价、收盘价、交易量）数据。
    # exchange: 交易所对象。
    # symbol: 交易对符号（例如："BTC/USDT"）。
    # timeframe: 时间周期（例如："5m"）。
    # limit: 每次请求的数据量限制。
    # step_since: 开始时间戳。
    # timedelta: 时间周期对应的毫秒数。
    result = await exchange.fetch_ohlcv(symbol = symbol, timeframe= timeframe, limit= limit, since=step_since)
    result_df = pd.DataFrame(result, columns=["timestamp_open", "open", "high", "low", "close", "volume"])
    for col in ["open", "high", "low", "close", "volume"]:
        result_df[col] = pd.to_numeric(result_df[col])
    result_df["date_open"] = pd.to_datetime(result_df["timestamp_open"], unit= "ms")
    result_df["date_close"] = pd.to_datetime(result_df["timestamp_open"] + timedelta, unit= "ms")

    return result_df

async def _download_symbol(exchange, symbol, timeframe = '5m', since = int(datetime.datetime(year=2020, month= 1, day= 1).timestamp()*1E3), until = int(datetime.datetime.now().timestamp()*1E3), limit = 1000, pause_every = 10, pause = 1):
    # 异步下载单个交易对的历史数据。
    # exchange: 交易所对象。
    # symbol: 交易对符号。
    # timeframe: 时间周期。
    # since: 开始时间戳（毫秒）。
    # until: 结束时间戳（毫秒）。
    # limit: 每次请求的数据量限制。
    # pause_every: 每隔多少批次暂停一次。
    # pause: 暂停时长（秒）。
    timedelta = int(pd.Timedelta(timeframe).to_timedelta64()/1E6)
    tasks = []
    results = []
    for step_since in range(since, until, limit * timedelta):
        tasks.append(
            asyncio.create_task(_ohlcv(exchange, symbol, timeframe, limit, step_since, timedelta))
        )
        if len(tasks) >= pause_every:
            results.extend(await asyncio.gather(*tasks))
            await asyncio.sleep(pause)
            tasks = []
    if len(tasks) > 0 :
        results.extend(await asyncio.gather(*tasks))
    final_df = pd.concat(results, ignore_index= True)
    final_df = final_df.loc[(since < final_df["timestamp_open"]) & (final_df["timestamp_open"] < until), :]
    del final_df["timestamp_open"]
    final_df.set_index('date_open', drop=True, inplace=True)
    final_df.sort_index(inplace= True)
    final_df.dropna(inplace=True)
    final_df.drop_duplicates(inplace=True)
    return final_df

async def _download_symbols(exchange_name, symbols, dir, timeframe,  **kwargs):
    # 异步下载多个交易对的历史数据。
    # exchange_name: 交易所名称。
    # symbols: 交易对列表。
    # dir: 保存数据的目录。
    # timeframe: 时间周期。
    # kwargs: 其他参数，如limit, pause_every, pause, since, until。
    exchange = getattr(ccxt, exchange_name)({ 'enableRateLimit': True })
    for symbol in symbols:
        df = await _download_symbol(exchange = exchange, symbol = symbol, timeframe= timeframe, **kwargs)
        save_file = f"{dir}/{exchange_name}-{symbol.replace('/', '')}-{timeframe}.pkl"
        print(f"{symbol} downloaded from {exchange_name} and stored at {save_file}")
        df.to_pickle(save_file)
    await exchange.close()

async def _download(exchange_names, symbols, timeframe, dir, since : datetime.datetime, until : datetime.datetime = datetime.datetime.now()):
    # 异步下载指定交易所和交易对的历史数据。
    # exchange_names: 交易所名称列表。
    # symbols: 交易对列表。
    # timeframe: 时间周期。
    # dir: 保存数据的目录。
    # since: 开始日期时间。
    # until: 结束日期时间。
    tasks = []
    for exchange_name in exchange_names:
        
        limit = EXCHANGE_LIMIT_RATES[exchange_name]["limit"]
        pause_every = EXCHANGE_LIMIT_RATES[exchange_name]["pause_every"]
        pause = EXCHANGE_LIMIT_RATES[exchange_name]["pause"]
        tasks.append(
            _download_symbols(
                exchange_name = exchange_name, symbols= symbols, timeframe= timeframe, dir = dir,
                limit = limit, pause_every = pause_every, pause = pause,
                since = int(since.timestamp()*1E3), until = int(until.timestamp()*1E3)
            )
        )
    await asyncio.gather(*tasks)
def download(*args, **kwargs):
    # 同步下载接口，内部调用异步下载函数。
    # args, kwargs: 传递给_download函数的参数。
    # loop = asyncio.get_event_loop()
    asyncio.run(
        _download(*args, **kwargs)
    )

async def main():
    # 主函数，用于示例下载数据。
    await _download(
        ["binance", "bitfinex2", "huobi"],
        symbols= ["BTC/USDT", "ETH/USDT"],
        timeframe= "30m",
        dir = "test/data",
        since= datetime.datetime(year= 2019, month= 1, day=1),
    )



if __name__ == "__main__":
    # 当脚本直接运行时执行主函数。
    asyncio.run(main())
