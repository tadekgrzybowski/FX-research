import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# IMPORTING DATA

bid1m = pd.read_csv('data\\bid1m.csv', sep = ',', header = 0, index_col=0)
ask1m = pd.read_csv('data\\ask1m.csv', sep = ',', header = 0, index_col=0)
evnts = pd.read_csv('data\\events.csv', sep = ',', header = 0, index_col=0)

# bid1m.loc[:,'close'].plot()

#-----------------------------------------------------------------------------------------#
#   DATA ANALYSIS 
n = 0
j=0
prev_index = bid1m.index[0]
data_close = []
data_open = []
columns = []

for i in range(20):
    data_close.append([])
    data_open.append([])
    columns.append(f'{i}')

def is_evnt_result_positive(number):
    if evnts.loc[:,'impact_type'][number] == 1:
        if evnts.loc[:,'forecast_value'][number] < evnts.loc[:,'actual_value'][number]:
            return True
    if evnts.loc[:,'impact_type'][number] == 2:
        if evnts.loc[:,'forecast_value'][number] > evnts.loc[:,'actual_value'][number]:
            return True
    return False

for idx in bid1m.index:
    prev_index = idx
    if evnts.index[n] <= idx and evnts.index[n] >= prev_index and (evnts.index[n+1] != evnts.index[n] or evnts.index[n-1] != evnts.index[n]) and is_evnt_result_positive(n) == True:
    # excluding datetimes with multiple events
        for i in range(20):
            data_close[i].append(bid1m.loc[:,'close'][j+i])
            data_open[i].append(bid1m.loc[:,'open'][j+i])
    else:
        while evnts.index[n] < prev_index and n < len(evnts)-2:
            n+= 1
    j+=1


df_close = pd.DataFrame(data_close)
df_close = df_close.transpose()
avg_close = df_close.mean()

df_open = pd.DataFrame(data_open)
df_open = df_open.transpose()
avg_open = df_open.mean()



avg_close.plot()
#avg_open.plot()
plt.show()
#-----------------------------------------------------------------------------------------#
# ENGINE USES OHLC DATA
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
            if pd.Timestamp(order.idx) + pd.Timedelta(minutes=1) != self.current_idx:
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
                    
                print("ORDER FILLED", self.current_idx, order.side, self.data.loc[self.current_idx]['open'] ,self.ask_data.loc[self.current_idx]['open'])
                self.strategy.trades.append(t)
                self.cash -= t.price * t.size
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
        print(metrics['total_return'], self.cash, self.strategy.position_size)
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
                    self.sell(pd.Timestamp(self.current_idx) + pd.Timedelta(minutes=10),1000)
            if evnts.loc[:,'impact_type'][self.event_num_idx] == 2:
                if evnts.loc[:,'forecast_value'][self.event_num_idx] > evnts.loc[:,'actual_value'][self.event_num_idx]:
                    self.buy(self.current_idx,1000)
                    self.sell(pd.Timestamp(self.current_idx) + pd.Timedelta(minutes=10),1000)
            if self.event_num_idx < len(evnts)-1:
                self.event_num_idx += 1
        else:
            while evnts.index[self.event_num_idx] < self.prev_idx and self.event_num_idx < len(evnts)-1:
                self.event_num_idx += 1


# e = Engine()
# e.add_data(bid1m)
# e.add_ask_data(ask1m)
# e.add_strategy(BuyAndSellSwitch())
# e.run()