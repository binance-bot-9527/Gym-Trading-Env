from flask import Flask, render_template, jsonify, make_response

from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar

from .utils.charts import charts
from pathlib import Path 
import glob
import pandas as pd


class Renderer():
    # 渲染器类，用于可视化交易环境的运行结果。
    def __init__(self, render_logs_dir):
        # 初始化渲染器。
        # render_logs_dir: 渲染日志文件所在的目录。
        self.app = Flask(__name__, static_folder="./templates/")
        # self.app.debug = True # 调试模式，生产环境应关闭。
        self.app.config["EXPLAIN_TEMPLATE_LOADING"] = True
        self.df = None
        self.render_logs_dir = render_logs_dir
        self.metrics = [
            # 默认指标列表。
            {
                # 投资组合回报率指标。
                # 市场回报率指标。
                "name": "Market Return",
                "function" : lambda df : f"{(df['close'].iloc[-1] / df['close'].iloc[0] - 1)*100:0.2f}%",
            },
            {
                "name": "Portfolio Return",
                "function" : lambda df : f"{ (df['portfolio_valuation'].iloc[-1] / df['portfolio_valuation'].iloc[0] - 1)*100:0.2f}%"
            },
        ]
        self.lines = [] # 用于存储额外线条的列表。
    
    def add_metric(self, name, function):
        # 添加自定义指标。
        # name: 指标名称。
        # function: 计算指标值的函数。
        self.metrics.append(
            {"name": name, "function":function}
        )
    def add_line(self, name, function, line_options = None):
        # 添加自定义线条。
        # name: 线条名称。
        # function: 计算线条值的函数。
        # line_options: 线条的样式选项。
        self.lines.append(
            {"name": name, "function":function}
        )
        if line_options is not None: self.lines[-1]["line_options"] = line_options
    def compute_metrics(self, df):
        # 计算所有指标。
        # df: 包含市场和投资组合数据的DataFrame。
        for metric in self.metrics:
            metric["value"] = metric["function"](df)
    def run(self,):
        # 运行渲染器，启动Flask应用。
        @self.app.route("/")
        # 根路由，渲染主页面。
        def index():
            render_pathes = glob.glob(f"{self.render_logs_dir}/*.pkl")
            render_names = [Path(path).name for path in render_pathes]
            return render_template('index.html', render_names = render_names)

        @self.app.route("/update_data/<name>")
        # 更新图表数据的路由。
        def update(name = None):
            if name is None or name == "":
                render_pathes = glob.glob(f"{self.render_logs_dir}/*.pkl")
                name = Path(render_pathes[-1]).name
            self.df = pd.read_pickle(f"{self.render_logs_dir}/{name}")
            chart = charts(self.df, self.lines)
            return chart.dump_options_with_quotes()

        @self.app.route("/metrics")
        # 获取指标数据的路由。
        def get_metrics():
            self.compute_metrics(self.df)
            return jsonify([{'name':metric['name'], 'value':metric['value']} for metric in self.metrics])

        self.app.run()

