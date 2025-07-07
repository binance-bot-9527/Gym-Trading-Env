import sys  
sys.path.append("./src")


from gym_trading_env.downloader import download, EXCHANGE_LIMIT_RATES
import datetime

EXCHANGE_LIMIT_RATES["bybit"] = {
    "limit":200, # 单次请求将查询1000个数据点（即K线图）
    "pause_every": 120, # 每10次请求暂停
    "pause" : 2, # 暂停持续1秒
}
download(
    exchange_names = ["bybit"],
    symbols= ["BTC/USDT", "ETH/USDT"],
    timeframe= "1h",
    dir = "examples/data",
    since= datetime.datetime(year= 2023, month= 1, day=1),
)