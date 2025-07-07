历史对象
========

历史对象类似于 DataFrame，但设计得更快。它在训练的每个时间步存储大量训练信息。你可以这样使用它：

* ``history['列名', t]`` 返回时间步 t 对应指标“列名”的标量值。
* ``history['列名']`` 返回从时间步 0 到当前时间步的所有值的 numpy 数组。
* ``history[t]`` 返回一个字典，键为指标名，值为对应的值。

它的设计目的是简化操作：

* 你可以访问 **训练信息**，如：``step``、``date``、``reward``、``position`` 等。
* 它收集了 **初始 DataFrame 的信息**，并用 ``data_{列名}`` 标记，如：``data_close``、``data_open``、``data_high`` 等。
* 它存储了 **投资组合估值和分布**。

.. code-block:: python

 >>> history[33091]
  {
   # 训练信息
   'step': 33091, # 步数 = t。
   'date': numpy.datetime64('2022-03-01T00:00:00.000000000'), # 时间步 t 的日期，datetime 类型。
   'position_index': 2, # 时间步 t 在仓位列表中的索引。
   'position': 1, # 代理最后采取的仓位。
   'real_position': 1.09848, # 真实投资组合仓位 = (持有资产 - 借入资产 - 利息) * 当前价格 / 投资组合估值
   'reward': 0.0028838985262525257, # 时间步 t 的奖励。显然，不能在自定义奖励函数中使用（因为尚未计算，值始终为0）。
   
   # DataFrame 信息：初始 DataFrame 中除特征外的每列，前缀为 'data_'
   'data_symbol': 'BTC/USD', 
   'data_volume': 52.05632, 
   'data_Volume USD': 2254677.3870464, 
   'data_high': 43626.49, 
   'data_open': 43221.71, 
   'data_close': 43312.27, 
   'data_unix': 1646092800, 
   'data_low': 43185.48,
   
   # 投资组合信息：投资组合分布
   'portfolio_valuation': 45.3857471834205, # 投资组合总估值
   'portfolio_distribution_asset': 0.001047869568779473, # 持有的 BTC 数量
   'portfolio_distribution_fiat': 0.0001374956603967803, # 持有的 USD 数量
   'portfolio_distribution_borrowed_asset': 0, # 借入的 BTC 数量（当仓位 < 0 即做空时）
   'portfolio_distribution_borrowed_fiat': 0, # 借入的 USD 数量（当仓位 > 1 时）
   'portfolio_distribution_interest_asset': 0.0, # 借入 BTC 产生的累计利息
   'portfolio_distribution_interest_fiat': 0.0, # 借入 USD 产生的累计利息
  }
