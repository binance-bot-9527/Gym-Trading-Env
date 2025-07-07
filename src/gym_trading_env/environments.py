import gymnasium as gym
from gymnasium import spaces
import pandas as pd
import numpy as np
import datetime
import glob
from pathlib import Path    

from collections import Counter
from .utils.history import History
from .utils.portfolio import Portfolio, TargetPortfolio

import tempfile, os
import warnings
warnings.filterwarnings("error")

def basic_reward_function(history : History):
    # 基本奖励函数：计算投资组合估值的对数收益。
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2])

def dynamic_feature_last_position_taken(history):
    # 动态特征函数：返回上一个时间步的头寸。
    return history['position', -1]

def dynamic_feature_real_position(history):
    # 动态特征函数：返回当前实际头寸。
    return history['real_position', -1]

class TradingEnv(gym.Env):
    # 交易环境类，用于OpenAI Gym。
    # 建议使用以下方式初始化：
    # import gymnasium as gym
    # import gym_trading_env
    # env = gym.make('TradingEnv', ...)
    """
    An easy trading environment for OpenAI gym. It is recommended to use it this way :

    .. code-block:: python

        import gymnasium as gym
        import gym_trading_env
        env = gym.make('TradingEnv', ...)


    :param df: 市场DataFrame。必须包含'open'、'high'、'low'、'close'列。索引必须是DatetimeIndex。您希望作为输入的列名中需要包含'feature'：这样，它们将在每个步骤中作为观察值返回。
    :type df: pandas.DataFrame

    :param positions: 环境允许的头寸列表。
    :type positions: optional - list[int or float]

    :param dynamic_feature_functions: 动态特征函数列表。默认情况下，添加两个动态特征：
    
        * 代理采取的最后一个头寸。
        * 投资组合的实际头寸（根据价格波动而变化）。

    :type dynamic_feature_functions: optional - list   

    :param reward_function: 接受环境的History对象并必须返回一个浮点数。
    :type reward_function: optional - function<History->float>

    :param windows: 默认为None。如果设置为整数N，则每个步骤的观察将返回过去N个观察。推荐用于基于循环神经网络的代理。
    :type windows: optional - None or int

    :param trading_fees: 交易手续费（买入和卖出操作）。例如：0.01对应1%的手续费。
    :type trading_fees: optional - float

    :param borrow_interest_rate: 每步借款利率（仅当头寸<0或头寸>1时）。例如：0.01对应每步1%的借款利率；如果您知道您的借款利率是每天0.05%，并且您的时间步长是1小时，您需要将其除以24 -> 0.05/100/24。
    :type borrow_interest_rate: optional - float

    :param portfolio_initial_value: 投资组合的初始估值。
    :type portfolio_initial_value: float or int

    :param initial_position: 您可以指定环境的初始头寸或将其设置为'random'。它必须包含在'positions'列表参数中。
    :type initial_position: optional - float or int

    :param max_episode_duration: 如果使用整数值，每个episode将在达到所需的最大步长持续时间后被截断（通过返回`truncated`为`True`）。当使用最大持续时间时，每个episode将从一个随机起始点开始。
    :type max_episode_duration: optional - int or 'max'

    :param verbose: 如果为0，不输出日志。如果为1，环境发送episode结果日志。
    :type verbose: optional - int
    
    :param name: 环境的名称（例如：'BTC/USDT'）。
    :type name: optional - str
    
    """
    metadata = {'render_modes': ['logs']}
    def __init__(self,
                # 初始化交易环境。
                df : pd.DataFrame,
                positions : list = [0, 1],
                dynamic_feature_functions = [dynamic_feature_last_position_taken, dynamic_feature_real_position],
                reward_function = basic_reward_function,
                windows = None,
                trading_fees = 0,
                borrow_interest_rate = 0,
                portfolio_initial_value = 1000,
                initial_position ='random',
                max_episode_duration = 'max',
                verbose = 1,
                name = "Stock",
                render_mode= "logs"
                ):
        self.max_episode_duration = max_episode_duration
        self.name = name
        self.verbose = verbose

        self.positions = positions
        self.dynamic_feature_functions = dynamic_feature_functions
        self.reward_function = reward_function
        self.windows = windows
        self.trading_fees = trading_fees
        self.borrow_interest_rate = borrow_interest_rate
        self.portfolio_initial_value = float(portfolio_initial_value)
        self.initial_position = initial_position
        assert self.initial_position in self.positions or self.initial_position == 'random', "'initial_position'参数必须是'random'或'position'参数中提到的头寸（默认为[0, 1]）。"
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.max_episode_duration = max_episode_duration
        self.render_mode = render_mode
        self._set_df(df) # 设置DataFrame并提取特征列。
        
        self.action_space = spaces.Discrete(len(positions)) # 定义动作空间为离散空间，大小为头寸列表的长度。
        self.observation_space = spaces.Box(
            # 定义观察空间为Box空间，范围从-np.inf到np.inf。
            -np.inf,
            np.inf,
            shape = [self._nb_features]
        )
        if self.windows is not None:
            # 如果设置了窗口大小，则调整观察空间以适应窗口。
            self.observation_space = spaces.Box(
                -np.inf,
                np.inf,
                shape = [self.windows, self._nb_features]
            )
        
        self.log_metrics = [] # 用于记录指标的列表。


    def _set_df(self, df):
        # 设置环境的DataFrame。
        # df: 市场数据DataFrame。
        df = df.copy()
        self._features_columns = [col for col in df.columns if "feature" in col]
        self._info_columns = list(set(list(df.columns) + ["close"]) - set(self._features_columns))
        self._nb_features = len(self._features_columns)
        self._nb_static_features = self._nb_features

        for i  in range(len(self.dynamic_feature_functions)):
            df[f"dynamic_feature__{i}"] = 0
            self._features_columns.append(f"dynamic_feature__{i}")
            self._nb_features += 1

        self.df = df
        self._obs_array = np.array(self.df[self._features_columns], dtype= np.float32)
        self._info_array = np.array(self.df[self._info_columns])
        self._price_array = np.array(self.df["close"])


    
    def _get_ticker(self, delta = 0):
        # 获取当前时间步的行情数据。
        # delta: 相对于当前索引的偏移量。
        return self.df.iloc[self._idx + delta]
    def _get_price(self, delta = 0):
        # 获取当前时间步的价格。
        # delta: 相对于当前索引的偏移量。
        return self._price_array[self._idx + delta]
    
    def _get_obs(self):
        # 获取当前观察值。
        # 根据动态特征函数更新观察数组。
        for i, dynamic_feature_function in enumerate(self.dynamic_feature_functions):
            self._obs_array[self._idx, self._nb_static_features + i] = dynamic_feature_function(self.historical_info)

        if self.windows is None:
            _step_index = self._idx
        else: 
            _step_index = np.arange(self._idx + 1 - self.windows , self._idx + 1)
        return self._obs_array[_step_index]

    
    def reset(self, seed = None, options=None, **kwargs):
        # 重置环境到初始状态。
        # seed: 随机种子。
        # options: 其他选项。
        # kwargs: 其他关键字参数。
        super().reset(seed = seed, options = options, **kwargs)
        
        self._step = 0 # 初始化步数为0。
        self._position = np.random.choice(self.positions) if self.initial_position == 'random' else self.initial_position # 设置初始头寸。
        self._limit_orders = {} # 初始化限价订单。
        

        self._idx = 0 # 初始化当前索引为0。
        if self.windows is not None: self._idx = self.windows - 1 # 如果设置了窗口，调整初始索引。
        if self.max_episode_duration != 'max':
            # 如果设置了最大episode持续时间，则随机选择起始索引。
            self._idx = np.random.randint(
                low = self._idx, 
                high = len(self.df) - self.max_episode_duration - self._idx
            )
        
        self._portfolio  = TargetPortfolio(
            # 初始化投资组合。
            position = self._position,
            value = self.portfolio_initial_value,
            price = self._get_price()
        )
        
        self.historical_info = History(max_size= len(self.df)) # 初始化历史信息记录器。
        self.historical_info.set(
            idx = self._idx,
            step = self._step,
            date = self.df.index.values[self._idx],
            position_index =self.positions.index(self._position),
            position = self._position,
            real_position = self._position,
            data =  dict(zip(self._info_columns, self._info_array[self._idx])),
            portfolio_valuation = self.portfolio_initial_value,
            portfolio_distribution = self._portfolio.get_portfolio_distribution(),
            reward = 0, # 初始奖励为0。
        )

        return self._get_obs(), self.historical_info[0] # 返回初始观察值和历史信息。

    def render(self):
        pass

    def _trade(self, position, price = None):
        self._portfolio.trade_to_position(
            position, 
            price = self._get_price() if price is None else price, 
            trading_fees = self.trading_fees
        )
        self._position = position
        return

    def _take_action(self, position):
        if position != self._position:
            self._trade(position)
    
    def _take_action_order_limit(self):
        if len(self._limit_orders) > 0:
            ticker = self._get_ticker()
            for position, params in self._limit_orders.items():
                if position != self._position and params['limit'] <= ticker["high"] and params['limit'] >= ticker["low"]:
                    self._trade(position, price= params['limit'])
                    if not params['persistent']: del self._limit_orders[position]


    
    def add_limit_order(self, position, limit, persistent = False):
        self._limit_orders[position] = {
            'limit' : limit,
            'persistent': persistent
        }
    
    def step(self, position_index = None):
        if position_index is not None: self._take_action(self.positions[position_index])
        self._idx += 1
        self._step += 1

        self._take_action_order_limit()
        price = self._get_price()
        self._portfolio.update_interest(borrow_interest_rate= self.borrow_interest_rate)
        portfolio_value = self._portfolio.valorisation(price)
        portfolio_distribution = self._portfolio.get_portfolio_distribution()

        done, truncated = False, False

        if portfolio_value <= 0:
            done = True
        if self._idx >= len(self.df) - 1:
            truncated = True
        if isinstance(self.max_episode_duration,int) and self._step >= self.max_episode_duration - 1:
            truncated = True

        self.historical_info.add(
            idx = self._idx,
            step = self._step,
            date = self.df.index.values[self._idx],
            position_index =position_index,
            position = self._position,
            real_position = self._portfolio.real_position(price),
            data =  dict(zip(self._info_columns, self._info_array[self._idx])),
            portfolio_valuation = portfolio_value,
            portfolio_distribution = portfolio_distribution, 
            reward = 0
        )
        if not done:
            reward = self.reward_function(self.historical_info)
            self.historical_info["reward", -1] = reward

        if done or truncated:
            self.calculate_metrics()
            self.log()
        return self._get_obs(),  self.historical_info["reward", -1], done, truncated, self.historical_info[-1]

    def add_metric(self, name, function):
        self.log_metrics.append({
            'name': name,
            'function': function
        })
    def calculate_metrics(self):
        self.results_metrics = {
            "Market Return" : f"{100*(self.historical_info['data_close', -1] / self.historical_info['data_close', 0] -1):5.2f}%",
            "Portfolio Return" : f"{100*(self.historical_info['portfolio_valuation', -1] / self.historical_info['portfolio_valuation', 0] -1):5.2f}%",
        }

        for metric in self.log_metrics:
            self.results_metrics[metric['name']] = metric['function'](self.historical_info)
    def get_metrics(self):
        return self.results_metrics
    def log(self):
        if self.verbose > 0:
            text = ""
            for key, value in self.results_metrics.items():
                text += f"{key} : {value}   |   "
            print(text)

    def save_for_render(self, dir = "render_logs"):
        assert "open" in self.df and "high" in self.df and "low" in self.df and "close" in self.df, "Your DataFrame needs to contain columns : open, high, low, close to render !"
        columns = list(set(self.historical_info.columns) - set([f"date_{col}" for col in self._info_columns]))
        history_df = pd.DataFrame(
            self.historical_info[columns], columns= columns
        )
        history_df.set_index("date", inplace= True)
        history_df.sort_index(inplace = True)
        render_df = self.df.join(history_df, how = "inner")
        
        if not os.path.exists(dir):os.makedirs(dir)
        render_df.to_pickle(f"{dir}/{self.name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl")

