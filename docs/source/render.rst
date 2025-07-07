渲染
====



.. note::

  渲染器在本地主机上作为 Web 应用程序运行，使用 ``Flask``，图表则通过 ``pyecharts`` 库绘制。




首次渲染
---------

为了不干扰训练，渲染需要在单独的 Python 脚本中执行。这样你就可以在不干扰强化学习代理训练的情况下，探索你的回合结果。

在*运行环境脚本*中，你需要保存渲染日志：

.. code-block:: python

  # 在你想要渲染的回合结束时
  env.save_for_render(dir = "render_logs")

然后，在*单独的脚本*中：

.. code-block:: python

  from gym_trading_env.renderer import Renderer
  renderer = Renderer(render_logs_dir="render_logs")
  renderer.run()

.. code-block:: bash

  ...
  * Running on http://127.0.0.1:5000
  ...

访问 Flask 提到的 URL（这里是 `http://127.0.0.1:5000 <http://127.0.0.1:5000>`_）
 
.. image:: images/render.gif
  :alt: 替代文本

自定义渲染
-----------

添加自定义线条
^^^^^^^^^^^^^^^^

.. code-block:: python
  
  renderer = Renderer(render_logs_dir="render_logs")
  
  # 添加自定义线条（简单移动平均线）
  renderer.add_line( name= "sma10", function= lambda df : df["close"].rolling(10).mean(), line_options ={"width" : 1, "color": "purple"})
  renderer.add_line( name= "sma20", function= lambda df : df["close"].rolling(20).mean(), line_options ={"width" : 1, "color": "blue"})
  
  renderer.run()

.. image:: images/custom_lines.PNG
  :width: 600
  :alt: 替代文本

使用 ``.add_line(name, function, line_options)`` 添加自定义线条，该函数接受以下参数：

* ``name``：线条的名称。
* ``function``：该函数接受 `历史对象 <https://gym-trading-env.readthedocs.io/en/latest/history.html>`_（在渲染时性能不再重要，因此转换为 DataFrame）作为参数，需要返回一个 Series、一维数组或与 DataFrame 长度相同的列表。
* ``line_options`` *(可选)*：一个 Dict 对象，可以包含 ``color`` (str) 和 ``width`` (int) 键来控制绘图的外观。



添加自定义指标
^^^^^^^^^^^^^^^^

.. code-block:: python
  
  renderer = Renderer(render_logs_dir="render_logs")

  # 添加自定义指标（年化指标）
  renderer.add_metric(
      name = "Annual Market Return",
      function = lambda df : f"{ ((df['close'].iloc[-1] / df['close'].iloc[0])**(pd.Timedelta(days=365)/(df.index.values[-1] - df.index.values[0]))-1)*100:0.2f}%"
  )
  renderer.add_metric(
          name = "Annual Portfolio Return",
          function = lambda df : f"{((df['portfolio_valuation'].iloc[-1] / df['portfolio_valuation'].iloc[0])**(pd.Timedelta(days=365)/(df.index.values[-1] - df.index.values[0]))-1)*100:0.2f}%"
  )

  renderer.run()

.. image:: images/custom_metrics.PNG
  :width: 300
  :alt: 替代文本

使用 ``.add_metric(name, function)`` 添加自定义指标，该函数接受以下参数：

* ``name``：指标的名称。
* ``function``：该函数接受历史对象（转换为 DataFrame）作为参数，需要返回一个字符串。
