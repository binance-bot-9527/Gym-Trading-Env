class Portfolio:
    def __init__(self, asset, fiat, interest_asset = 0, interest_fiat = 0):
        # 初始化投资组合。
        # asset: 资产数量。
        # fiat: 法币数量。
        # interest_asset: 资产的利息（借入资产）。
        # interest_fiat: 法币的利息（借入法币）。
        self.asset =asset
        self.fiat =fiat
        self.interest_asset = interest_asset
        self.interest_fiat = interest_fiat
    def valorisation(self, price):
        # 计算投资组合的总估值。
        # price: 当前资产价格。
        return sum([
            self.asset * price,
            self.fiat,
            - self.interest_asset * price,
            - self.interest_fiat
        ])
    def real_position(self, price):
        # 计算实际头寸（考虑借入资产）。
        # price: 当前资产价格。
        return (self.asset - self.interest_asset)* price / self.valorisation(price)
    def position(self, price):
        # 计算名义头寸。
        # price: 当前资产价格。
        return self.asset * price / self.valorisation(price)
    def trade_to_position(self, position, price, trading_fees):
        # 根据目标头寸进行交易。
        # position: 目标头寸。
        # price: 当前资产价格。
        # trading_fees: 交易费用。
        # 偿还利息
        current_position = self.position(price)
        interest_reduction_ratio = 1
        if (position <= 0 and current_position < 0):
            interest_reduction_ratio = min(1, position/current_position)
        elif (position >= 1 and current_position > 1):
            interest_reduction_ratio = min(1, (position-1)/(current_position-1))
        if interest_reduction_ratio < 1:
            self.asset = self.asset - (1-interest_reduction_ratio) * self.interest_asset
            self.fiat = self.fiat - (1-interest_reduction_ratio) * self.interest_fiat
            self.interest_asset = interest_reduction_ratio * self.interest_asset
            self.interest_fiat = interest_reduction_ratio * self.interest_fiat
        
        # 进行交易
        asset_trade = (position * self.valorisation(price) / price - self.asset)
        if asset_trade > 0:
            asset_trade = asset_trade / (1 - trading_fees + trading_fees * position)
            asset_fiat = - asset_trade * price
            self.asset = self.asset + asset_trade * (1 - trading_fees)
            self.fiat = self.fiat + asset_fiat
        else:
            asset_trade = asset_trade / (1 - trading_fees * position)
            asset_fiat = - asset_trade * price
            self.asset = self.asset + asset_trade 
            self.fiat = self.fiat + asset_fiat * (1 - trading_fees)
    def update_interest(self, borrow_interest_rate):
        # 更新借贷利息。
        # borrow_interest_rate: 借贷利率。
        self.interest_asset = max(0, - self.asset)*borrow_interest_rate
        self.interest_fiat = max(0, - self.fiat)*borrow_interest_rate
    def __str__(self): return f"{self.__class__.__name__}({self.__dict__})" # 返回投资组合的字符串表示。
    def describe(self, price): print("Value : ", self.valorisation(price), "Position : ", self.position(price)) # 打印投资组合的估值和头寸。
    def get_portfolio_distribution(self):
        # 获取投资组合的分布情况。
        # 返回一个字典，包含资产、法币、借入资产、借入法币、资产利息和法币利息。
        return {
            "asset":max(0, self.asset),
            "fiat":max(0, self.fiat),
            "borrowed_asset":max(0, -self.asset),
            "borrowed_fiat":max(0, -self.fiat),
            "interest_asset":self.interest_asset,
            "interest_fiat":self.interest_fiat,
        }

class TargetPortfolio(Portfolio):
    # 目标投资组合类，继承自Portfolio。
    # 用于根据目标头寸和价值初始化投资组合。
    def __init__(self, position ,value, price):
        # 初始化目标投资组合。
        # position: 目标头寸。
        # value: 投资组合的总价值。
        # price: 当前资产价格。
        super().__init__(
            asset = position * value / price,
            fiat = (1-position) * value,
            interest_asset = 0,
            interest_fiat = 0
        )
