import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import statistics as st

load_dotenv()
# IMPORTING DATA

bid1m = pd.read_csv(os.getenv('bid1m'), sep = ',', header = 0, index_col=0)
ask1m = pd.read_csv(os.getenv('ask1m'), sep = ',', header = 0, index_col=0)
evnts = pd.read_csv(os.getenv('evnts'), sep = ',', header = 0, index_col=0)
tick = pd.read_csv(os.getenv('tick'), sep = ',', header = 0, index_col=0)


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

def candle_mean(side, minutes):
    n = 0
    j=0
    data_close = []
    data_open = []
    columns = []

    for i in range(minutes):
        data_close.append([])
        data_open.append([])
        columns.append(f'{i}')

    for idx in bid1m.index:
        if  evnts.index[n] == idx and (evnts.index[n+1] != idx or evnts.index[n-1] != idx) and is_evnt_result_positive(n) == True:
        # excluding datetimes with multiple events
            print(evnts.loc[:,'event_id'].iloc[n],evnts.index[n], bid1m.index[j], bid1m.loc[:,'open'].iloc[j])
            for i in range(minutes):
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

    if side == "close":
        df_close = pd.DataFrame(data_close)
        df_close = df_close.transpose()
        avg_close = df_close.mean()
        avg_close.plot()
    if side == "open":
        df_open = pd.DataFrame(data_open)
        df_open = df_open.transpose()
        avg_open = df_open.mean()
        avg_open.plot()

def tick_mean(minutes):
    data_tick = []
    for i in range(minutes*60 +30):
        data_tick.append([])

    k=0
    h=0
    prev_idx = tick.index[0]

    def price_in_t(datetime, side, point):
        if tick.index[point] > datetime:
            point = 0
        while (tick.index[point] < datetime) and point < len(tick)-60:
            point += 1
        point -= 1
        return (tick.loc[:,side][point],point)


    for k in range(len(evnts.index)-1):
    #for k in range(1):
        if (evnts.index[k+1] != evnts.index[k] or evnts.index[k-1] != evnts.index[k]) and is_evnt_result_positive(k) == True:
        #if  is_evnt_result_positive(k) == True:
            while (tick.index[h] <= evnts.index[k] and tick.index[h+1] > evnts.index[k]) == False and h < len(tick)-60:
                h+=1
            point0 = tick.loc[:,'<BID>'][h]
            print(evnts.index[k],tick.index[h], point0, k)
            j=h-300
            for i in range(minutes*60 +30):
                time_date = str(pd.Timestamp(evnts.index[k]) + pd.Timedelta(seconds=i) - pd.Timedelta(seconds=30))
                price_vector = price_in_t(time_date, '<BID>', j-1)
                j = price_vector[1]
                change = (price_vector[0]/point0 - 1)*100
                data_tick[i].append(change)
        else:
            while evnts.index[k] < prev_idx and k < len(evnts)-2:
                k+= 1

    df_tick = pd.DataFrame(data_tick)
    df_tick = df_tick.transpose()
    avg_tick = df_tick.mean()

    avg_tick.plot()

def tick_volatility(minutes, length):
    data_vol = []
    for i in range(minutes*60 +30):
        data_vol.append([])

    k=0
    h=0
    prev_idx = tick.index[0]

    mem = []
    for i in range(length):
        mem.append(0)

    def price_in_t(datetime, side, point):
        if tick.index[point] > datetime:
            point = 0
        while (tick.index[point] < datetime) and point < len(tick)-60:
            point += 1
        point -= 1
        return (tick.loc[:,side][point],point)


    for k in range(len(evnts.index)-1):
    #for k in range(1):
        if (evnts.index[k+1] != evnts.index[k] or evnts.index[k-1] != evnts.index[k]) and is_evnt_result_positive(k) == True:
        #if  is_evnt_result_positive(k) == True:
            event_idx_min_30sek = str(pd.Timestamp(evnts.index[k]) - pd.Timedelta(seconds=30))
            while (tick.index[h] <= event_idx_min_30sek and tick.index[h+1] > event_idx_min_30sek) == False and h < len(tick)-60:
                h+=1
            point0 = tick.loc[:,'<BID>'][h]
            j=h
            for i in range(minutes*60 +30):
                time_date = str(pd.Timestamp(evnts.index[k]) + pd.Timedelta(seconds=i) - pd.Timedelta(seconds=30))
                price_vector = price_in_t(time_date, '<BID>', j-1)
                j = price_vector[1]
                price = price_vector[0]
                for p in range(length):
                    if p < length-1:
                        mem[length-p-1]=mem[length-p-2]
                    else:
                        mem[0]=np.log(price/point0)
                if i < length:
                    data_vol[i].append(0)
                else:
                    data_vol[i].append(st.stdev(mem)*100000)
                point0 = price
        else:
            while evnts.index[k] < prev_idx and k < len(evnts)-2:
                k+= 1

    df_tick = pd.DataFrame(data_vol)
    df_tick = df_tick.transpose()
    avg_tick = df_tick.mean()

    plt.axvline(x=30)
    avg_tick.plot()

