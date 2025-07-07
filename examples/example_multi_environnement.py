import sys  
sys.path.append("./src")

import pandas as pd
import numpy as np
import gymnasium as gym
import gym_trading_env

# 警告：请先使用 example_download.py 脚本下载数据！

# 生成特征
# 警告：列名需要包含关键字 'feature'！
def preprocess(df : pd.DataFrame):
    df["feature_close"] = df["close"].pct_change()
    df["feature_open"] = df["open"]/df["close"]
    df["feature_high"] = df["high"]/df["close"]
    df["feature_low"] = df["low"]/df["close"]
    df["feature_volume"] = df["volume"] / df["volume"].rolling(7*24).max()
    df.dropna(inplace= True)
    return df

# 使用历史对象创建你自己的奖励函数
def reward_function(history):
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2]) #log (p_t / p_t-1 )


env = gym.make(
        "MultiDatasetTradingEnv",
        dataset_dir= './examples/data/*.pkl', 
        preprocess= preprocess,
        windows= 5,
        positions = [ -1, -0.5, 0, 0.5, 1, 1.5, 2], # 从 -1（=完全做空）到 +1（=完全做多），0 = 无头寸
        initial_position = 0, # 初始头寸
        trading_fees = 0.01/100, # 每笔股票买卖收取0.01%的交易费
        borrow_interest_rate= 0.0003/100, # 每个时间步（此处为1小时）的借贷利率
        reward_function = reward_function,
        portfolio_initial_value = 1000, # 投资组合初始价值（此处为美元）
        max_episode_duration= 500,
        episodes_between_dataset_switch = 10

    )

# 运行模拟
while True:
    truncated = False
    observation, info = env.reset()
    while not truncated:
        action = env.action_space.sample() # 或者手动输入：action = int(input("Action : ")) 
        observation, reward, done, truncated, info = env.step(action)

# 渲染
# env.save_for_render()