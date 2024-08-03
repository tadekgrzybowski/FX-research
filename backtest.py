import numpy as np
import pandas as pd
import matplotlib as plt
import time

#           Gathering Data
#----------------------------------------------------------------------------------------------------------------------------#
file_path = 'C:\\Users\\Tadek\\Documents\\TickData\\EURUSD_202406030000_202406282358.csv'

file_reader = pd.read_csv(file_path, header=0,sep='\t')

file_reader.loc[:,"<BID>"] = file_reader.loc[:,"<BID>"].replace("",np.NaN).fillna(file_reader.loc[:,"<ASK>"])

file_reader.loc[:,'<DATE_TIME>'] = pd.to_datetime(file_reader.pop('<DATE>')) + pd.to_timedelta(file_reader.pop('<TIME>'))

file_reader.insert(0, '<DATE_TIME>', file_reader.pop('<DATE_TIME>'))

file_reader.set_index('<DATE_TIME>')

resample_bid = file_reader.resample('1Min', on='<DATE_TIME>')['<BID>'].ohlc()

#print(resample_bid.head())

print(file_reader.loc[:,"<DATE_TIME>"].head())
#----------------------------------------------------------------------------------------------------------------------------#

class Engine():
    def __init__(self, initial_cash=100_000):
        self.strategy = None
        self.cash = initial_cash
        self.data = None

    def add_data(self, data:pd.DataFrame):
        self.data = data

    def run(self):
        for date in self.data.loc[:,"<DATE_TIME>"]:
            print(date)

class Strategy():
    """This base class will handle the execution logic of our trading strategies
    """
    def __init__(self):
        pass
    
class Trade():
    """Trade objects are created when an order is filled.
    """
    def __init__(self):
        pass

class Order():
    """When buying or selling, we first create an order object. If the order is filled, we create a trade object.
    """
    def __init__(self):
        pass

e = Engine()
e.add_data(file_reader)
e.run()