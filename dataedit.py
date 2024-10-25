import numpy as np
import pandas as pd

#           Gathering Data
#----------------------------------------------------------------------------------------------------------------------------#
file_path = 'C:\\Users\\Tadek\\Documents\\TickData\\EURUSD_202401020000_202410232359.csv'

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

# print(evpfl.head())

# print(resample_bid.head())

# SAVING DATA TO FILE

resample_bid.to_csv('data\\bid1m.csv')

resample_ask.to_csv('data\\ask1m.csv')

evpfl.to_csv('data\\events.csv')

print("FIXED DATA")
#-----------------------------------------------------------------------------------------#