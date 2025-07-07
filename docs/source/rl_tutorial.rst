教程
========

欢迎使用 Gym Trading Env 包的第一个教程。您将学习如何使用它。

.. note:: 

  在整个教程中，我们将以 BTC/USD 交易对为例。


理解动作空间
---------------------------

仓位
^^^^^^^^^

我见过许多环境将动作视为买入(BUY)、卖出(SELL)。根据我的经验，以与交易者相同的方式考虑强化学习代理是一个错误。因为在交易背后，真正重要的是：**达到的仓位**。在环境中，我们用数字标记每个仓位：
*(以BTC/USD交易对为例)*

* ``1``：将全部投资组合转换为BTC **(=全部买入)**
* ``0``：将全部投资组合转换为USD **(=全部卖出)**

*现在，我们可以想象半仓和其他变体：*

* ``0.5``：50% BTC & 50% USD
* 甚至 ``0.1``：10% BTC & 90% USD ....

.. note::

  对于强化学习代理来说，使用仓位进行操作要简单得多。这样，它可以通过简单的动作空间轻松执行复杂的操作。

复杂仓位
^^^^^^^^^^^^^^^^^

此环境支持更复杂的仓位（实际上是任何从负无穷到正无穷的浮点数），例如：

* ``-1``：将投资组合价值的100%押注在BTC下跌上（=做空）。为了执行此操作，环境会向一个假想的人借入100%的投资组合估值作为BTC，并立即将其出售以获得USD。当代理想要平仓时，环境会买回所欠的BTC数量并偿还给假想的人。如果在此操作期间价格下跌，我们买入的价格会比最初卖出的价格便宜：差额就是我们的收益。在借贷期间，假想的人会获得少量租金（环境参数：``borrow_interest_rate``）。
* ``+2``：将投资组合价值的100%押注在BTC上涨上。我们使用与上述相同的机制，但我们借入USD并用它购买BTC。

.. note::

  我们可以使用 ``-10`` 吗？
  可以，但是...我们需要借入投资组合估值的1000%作为BTC。您需要了解，这种“杠杆”非常危险。事实上，如果BTC价格上涨10%，您需要以当前投资组合估值的1100%（1000%*1.10）来偿还最初1000%的投资组合估值。那么，您投资组合的100%（1100% - 1000%）将用于偿还债务。游戏结束，您将一无所有。杠杆非常有用但也非常危险，因为它会增加您的收益和损失。请始终记住，您可能会失去一切。


市场数据
-----------

导入您自己的数据集
^^^^^^^^^^^^^^^^^^^^^^^

它们需要按日期升序排列。索引必须是 DatetimeIndex。您的 DataFrame 需要包含一个名为 ``close`` 的收盘价，以便环境运行；以及分别名为 ``open``、``high``、``low``、``volume`` 的开盘价、最高价、最低价和成交量特征，以便进行渲染。

.. code-block:: python

  import pandas as pd
  # 可在 GitHub 仓库中找到：examples/data/BTC_USD-Hourly.csv
  url = "https://raw.githubusercontent.com/ClementPerroud/Gym-Trading-Env/main/examples/data/BTC_USD-Hourly.csv"
  df = pd.read_csv(url, parse_dates=["date"], index_col= "date")
  df.sort_index(inplace= True)
  df.dropna(inplace= True)
  df.drop_duplicates(inplace=True)

  
轻松下载加密货币数据
^^^^^^^^^^^^^^^^^^^^^^^^
该软件包还提供了一种轻松下载加密货币交易对历史数据的方法。它将数据存储为 `.pkl` 格式，以便快速使用。

`更多信息请点击此处 <https://gym-trading-env.readthedocs.io/en/latest/download.html>`_

.. code-block:: python

  from gym_trading_env.downloader import download
  import datetime
  import pandas as pd
  
  # 下载币安 BTC/USDT 历史数据并将其存储到目录 ./data/binance-BTCUSDT-1h.pkl
  download(exchange_names = ["binance"],
      symbols= ["BTC/USDT"],
      timeframe= "1h",
      dir = "data",
      since= datetime.datetime(year= 2020, month= 1, day=1),
  )
  # 导入您的新数据
  df = pd.read_pickle("./data/binance-BTCUSDT-1h.pkl")


创建您的特征
--------------------

您的强化学习代理将需要输入。确保它拥有所需的一切是您的职责。

.. important::

  环境将识别名称中包含关键字“**feature**”的每一列作为输入。


.. code-block:: python

  # df 是一个包含列的 DataFrame："open", "high", "low", "close", "Volume USD"
  
  # 创建特征：( close[t] - close[t-1] )/ close[t-1]
  df["feature_close"] = df["close"].pct_change() 
  
  # 创建特征：open[t] / close[t]
  df["feature_open"] = df["open"]/df["close"]
  
  # 创建特征：high[t] / close[t]
  df["feature_high"] = df["high"]/df["close"]
  
  # 创建特征：low[t] / close[t]
  df["feature_low"] = df["low"]/df["close"]
  
   # 创建特征：volume[t] / max(*volume[t-7*24:t+1])
  df["feature_volume"] = df["Volume USD"] / df["Volume USD"].rolling(7*24).max()
  
  df.dropna(inplace= True) # 再次清理！
  # 每一步，环境将返回 5 个输入：“feature_close”, “feature_open”, “feature_high”, “feature_low”, “feature_volume”



.. note::

  上面介绍的是称为**静态特征**的特征。实际上，它们在环境中被使用之前只计算一次。但您也可以使用**动态特征**，它们在环境的每一步都会计算。默认情况下，环境会添加 2 个动态特征。更多信息请参见**特征**页面。
 
 
创建您的第一个环境
-----------------------------

做得好，您已经很好地配置了您的第一个环境！

.. code-block:: python

  import gymnasium as gym
  import gym_trading_env
  env = gym.make("TradingEnv",
          name= "BTCUSD",
          df = df, # 您的数据集，包含您的自定义特征
          positions = [ -1, 0, 1], # -1 (=做空), 0(=空仓), +1 (=做多)
          trading_fees = 0.01/100, # 每笔股票买入/卖出收取 0.01% 的费用（币安费用）
          borrow_interest_rate= 0.0003/100, # 每时间步 0.0003%（此处一个时间步 = 1 小时）
      )

`TradingEnv 文档 <https://gym-trading-env.readthedocs.io/en/latest/documentation.html#gym_trading_env.environments.TradingEnv>`_

运行环境
-------------------

现在是享受的时候了。

.. code-block:: python
 
  # 运行一个回合直到结束：
  done, truncated = False, False
  observation, info = env.reset()
  while not done and not truncated:
      # 从您的仓位列表中（=[-1, 0, 1]）选择一个仓位索引……通常类似于：position_index = your_policy(observation)
      position_index = env.action_space.sample() # 在每个时间步，从您的仓位列表中（=[-1, 0, 1]）随机选择一个仓位索引
      observation, reward, done, truncated, info = env.step(position_index)
 
.. code-block:: bash

  市场回报率：423.10%   |   投资组合回报率：-98.28%

每个回合都会生成一个包含基本指标的输出，您可以自定义这些指标。`有关如何自定义环境的更多信息，请点击此处 <https://gym-trading-env.readthedocs.io/en/latest/customization.html#>`_

想要一个酷炫的渲染效果吗？`有关如何渲染已完成回合的更多信息，请点击此处 <https://gym-trading-env.readthedocs.io/en/latest/render.html>`_

  
