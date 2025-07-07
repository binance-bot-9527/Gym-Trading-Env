多数据集环境
============

现在，你已经知道如何为你的强化学习代理创建一个单数据集环境。但有些地方似乎不对劲……一个好的数据集大约有 10 万个数据点。但这与强化学习代理需要数百万步才能表现良好相比，听起来非常少。

**单个数据集足以让代理学到真东西吗？**

在我看来，一个数据集是不够的。代理会过拟合，无法泛化。我的解决方案很简单，就是为环境添加多个数据集。我向你介绍 *MultiDatasetTradingEnv*。

多数据集交易环境
-----------------

  （继承自 TradingEnv）
  
一个处理多个数据集的 TradingEnv 环境。它会在每个回合结束时自动从一个数据集切换到另一个数据集。通过拥有多个数据集（即使是来自不同交易所的相同交易对），带来多样性是一个好主意。这应该有助于避免过拟合。

如何使用？
^^^^^^^^^^^^

你需要指定一个 `glob 路径 <https://docs.python.org/3.6/library/glob.html>`_ 来收集所有数据集（.pkl 格式）。
假设你有一个名为 ``preprocessed_data`` 的文件夹，其中包含多个预处理过的数据集。

.. code-block:: python
  
  import gymnasium as gym
  import gym_trading_env
  env = gym.make('MultiDatasetTradingEnv',
      dataset_dir = 'preprocessed_data/*.pkl',
  )

.. note::
  
    **如果你这样做，你需要确保所有数据集都满足要求**：它们需要按日期升序排列。索引必须是 DatetimeIndex。你的 DataFrame 需要包含一个名为 ``close`` 的收盘价列才能运行环境。并且需要包含名为 ``open``、``high``、``low``、``volume`` 的开盘价、最高价、最低价、成交量列才能进行渲染。你的代理所需的输入观测值需要在列名中包含 ``feature``）。


轻松预处理
^^^^^^^^^^^^^^^

为了避免每次需要更改特征或其他更改时都重新预处理和保存所有数据集，我为 MultiDatasetTradingEnv 添加了一个 ``preprocess`` 参数。此函数接受一个 pandas.DataFrame 并返回一个 pandas.DataFrame。此函数在每个数据集用于环境之前都会被应用。

假设你有一个名为 ``raw_data`` 的文件夹，其中包含多个原始数据集。

.. code-block:: python

  def preprocess(df : pd.DataFrame):
    # 预处理
    df["date"] = pd.to_datetime(df["timestamp"], unit= "ms")
    df.set_index("date", inplace = True)
    
    # 创建你的特征
    df["feature_close"] = df["close"].pct_change()
    df["feature_open"] = df["open"]/df["close"]
    df["feature_high"] = df["high"]/df["close"]
    df["feature_low"] = df["low"]/df["close"]
    df["feature_volume"] = df["volume"] / df["volume"].rolling(7*24).max()
    df.dropna(inplace= True)
    return df
   
  env = gym.make(
          "MultiDatasetTradingEnv",
          dataset_dir= 'raw_data/*.pkl',
          preprocess= preprocess,
      )
 
`MultiDatasetTradingEnv 文档 <https://gym-trading-env.readthedocs.io/en/latest/documentation.html#gym_trading_env.environments.TradingEnv>`_ 

运行环境
^^^^^^^^^^^^^^^

.. code-block:: python
  
  # 运行 100 个回合
  for _ in range(100): 
    # 在每个回合中，环境都会选择一个新的数据集。
    done, truncated = False, False
    observation, info = env.reset()
    while not done and not truncated:
        position_index = env.action_space.sample() # 选择随机仓位索引
        observation, reward, done, truncated, info = env.step(position_index)

.. note::
  
  运行环境的代码与 ``TradingEnv`` 没有变化

