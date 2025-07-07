import sys  
sys.path.append("./src")

import pandas as pd
import numpy as np
import time
from gym_trading_env.environments import TradingEnv
import gymnasium as gym

# 导入你的数据
df = pd.read_csv("examples/data/BTC_USD-Hourly.csv", parse_dates=["date"], index_col= "date")
df.sort_index(inplace= True)
df.dropna(inplace= True)
df.drop_duplicates(inplace=True)

# 生成特征
# 警告：列名需要包含关键字 'feature'！
df["feature_close"] = df["close"].pct_change()
df["feature_open"] = df["open"]/df["close"]
df["feature_high"] = df["high"]/df["close"]
df["feature_low"] = df["low"]/df["close"]
df["feature_volume"] = df["Volume USD"] / df["Volume USD"].rolling(7*24).max()
df.dropna(inplace= True)


# 使用历史对象创建你自己的奖励函数
def reward_function(history):
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2]) #log (p_t / p_t-1 )

env = gym.make(
        "TradingEnv",
        name= "BTCUSD",
        df = df,
        windows= 5,
        positions = [ -1, -0.5, 0, 0.5, 1, 1.5, 2], # 从 -1（=做空）到 +1（=做多）
        initial_position = 'random', # 初始头寸
        trading_fees = 0.01/100, # 每笔股票买卖收取0.01%的交易费
        borrow_interest_rate= 0.0003/100, # 每个时间步（此处为1小时）的借贷利率
        reward_function = reward_function,
        portfolio_initial_value = 1000, # 投资组合初始价值（此处为美元）
        max_episode_duration = 500,
        disable_env_checker= True
    )

env.add_metric('Position Changes', lambda history : np.sum(np.diff(history['position']) != 0) )
env.add_metric('Episode Lenght', lambda history : len(history['position']) )

done, truncated = False, False
observation, info = env.reset()
print(info)
while not done and not truncated:
    action = env.action_space.sample()
    observation, reward, done, truncated, info = env.step(action)
    print(observation)
# 保存以供渲染
# env.save_for_render()