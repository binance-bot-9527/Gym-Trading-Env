自定义
=====

自定义奖励函数
------------

使用 `History 对象 <https://gym-trading-env.readthedocs.io/en/latest/history.html>`_ 来创建你的自定义奖励函数。下面是一个非常基础的奖励函数示例：数学表达式 :math:`r_{t} = ln(\frac{p_{t}}{p_{t-1}})\text{，其中 }p_{t}\text{ 是时间步 }t\text{ 的投资组合估值}`（这是默认的奖励函数）。

.. code-block:: python

 import gymnasium as gym
 import numpy as np
 def reward_function(history):
         return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2])
 
 env = gym.make("TradingEnv",
         ...
         reward_function = reward_function
         ...
     )

自定义日志
---------

使用 `History 对象 <https://gym-trading-env.readthedocs.io/en/latest/history.html>`_ 来添加自定义日志。如果你的交易环境的 ``verbose`` 参数设置为 ``1`` 或 ``2``，环境会显示你的回合的快速摘要。默认显示的指标是 `市场收益` 和 `投资组合收益`。

.. code-block:: bash

  市场收益 :  25.30%   |   投资组合收益 : 45.24%

你可以在初始化环境后使用 ``.add_metric(name, function)`` 方法添加自定义指标：

.. code-block:: python
  
  env = gym.make("TradingEnv",
         ...
     )
  env.add_metric('仓位变动次数', lambda history : np.sum(np.diff(history['position']) != 0) )
  env.add_metric('回合长度', lambda history : len(history['position']) )
  # 然后，运行你的回合

.. code-block:: bash

  市场收益 :  25.30%   |   投资组合收益 : 45.24%   |   仓位变动次数 : 28417   |   回合长度 : 33087

``.add_metric`` 方法接受两个参数：

* ``name`` ：指标显示的名称

* ``function`` ：接受 `History 对象 <https://gym-trading-env.readthedocs.io/en/latest/history.html>`_ 作为参数并返回一个值的函数（建议返回字符串以避免错误）。

.. note::

 如果你想使用这些指标来驱动自定义日志器、可视化数据或跟踪性能，可以在**回合结束时**通过 ``env.get_metrics()`` 访问结果。此时返回：
 
 .. code-block:: python
 
  { "市场收益" :  "25.30%", "投资组合收益" : "45.24%", "仓位变动次数" : 28417, "回合长度" : 33087 }

 

.. note::

  如果你想使用这些指标来驱动自定义日志器、可视化数据或跟踪性能，可以在**回合结束时**通过 ``env.get_metrics()`` 访问结果。此时返回：

 .. code-block:: python
 
  { "市场收益" :  "25.30%", "投资组合收益" : "45.24%", "仓位变动次数" : 28417, "回合长度" : 33087 }
 
