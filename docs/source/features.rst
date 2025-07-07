特征
====

如教程中所示，我们可以轻松创建将在每个时间步作为观测返回的特征。
这种特征称为**静态特征**，因为它只在 DataFrame 处理开始时计算一次。

.. hint::

    **但如果你想使用无法预先计算的特征怎么办？**

这种情况下，你将使用**动态特征**，它将在每个步骤计算。

创建静态特征
----------

.. code-block:: python

  # df 是包含列："open"、"high"、"low"、"close"、"Volume USD" 的 DataFrame
  
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
  # 每个步骤，环境将返回5个静态输入："feature_close"、"feature_open"、"feature_high"、"feature_low"、"feature_volume"

  env = gym.make('TradingEnv',
    df = df,
    ....
  )


.. important::

  环境会识别所有列名中包含关键字 '**feature**' 的列作为输入。

创建动态特征
----------

**动态特征**在每个步骤计算。注意，动态特征在计算时间上*远不如*静态特征高效。

.. important::

    下面展示的动态特征是环境默认使用的动态特征！

.. code-block:: python

    def dynamic_feature_last_position_taken(history):
        return history['position', -1]

    def dynamic_feature_real_position(history):
        return history['real_position', -1]
  
    env = gym.make(
        "TradingEnv",
        df = df,
        dynamic_feature_functions = [dynamic_feature_last_position_taken, dynamic_feature_real_position],
        ...
    )

在每个步骤，环境会计算并将这两个特征添加到*观测*的末尾。


