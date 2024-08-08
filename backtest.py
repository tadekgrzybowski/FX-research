import numpy as np
import pandas as pd
import matplotlib as plt
import time

#           Gathering Data
#----------------------------------------------------------------------------------------------------------------------------#
file_path = 'C:\\Users\\Tadek\\Documents\\TickData\\EURUSD_202406030000_202406282358.csv'

file_reader = pd.read_csv(file_path, header=0, sep='\t')

file_reader.loc[:,"<BID>"] = file_reader.loc[:,"<BID>"].replace("",np.NaN).fillna(file_reader.loc[:,"<ASK>"])

file_reader.loc[:,"<ASK>"] = file_reader.loc[:,"<ASK>"].replace("",np.NaN).fillna(file_reader.loc[:,"<BID>"])

file_reader.loc[:,'<DATE_TIME>'] = pd.to_datetime(file_reader.pop('<DATE>')) + pd.to_timedelta(file_reader.pop('<TIME>'))

#file_reader.insert(0, '<DATE_TIME>', file_reader.pop('<DATE_TIME>'))

# RESAMPLING DATA FROM TICK TO OHLC 1 MIN BARS
resample_bid = file_reader.resample('1Min', on='<DATE_TIME>')['<BID>'].ohlc()

for i in range(len(resample_bid)):
    if np.isnan(resample_bid.iloc[i, 0]):
        resample_bid.iloc[i, 0] = resample_bid.iloc[i-1, 3]
        resample_bid.iloc[i, 1] = resample_bid.iloc[i-1, 3]
        resample_bid.iloc[i, 2] = resample_bid.iloc[i-1, 3]
        resample_bid.iloc[i, 3] = resample_bid.iloc[i-1, 3]

print("FIXED DATA")
#-----------------------------------------------------------------------------------------#

# ENGINE USES OHLC DATA
class Engine():
    def __init__(self, initial_cash=100_000):
        self.strategy = None
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.data = None
        self.current_idx = None
        
    def add_data(self, data:pd.DataFrame):
        self.data = data
        
    def add_strategy(self, strategy):
        self.strategy = strategy
    
    def run(self):
        self.strategy.data = self.data
        
        for idx in self.data.index:
            self.current_idx = idx
            self.strategy.current_idx = self.current_idx
            self._fill_orders()
            
            self.strategy.on_bar()
        return self._get_stats()
            
    def _fill_orders(self):
        for order in self.strategy.orders:
            can_fill = False
            if order.side == 'buy' and self.cash >= self.data.loc[self.current_idx]['open'] * order.size:
                    can_fill = True 
            elif order.side == 'sell' and self.strategy.position_size >= order.size:
                    can_fill = True
            if can_fill:
                t = Trade(
                    ticker = order.ticker,
                    side = order.side,
                    price= self.data.loc[self.current_idx]['open'],
                    size = order.size,
                    type = order.type,
                    idx = self.current_idx)

                self.strategy.trades.append(t)
                self.cash -= t.price * t.size
        self.strategy.orders = []

    def _get_stats(self):
        metrics = {}
        total_return =100 * ((self.data.loc[self.current_idx]['close'] * self.strategy.position_size + self.cash) / self.initial_cash -1)
        metrics['total_return'] = total_return
        print(self.cash)
        return metrics

class Strategy():
    def __init__(self):
        self.current_idx = None
        self.data = None
        self.orders = []
        self.trades = []
    
    def buy(self,ticker,size=1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'buy',
                size = size,
                idx = self.current_idx
            ))

    def sell(self,ticker,size=1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'sell',
                size = -size,
                idx = self.current_idx
            ))
        
    @property
    def position_size(self):
        return sum([t.size for t in self.trades])
        
    def on_bar(self):
        pass
    
class Order():
    def __init__(self, ticker, size, side, idx):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.type = 'market'
        self.idx = idx
        
class Trade():
    def __init__(self, ticker,side,size,price,type,idx):
        self.ticker = ticker
        self.side = side
        self.price = price
        self.size = size
        self.type = type
        self.idx = idx
    def __repr__(self):
        return f'<Trade: {self.idx} {self.ticker} {self.size}@{self.price}>'

class BuyAndSellSwitch(Strategy):
    def on_bar(self):
        if self.position_size == 0:
            self.buy('AAPL', 1)
#            print(self.current_idx,"buy")
        else:
            self.sell('AAPL', 1)
#            print(self.current_idx,"sell")

e = Engine()
e.add_data(resample_bid)
e.add_strategy(BuyAndSellSwitch())
e.run()