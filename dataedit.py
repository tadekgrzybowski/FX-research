import numpy as np
import pandas as pd

#           Gathering Data
#----------------------------------------------------------------------------------------------------------------------------#
file_path = 'C:\\Users\\Tadek\\Documents\\TickData\\EURUSD_202301020702_202312292358.csv'

event_file_path = 'C:\\Users\\Tadek\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\test.csv'

event_filter_path = 'C:\\Users\\Tadek\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\test2.csv'

file_reader = pd.read_csv(file_path, header=0, sep='\t')

evpfl = pd.read_csv(event_file_path, sep = ";", header=0)

event_filter = pd.read_csv(event_filter_path, sep = ";", header=0, encoding='cp1252')

print(event_filter.loc[:,"event_id"].to_numpy())

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

for i in range(len(evpfl)):
    if (evpfl.loc[:,"event_id"][i] in event_filter.loc[:,"event_id"].to_numpy()) == False:
        evpfl = evpfl.drop([i])

evpfl = evpfl.set_index('<DATE_TIME>')
evpfl = evpfl.sort_index()
# print(evpfl.head())

# print(resample_bid.head())

tick = file_reader[['<DATE_TIME>','<BID>','<ASK>']].copy()

tick = tick.set_index('<DATE_TIME>')

# SAVING DATA TO FILE

resample_bid.to_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\bid1m.csv')

resample_ask.to_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\ask1m.csv')

evpfl.to_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\events.csv')

tick.to_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\tick.csv')

print("FIXED DATA")
#-----------------------------------------------------------------------------------------#