class MultiDatasetTradingEnv(TradingEnv):
    """
    (Inherits from TradingEnv) A TradingEnv environment that handles multiple datasets.
    It automatically switches from one dataset to another at the end of an episode.
    Bringing diversity by having several datasets, even from the same pair from different exchanges, is a good idea.
    This should help avoiding overfitting.

    It is recommended to use it this way :
    
    .. code-block:: python

        import gymnasium as gym
        import gym_trading_env
        env = gym.make('MultiDatasetTradingEnv',
            dataset_dir = 'data/*.pkl',
            ...
        )
    
    
    
    :param dataset_dir: A `glob path <https://docs.python.org/3.6/library/glob.html>`_ that needs to match your datasets. All of your datasets needs to match the dataset requirements (see docs from TradingEnv). If it is not the case, you can use the ``preprocess`` param to make your datasets match the requirements.
    :type dataset_dir: str

    :param preprocess: This function takes a pandas.DataFrame and returns a pandas.DataFrame. This function is applied to each dataset before being used in the environment.
        
        For example, imagine you have a folder named 'data' with several datasets (formatted as .pkl)

        .. code-block:: python

            import pandas as pd
            import numpy as np
            import gymnasium as gym
            from gym_trading_env

            # Generating features.
            def preprocess(df : pd.DataFrame):
                # You can easily change your inputs this way
                df["feature_close"] = df["close"].pct_change()
                df["feature_open"] = df["open"]/df["close"]
                df["feature_high"] = df["high"]/df["close"]
                df["feature_low"] = df["low"]/df["close"]
                df["feature_volume"] = df["volume"] / df["volume"].rolling(7*24).max()
                df.dropna(inplace= True)
                return df

            env = gym.make(
                    "MultiDatasetTradingEnv",
                    dataset_dir= 'examples/data/*.pkl',
                    preprocess= preprocess,
                )
    
    :type preprocess: function<pandas.DataFrame->pandas.DataFrame>

    :param episodes_between_dataset_switch: Number of times a dataset is used to create an episode, before moving on to another dataset. It can be useful for performances when `max_episode_duration` is low.
    :type episodes_between_dataset_switch: optional - int
    """
    def __init__(self,
                dataset_dir, 
                *args, 

                preprocess = lambda df : df,
                episodes_between_dataset_switch = 1,
                **kwargs):
        self.dataset_dir = dataset_dir
        self.preprocess = preprocess
        self.episodes_between_dataset_switch = episodes_between_dataset_switch
        self.dataset_pathes = glob.glob(self.dataset_dir)
        if len(self.dataset_pathes) == 0:raise FileNotFoundError(f"No dataset found with the path : {self.dataset_dir}")
        self.dataset_nb_uses = np.zeros(shape=(len(self.dataset_pathes), ))
        super().__init__(self.next_dataset(), *args, **kwargs)

    def next_dataset(self):
        self._episodes_on_this_dataset = 0
        # Find the indexes of the less explored dataset
        potential_dataset_pathes = np.where(self.dataset_nb_uses == self.dataset_nb_uses.min())[0]
        # Pick one of them
        random_int = np.random.randint(potential_dataset_pathes.size)
        dataset_idx = potential_dataset_pathes[ random_int ]
        dataset_path = self.dataset_pathes[dataset_idx]
        self.dataset_nb_uses[dataset_idx] += 1 # Update nb use counts

        self.name = Path(dataset_path).name
        return self.preprocess(pd.read_pickle(dataset_path))

    def reset(self, seed=None, options = None, **kwargs):
        self._episodes_on_this_dataset += 1
        if self._episodes_on_this_dataset % self.episodes_between_dataset_switch == 0:
            self._set_df(
                self.next_dataset()
            )
        if self.verbose > 1: print(f"Selected dataset {self.name} ...")
        return super().reset(seed = seed, options = options, **kwargs)
    
