import numpy as np
import pandas as pd
import matplotlib as plt
import datetime

#           Gathering Data
#----------------------------------------------------------------------------------------------------------------------------#
file_path = 'C:\\Users\\Tadek\\Documents\\TickData\\EURUSD_202406030000_202406282358.csv'

event_file_path = 'C:\\Users\\Tadek\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\test.csv'

file_reader = pd.read_csv(file_path, header=0, sep='\t')

evpfl = pd.read_csv(event_file_path, sep = ";", header=0)

file_reader.loc[:,"<BID>"] = file_reader.loc[:,"<BID>"].replace("",np.NaN).fillna(file_reader.loc[:,"<ASK>"])

file_reader.loc[:,"<ASK>"] = file_reader.loc[:,"<ASK>"].replace("",np.NaN).fillna(file_reader.loc[:,"<BID>"])

file_reader.loc[:,'<DATE_TIME>'] = pd.to_datetime(file_reader.pop('<DATE>')) + pd.to_timedelta(file_reader.pop('<TIME>'))

#file_reader.insert(0, '<DATE_TIME>', file_reader.pop('<DATE_TIME>'))

# RESAMPLING DATA FROM TICK TO OHLC 1 MIN BARS
resample_bid = file_reader.resample('1Min', on='<DATE_TIME>')['<BID>'].ohlc()

resample_ask = file_reader.resample('1Min', on='<DATE_TIME>')['<ASK>'].ohlc()

for i in range(len(resample_bid)):
    if np.isnan(resample_bid.iloc[i, 0]):
        resample_bid.iloc[i, 0] = resample_bid.iloc[i-1, 3]
        resample_bid.iloc[i, 1] = resample_bid.iloc[i-1, 3]
        resample_bid.iloc[i, 2] = resample_bid.iloc[i-1, 3]
        resample_bid.iloc[i, 3] = resample_bid.iloc[i-1, 3]

for i in range(len(resample_ask)):
    if np.isnan(resample_ask.iloc[i, 0]):
        resample_ask.iloc[i, 0] = resample_ask.iloc[i-1, 3]
        resample_ask.iloc[i, 1] = resample_ask.iloc[i-1, 3]
        resample_ask.iloc[i, 2] = resample_ask.iloc[i-1, 3]
        resample_ask.iloc[i, 3] = resample_ask.iloc[i-1, 3]

evpfl.loc[:,'<DATE_TIME>'] = pd.to_datetime(evpfl.loc[:,'<DATE_TIME>'])

evpfl = evpfl.set_index('<DATE_TIME>')

#print(evpfl.head())

print("FIXED DATA")
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
            if order.idx + pd.Timedelta(minutes=1) != self.current_idx:
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
        if evpfl.index[self.event_num_idx] >= self.prev_idx and evpfl.index[self.event_num_idx] < self.current_idx:
            if evpfl.loc[:,'impact_type'][self.event_num_idx] == 1:
                if evpfl.loc[:,'forecast_value'][self.event_num_idx] < evpfl.loc[:,'actual_value'][self.event_num_idx]:
                    self.buy(self.current_idx,1000)
                    self.sell(self.current_idx + pd.Timedelta(minutes=10),1000)
            if evpfl.loc[:,'impact_type'][self.event_num_idx] == 2:
                if evpfl.loc[:,'forecast_value'][self.event_num_idx] > evpfl.loc[:,'actual_value'][self.event_num_idx]:
                    self.buy(self.current_idx,1000)
                    self.sell(self.current_idx + pd.Timedelta(minutes=10),1000)
            if self.event_num_idx < len(evpfl)-1:
                self.event_num_idx += 1
        else:
            while evpfl.index[self.event_num_idx] < self.prev_idx and self.event_num_idx < len(evpfl)-1:
                self.event_num_idx += 1

e = Engine()
e.add_data(resample_bid)
e.add_ask_data(resample_ask)
e.add_strategy(BuyAndSellSwitch())
e.run()