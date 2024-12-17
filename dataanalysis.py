import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# IMPORTING DATA

bid1m = pd.read_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\bid1m.csv', sep = ',', header = 0, index_col=0)
ask1m = pd.read_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\ask1m.csv', sep = ',', header = 0, index_col=0)
evnts = pd.read_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\events.csv', sep = ',', header = 0, index_col=0)
tick = pd.read_csv('C:\\Users\\Tadek\\Desktop\\inf\\serious\\data\\tick.csv', sep = ',', header = 0, index_col=0)


#-----------------------------------------------------------------------------------------#
#   DATA ANALYSIS 

def is_evnt_result_positive(number):
    if evnts.loc[:,'impact_type'].iloc[number] == 1:
        if evnts.loc[:,'forecast_value'].iloc[number] < evnts.loc[:,'actual_value'].iloc[number]:
            return True
    if evnts.loc[:,'impact_type'].iloc[number] == 2:
        if evnts.loc[:,'forecast_value'].iloc[number] > evnts.loc[:,'actual_value'].iloc[number]:
            return True
    return False

def is_evnt_result_negative(number):
    if evnts.loc[:,'impact_type'].iloc[number] == 1:
        if evnts.loc[:,'forecast_value'].iloc[number] > evnts.loc[:,'actual_value'].iloc[number]:
            return True
    if evnts.loc[:,'impact_type'].iloc[number] == 2:
        if evnts.loc[:,'forecast_value'].iloc[number] < evnts.loc[:,'actual_value'].iloc[number]:
            return True
    return False

def candle_mean(side):
    n = 0
    j=0
    data_close = []
    data_open = []
    columns = []

    for i in range(20):
        data_close.append([])
        data_open.append([])
        columns.append(f'{i}')

    for idx in bid1m.index:
        if  evnts.index[n] == idx and (evnts.index[n+1] != evnts.index[n] or evnts.index[n-1] != evnts.index[n]) and is_evnt_result_positive(n) == True:
        # excluding datetimes with multiple events
            for i in range(20):
                prcnt_chng_close = (bid1m.loc[:,'close'].iloc[j+i]/bid1m.loc[:,'close'].iloc[j] - 1) *100
                prcnt_chng_open = (bid1m.loc[:,'open'].iloc[j+i]/bid1m.loc[:,'open'].iloc[j] - 1) *100
                data_close[i].append(prcnt_chng_close)
                data_open[i].append(prcnt_chng_open)
            if n < len(evnts) - 2:
                n+=1
        else:
            while evnts.index[n] < idx and n < len(evnts)-2:
                n+= 1
        j+=1

    df_close = pd.DataFrame(data_close)
    df_close = df_close.transpose()
    avg_close = df_close.mean()
    df_open = pd.DataFrame(data_open)
    df_open = df_open.transpose()
    avg_open = df_open.mean()

    if side == "close":
        avg_close.plot()
    if side == "open":
        avg_open.plot()

def tick_mean():
    data_tick = []
    for i in range(1200 +30):
        data_tick.append([])

    k=0
    h=0
    prev_idx = tick.index[0]

    def price_in_t(datetime, side, point):
        while (tick.index[point] <= datetime and tick.index[point+1] > datetime) == False and point < len(tick)-60:
            point += 1
        return tick.loc[:,side][point]


    for k in range(len(evnts.index)-1):
    #for k in range(1):
        if (evnts.index[k+1] != evnts.index[k] or evnts.index[k-1] != evnts.index[k]) and is_evnt_result_positive(k) == True:
        #if  is_evnt_result_positive(k) == True:
            while (tick.index[h] <= evnts.index[k] and tick.index[h+1] > evnts.index[k]) == False and h < len(tick)-60:
                h+=1
            point0 = tick.loc[:,'<BID>'][h]
            print(evnts.index[k], point0, k)
            for i in range(1200 +30):
                time_date = str(pd.Timestamp(evnts.index[k]) + pd.Timedelta(seconds=i) - pd.Timedelta(seconds=30))
                change = (price_in_t(time_date, '<BID>', h-1000)/point0 - 1)*100
                data_tick[i].append(change)
        else:
            while evnts.index[k] < prev_idx and k < len(evnts)-2:
                k+= 1

    df_tick = pd.DataFrame(data_tick)
    df_tick = df_tick.transpose()
    avg_tick = df_tick.mean()

    avg_tick.plot()


# prcnt_larger_val_than_max_avg = 0
# prcnt_larger_val_than_max_avg_idx = 0

# prcnt_smaller_val_than_max_avg = 0
# prcnt_smaller_val_than_max_avg_idx = 0
# for i in range(len(df_close)):
#     for j in range(20):
#         if df_close.loc[:,j][i] >= avg_close.nlargest(1).values[0]:
#             prcnt_larger_val_than_max_avg += 1
#             break
#     for j in range(20):
#         if df_close.loc[:,j][i] <= -avg_close.nlargest(1).values[0]:
#             prcnt_smaller_val_than_max_avg += 1
#             break

# prcnt_larger_val_than_max_avg = prcnt_larger_val_than_max_avg/len(df_close)
# prcnt_smallerr_val_than_max_avg = prcnt_smaller_val_than_max_avg/len(df_close)

# print(prcnt_larger_val_than_max_avg)
# print(prcnt_smallerr_val_than_max_avg)

#df_close.std().add(avg_close).plot()
#avg_close.sub(df_close.std()).plot()

#df_close.std().plot()

candle_mean()
#avg_open.plot()

plt.show()