def min_max_dots_tick(minutes):
    k=0
    h=0
    prev_idx = tick.index[0]

    max_val = 0
    max_val_idx = 0

    min_val = 0
    min_val_idx = 0


    def price_in_t(datetime, side, point):
        if tick.index[point] > datetime:
            point = 0
        while (tick.index[point] < datetime) and point < len(tick)-60:
            point += 1
        point -= 1
        return (tick.loc[:,side][point],point)


    for k in range(len(evnts.index)-1):
    #for k in range(1):
        if (evnts.index[k+1] != evnts.index[k] or evnts.index[k-1] != evnts.index[k]) and is_evnt_result_positive(k) == True:
        #if  is_evnt_result_positive(k) == True:
            while (tick.index[h] <= evnts.index[k] and tick.index[h+1] > evnts.index[k]) == False and h < len(tick)-60:
                h+=1
            point0 = tick.loc[:,'<BID>'][h]
            max_val = point0
            min_val = point0
            j=h-300
            for i in range(minutes*60 +30):
                time_date = str(pd.Timestamp(evnts.index[k]) + pd.Timedelta(seconds=i) - pd.Timedelta(seconds=30))
                price_vector = price_in_t(time_date, '<BID>', j-1)
                j = price_vector[1]
                price = price_vector[0]
                if price > max_val:
                    max_val = price
                    max_val_idx = i
                if price < min_val:
                    min_val = price
                    min_val_idx = i
            plt.plot([max_val_idx, min_val_idx],[(max_val/point0 - 1)*100,(min_val/point0 - 1)*100],'-ko', label='line & marker', linewidth = 0.5)
            plt.plot(max_val_idx, (max_val/point0 - 1)*100, 'ro')
            plt.plot(min_val_idx, (min_val/point0 - 1)*100, 'bo')
            plt.axvline(x=30)
                
        else:
            while evnts.index[k] < prev_idx and k < len(evnts)-2:
                k+= 1


def min_max_dots(minutes):
    n = 0
    j=0

    max_val = 0
    max_val_idx = 0

    min_val = 0
    min_val_idx = 0

    counter = 0
    evnt_counter = 0
    mon_interval = 0

    for idx in bid1m.index:
        if  evnts.index[n] == idx and (evnts.index[n+1] != idx or evnts.index[n-1] != idx) and is_evnt_result_positive(n) == True:
        # excluding datetimes with multiple events
            evnt_counter += 1
            max_val = bid1m.loc[:,'high'].iloc[j]
            max_val_idx = 0
            min_val = bid1m.loc[:,'low'].iloc[j]
            min_val_idx = 0
            for i in range(minutes):
                if bid1m.loc[:,'high'].iloc[j+i] > max_val:
                    max_val = bid1m.loc[:,'high'].iloc[j+i]
                    max_val_idx = i
                if bid1m.loc[:,'low'].iloc[j+i] < min_val:
                    min_val = bid1m.loc[:,'low'].iloc[j+i]
                    min_val_idx = i
            if max_val_idx == 0 or min_val_idx == 0:
                counter += 1
                mon_interval += (np.abs(max_val_idx-min_val_idx))
            plt.plot([max_val_idx, min_val_idx], [(max_val/bid1m.loc[:,'open'].iloc[j] - 1) *100, (min_val/bid1m.loc[:,'open'].iloc[j] - 1) *100], '-ko', label='line & marker', linewidth = 0.5)
            plt.plot(max_val_idx, (max_val/bid1m.loc[:,'open'].iloc[j] - 1) *100, 'ro')
            plt.plot(min_val_idx, (min_val/bid1m.loc[:,'open'].iloc[j] - 1) *100, 'bo')
            if n < len(evnts) - 2:
                n+=1
        else:
            while evnts.index[n] < idx and n < len(evnts)-2:
                n+= 1
        j+=1
    print(evnt_counter)
    print((counter/evnt_counter)*100, mon_interval/counter)


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

#candle_mean("open",10)
#min_max_dots(10)

#tick_mean(7)
#min_max_dots_tick(7)

tick_volatility(4,10)

#avg_open.plot()

plt.show()

