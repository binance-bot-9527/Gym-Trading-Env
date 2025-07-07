环境快速概述
=============

.. image:: images/render.gif
  :width: 600
  :align: center
  
  
该环境是一个 `Gymnasium <https://gymnasium.farama.org/content/basic_usage/>`_ 环境，设计用于单一交易对的交易。

.. list-table::
   :widths: 25 70
   :header-rows: 0
   
   * - 动作空间
     - ``Discrete(number_of_positions)``
   * - 观测空间
     - ``Box(-np.inf, +np.inf, shape=...)``
   * - 导入
     - ``gymnasium.make("TradingEnv", df=df)``

重要参数
--------

* ``df`` *(必需)*：一个 pandas.DataFrame，索引为 DatetimeIndex，且包含 ``close`` 列。若要执行渲染，DataFrame 还需包含 ``open``、``low`` 和 ``high`` 列。
* ``positions`` *(可选，默认值：[-1, 0, 1])*：代理可采取的仓位列表。每个仓位由一个数字表示（详见*动作空间*部分）。

`所有参数文档 <https://gym-trading-env.readthedocs.io/en/latest/documentation.html#gym_trading_env.environments.TradingEnv>`_

动作空间
--------

动作空间是用户提供的**仓位**列表。每个仓位从 -∞ 到 +∞ 标记，表示投资组合估值中投入该仓位的比例（> 0 表示看涨，< 0 表示看跌）。


.. list-table:: 以 BTC/USDT 交易对为例（%pv 表示*投资组合估值百分比*）
   :widths: 5 5 5 5 5
   :header-rows: 1
   
   * - 仓位示例
     - BTC (%pv)
     - USDT (%pv)
     - 借入的 BTC (%pv)
     - 借入的 USDT (%pv)
   * - **0**
     -  
     - 100
     -  
     -  
   * - **1**
     - 100
     -  
     -  
     -  
   * - **0.5**
     - 50
     - 50
     - 
     - 
   * - **2**
     - 200
     -  
     -  
     - 100
   * - **-1**
     -  
     - 200
     - 100
     -  
     
如果 ``position < 0``：环境执行做空操作（通过借入 USDT 并用其买入 BTC）。

如果 ``position > 1``：环境执行保证金交易（通过借入 BTC 并卖出以获得 USDT）。

观测空间
--------

观测空间是一个 np.array，包含：

* DataFrame 中列名包含 ``feature`` 的行：**静态特征**
* **动态特征**（默认包括代理上一步采取的仓位和当前真实仓位）。

.. code-block:: python

  >>> df["feature_pct_change"] = df["close"].pct_change()
  >>> df["feature_high"] = df["high"] / df["close"] - 1
  >>> df["feature_low"] = df["low"] / df["close"] - 1
  >>> df.dropna(inplace= True)
  >>> env = gymnasium.make("TradingEnv", df = df, positions = [-1, 0, 1], initial_position= 1)
  >>> observation, info = env.reset()
  >>> observation
  array([-2.2766300e-04,  1.0030895e+00,  9.9795288e-01,  1.0000000e+00], dtype=float32)

如果 ``windows`` 参数设置为整数 W > 1，则观测为最近 W 个状态的堆叠。

.. code-block:: python
  
  >>> env = gymnasium.make("TradingEnv", df = df, positions = [-1, 0, 1], initial_position= 1, windows = 3)
  >>> observation, info = env.reset()
  >>> observation
  array([[-0.00231082,  1.0052915 ,  0.9991996 ,  1.        ],
         [ 0.01005705,  1.0078559 ,  0.98854125,  1.        ],
         [-0.00408145,  1.0069852 ,  0.99777853,  1.        ]],
         dtype=float32)

奖励
----

奖励由公式 :math:`r_{t} = ln(\frac{p_{t}}{p_{t-1}})\text{，其中 }p_{t}\text{ 是时间步 }t\text{ 的投资组合估值}` 给出。强烈建议根据需要 `自定义奖励函数 <https://gym-trading-env.readthedocs.io/en/latest/customization.html#custom-reward-function>`_。

起始状态
--------

环境遍历给定的 DataFrame 并从其开始处启动。

回合终止
--------

回合在以下情况下结束：

1 - 环境达到 DataFrame 末尾，返回 ``truncated`` 为 ``True``
2 - 投资组合估值降至 0（或以下），返回 ``done`` 为 ``True``。这可能发生在采取保证金仓位（>1 或 <0）时。

参数
----

.. autoclass:: gym_trading_env.environments.TradingEnv
