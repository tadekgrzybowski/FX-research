import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
# IMPORTING DATA


bid1m = pd.read_csv(os.getenv('bid1m'), sep = ',', header = 0, index_col=0)
ask1m = pd.read_csv(os.getenv('ask1m'), sep = ',', header = 0, index_col=0)
evnts = pd.read_csv(os.getenv('evnts'), sep = ',', header = 0, index_col=0)

# bid1m.loc[:,'close'].plot()

#-----------------------------------------------------------------------------------------#
# ENGINE USES OHLC DATA

trade_balance = []

class Engine():
    def __init__(self, initial_cash=100000):
        self.strategy = None
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.data = None
        self.ask_data = None
        self.current_idx = None
        
    def add_data(self, data:pd.DataFrame):
        self.data = data

    def add_ask_data(self, data:pd.DataFrame):
        self.ask_data = data

    def add_strategy(self, strategy):
        self.strategy = strategy
    
    def run(self):
        self.strategy.data = self.data
        
        for idx in self.data.index:
            self.current_idx = idx
            self.strategy.current_idx = self.current_idx
            self._fill_orders()
            
            self.strategy.on_bar()
            self.strategy.prev_idx = self.strategy.current_idx
        return self._get_stats()
            
    def _fill_orders(self):
        orders_filled = []
        for order in self.strategy.orders:
            can_fill = False
            if str(pd.Timestamp(order.idx) + pd.Timedelta(minutes=1)) != self.current_idx:
                continue
            if order.side == 'buy' and self.cash >= self.data.loc[self.current_idx]['open'] * order.size:
                    can_fill = True 
            elif order.side == 'sell' and self.strategy.position_size >= order.size:
                    can_fill = True
            if can_fill:
                if order.side == 'sell':
                    t = Trade(
                        side = order.side,
                        price= self.ask_data.loc[order.idx]['open'],
                        size = order.size,
                        type = order.type,
                        idx = order.idx)
                if order.side == 'buy':
                    t = Trade(
                        side = order.side,
                        price= self.data.loc[order.idx]['open'],
                        size = order.size,
                        type = order.type,
                        idx = order.idx)
                    
#                print("ORDER FILLED", self.current_idx, order.side, self.data.loc[self.current_idx]['open'] ,self.ask_data.loc[self.current_idx]['open'])
                self.strategy.trades.append(t)
                self.cash -= t.price * t.size
                trade_balance.append([order.idx, self._get_stats()['total_return']])
                orders_filled.append(order)
#                self.strategy.orders.remove(order)
        for order in orders_filled:
            self.strategy.orders.remove(order)
        orders_filled = []
#        self.strategy.orders = []

    def _get_stats(self):
        metrics = {}
        total_return =100 * ((self.data.loc[self.current_idx]['close'] * self.strategy.position_size + self.cash) / self.initial_cash -1)
        metrics['total_return'] = total_return
#        print(metrics['total_return'], self.cash, self.strategy.position_size)
        return metrics

class Strategy():
    def __init__(self):
        self.current_idx = None
        self.prev_idx = None
        self.data = None
        self.orders = []
        self.trades = []
        self.event_num_idx = 0
    
    def buy(self,idx,size=1):
        self.orders.append(
            Order(
                side = 'buy',
                size = size,
                idx = idx
            ))

    def sell(self,idx,size=1):
        self.orders.append(
            Order(
                side = 'sell',
                size = -size,
                idx = idx
            ))
        
    @property
    def position_size(self):
        return sum([t.size for t in self.trades])
        
    def on_bar(self):
        pass
    
class Order():
    def __init__(self, size, side, idx):
        self.side = side
        self.size = size
        self.type = 'market'
        self.idx = idx
        
class Trade():
    def __init__(self,side,size,price,type,idx):
        self.side = side
        self.price = price
        self.size = size
        self.type = type
        self.idx = idx
    def __repr__(self):
        return f'<Trade: {self.idx} {self.size}@{self.price}>'

class BuyAndSellSwitch(Strategy):
    def on_bar(self):
        if self.prev_idx == None:
            self.prev_idx = self.current_idx
        if evnts.index[self.event_num_idx] >= self.prev_idx and evnts.index[self.event_num_idx] < self.current_idx:
            if evnts.loc[:,'impact_type'][self.event_num_idx] == 1:
                if evnts.loc[:,'forecast_value'][self.event_num_idx] < evnts.loc[:,'actual_value'][self.event_num_idx]:
                    self.buy(self.current_idx,1000)
                    self.sell(str(pd.Timestamp(self.current_idx) + pd.Timedelta(minutes=12)),1000)
            if evnts.loc[:,'impact_type'][self.event_num_idx] == 2:
                if evnts.loc[:,'forecast_value'][self.event_num_idx] > evnts.loc[:,'actual_value'][self.event_num_idx]:
                    self.buy(self.current_idx,1000)
                    self.sell(str(pd.Timestamp(self.current_idx) + pd.Timedelta(minutes=12)),1000)
            if self.event_num_idx < len(evnts)-1:
                self.event_num_idx += 1
        else:
            while evnts.index[self.event_num_idx] < self.prev_idx and self.event_num_idx < len(evnts)-1:
                self.event_num_idx += 1


e = Engine()
e.add_data(bid1m)
e.add_ask_data(ask1m)
e.add_strategy(BuyAndSellSwitch())
e.run()

df = pd.DataFrame(trade_balance, columns=['datetime', 'val'])
df = df.set_index('datetime')
df.plot()
plt.show()