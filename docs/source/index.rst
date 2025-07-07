.. meta::
   :description: A simple, easy, customizable Gymnasium environment for trading and easy Reinforcement Learning implementation.




|Gym Trading Environment|
============================

.. |Gym Trading Environment| raw:: html

      <img src = 'https://github.com/ClementPerroud/Gym-Trading-Env/raw/main/docs/source/images/logo_light-bg.png' width='500' alt = "Gym Trading Environment" style = "display:block;margin:auto">

 
.. raw:: html

   <section class="shields" align="center">
      <a href="https://www.python.org/">
         <img src="https://img.shields.io/badge/python-v3-brightgreen.svg"
            alt="python">
      </a>
      <a href="https://pypi.org/project/gym-trading-env/">
         <img src="https://img.shields.io/badge/pypi-v1.1.3-brightgreen.svg"
            alt="PyPI">
      </a>
      <a href="https://github.com/ClementPerroud/Gym-Trading-Env/blob/main/LICENSE.txt">
      <img src="https://img.shields.io/badge/license-MIT%202.0%20Clause-green"
            alt="Apache 2.0 with Commons Clause">
      </a>
      <a href='https://gym-trading-env.readthedocs.io/en/latest/?badge=latest'>
          <img src='https://readthedocs.org/projects/gym-trading-env/badge/?version=latest' alt='Documentation Status' />
      </a>
      <a href = 'https://pepy.tech/project/gym-trading-env'>
         <img src = 'https://static.pepy.tech/badge/gym-trading-env'>
      </a>
      <br>
      <a href="https://github.com/ClementPerroud/Gym-Trading-Env">
         <img src="https://img.shields.io/github/stars/ClementPerroud/gym-trading-env?style=social" alt="Github stars">
      </a>
   </section>
  
Gym Trading Env 是一个用于模拟股票交易和训练强化学习（RL）交易代理的 Gymnasium 环境。
它的设计目标是快速且可定制，便于实现 RL 交易算法。

+----------------------------------------------------------------+
| `Github <https://github.com/ClementPerroud/Gym-Trading-Env>`_  |
+----------------------------------------------------------------+

主要特性
--------

本包旨在通过提供以下功能大大简化研究阶段：

* 在多个交易所轻松快速下载技术数据
* 为用户和 AI 提供简单快速的环境，同时支持复杂操作（做空、保证金交易）
* 高性能渲染（可同时显示数十万根蜡烛图），可定制以可视化代理的行为及其结果
* （即将推出）一种简单的方式来回测任何 RL 代理或其他类型的代理

.. image:: images/render.gif

安装
----

Gym Trading Env 支持 Windows、Mac 和 Linux 上的 Python 3.9+。你可以使用 pip 安装：

.. code-block:: console

   pip install gym-trading-env

或者使用 git：

.. code-block:: console
   
   git clone https://github.com/ClementPerroud/Gym-Trading-Env

   
目录
----

.. toctree::
   
   简介 <self>
   getting_started
   environment_desc

.. toctree::
   :caption: 🤖 强化学习
   
   rl_tutorial
   customization
   features
   multi_datasets
   vectorize_env

.. toctree:: 
   :caption: 🦾 功能
   
   render
   download
 
.. toctree::
   :caption: 📚 参考
   
   history
   documentation
