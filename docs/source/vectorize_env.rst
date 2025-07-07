向量化您的环境
==================

Gym 向量化
----------

**您仍然希望您的代理表现更好吗？**

那么，我建议使用向量化环境来并行化多个环境。它保证在训练期间拥有多个同步数据源。

.. code-block:: python

  import gymnasium as gym
  import gym_trading_env
  
  if __name__ == "__main__":
    envs = gym.vector.make(
      "MultiDatasetTradingEnv",
      dataset_dir = "preprocessed_data",
      num_envs = 3)
    print(envs.reset())

.. code-block:: python

  (array([[4.1329634e-04, 9.9952787e-01, 1.0001770e+00, 9.9935079e-01,
        2.4035616e-02, 0.0000000e+00],
       [4.2866479e-04, 9.9957150e-01, 1.0002638e+00, 9.9926108e-01,
        1.8846054e-01, 0.0000000e+00],
       [7.6002884e-04, 9.9924058e-01, 1.0001662e+00, 9.9836242e-01,
        7.7975184e-02, 0.0000000e+00]], dtype=float32), {'step': array([0, 0, 0]), '_step': array([ True,  True,  True]), 'date': array([numpy.datetime64('2023-01-07T23:00:00.000000000'),
       numpy.datetime64('2023-01-07T23:00:00.000000000'),
       numpy.datetime64('2023-01-07T23:00:00.000000000')], dtype=object), '_date': array([ True,  True,  True]), 'position_index': array([0, 0, 0]), '_position_index': array([ True,  True,  True]), 'position': array([0, 0, 0]), '_position': array([ True,  True,  True]), 'data_open': array([16936.  , 16936.31,  1263.11]), '_data_open': array([ True,  True,  True]), 'data_volume': array([2.88336096e+00, 3.60376360e+03, 5.95961140e+03]), '_data_volume': array([ True,  True,  True]), 'data_date_close': array([Timestamp('2023-01-08 00:00:00'), Timestamp('2023-01-08 00:00:00'),
       Timestamp('2023-01-08 00:00:00')], dtype=object), '_data_date_close': array([ True,  True,  True]), 'data_low': array([16933.  , 16931.05,  1262.  ]), '_data_low': array([ True,  True,  True]), 'data_close': array([16944.  , 16943.57,  1264.07]), '_data_close': array([ True,  True,  True]), 'data_high': array([16947.  , 16948.04,  1264.28]), '_data_high': array([ True,  True,  True]), 'portfolio_valuation': array([1000., 1000., 1000.]), '_portfolio_valuation': array([ True,  True,  True]), 'portfolio_distribution_asset': array([0, 0, 0]), '_portfolio_distribution_asset': array([ True,  True,  True]), 'portfolio_distribution_fiat': array([1000., 1000., 1000.]), '_portfolio_distribution_fiat': array([ True,  True,  True]), 'portfolio_distribution_borrowed_asset': array([0, 0, 0]), '_portfolio_distribution_borrowed_asset': array([ True,  True,  True]), 'portfolio_distribution_borrowed_fiat': array([0, 0, 0]), '_portfolio_distribution_borrowed_fiat': array([ True,  True,  True]), 'portfolio_distribution_interest_asset': array([0, 0, 0]), '_portfolio_distribution_interest_asset': array([ True,  True,  True]), 'portfolio_distribution_interest_fiat': array([0, 0, 0]), '_portfolio_distribution_interest_fiat': array([ True,  True,  True]), 'reward': array([0, 0, 0]), '_reward': array([ True,  True,  True])})
  
.. note::

  建议使用 ``if __name__ == "__main__":``，否则可能会遇到错误。

特殊情况
-------------

在某些情况下（Jupyter Notebooks），您可能需要使用 gym 中的 ``SyncVectorEnv`` 对象来避免崩溃：

.. code-block:: python

  import gymnasium as gym
  import gym_trading_env
  
  def make_env():
    env = gym.make(
        "MultiDatasetTradingEnv",
        dataset_dir= "preprocessed_data",
    )
    return env
  envs = gym.vector.SyncVectorEnv([lambda: make_env() for _ in range(3)])

运行环境
--------------------

.. code-block:: python
      
      observation, info = env.reset()
      while True:
        actions = [0, 0, 0] # 3D 列表，因为我们有 3 个同时存在的环境
        observation, reward, done, truncated, info = env.step(actions)
