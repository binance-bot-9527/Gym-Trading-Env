import sys  
sys.path.append("./src")

import pandas as pd
from gym_trading_env.renderer import Renderer


renderer = Renderer(render_logs_dir="render_logs")

# # 添加自定义线（简单移动平均线）
# renderer.add_line( name= "sma10", function= lambda df : df["close"].rolling(10).mean(), line_options ={"width" : 1, "color": "purple"})
# renderer.add_line( name= "sma20", function= lambda df : df["close"].rolling(20).mean(), line_options ={"width" : 1, "color": "blue"})

# # 添加自定义指标（年化指标）
# renderer.add_metric(
#     name = "Annual Market Return",
#     function = lambda df : f"{ ((df['close'].iloc[-1] / df['close'].iloc[0])**(pd.Timedelta(days=365)/(df.index.values[-1] - df.index.values[0]))-1)*100:0.2f}%"
# )

# renderer.add_metric(
#         name = "Annual Portfolio Return",
#         function = lambda df : f"{((df['portfolio_valuation'].iloc[-1] / df['portfolio_valuation'].iloc[0])**(pd.Timedelta(days=365)/(df.index.values[-1] - df.index.values[0]))-1)*100:0.2f}%"
# )

renderer.run()