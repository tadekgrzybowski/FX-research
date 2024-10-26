import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# IMPORTING DATA

bid1m = pd.read_csv('data\\bid1m.csv', sep = ',', header = 0, index_col=0)
ask1m = pd.read_csv('data\\ask1m.csv', sep = ',', header = 0, index_col=0)
evnts = pd.read_csv('data\\events.csv', sep = ',', header = 0, index_col=0)


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
    if  evnts.index[n] == prev_index and (evnts.index[n+1] != evnts.index[n] or evnts.index[n-1] != evnts.index[n]) and is_evnt_result_positive(n) == True:
    # excluding datetimes with multiple events
        for i in range(20):
            prcnt_chng_close = (bid1m.loc[:,'close'][j+i]/bid1m.loc[:,'close'][j] - 1)
            prcnt_chng_open = (bid1m.loc[:,'open'][j+i]/bid1m.loc[:,'open'][j] - 1)
            data_close[i].append(prcnt_chng_close)
            data_open[i].append(prcnt_chng_open)
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

prcnt_larger_val_than_max_avg = 0
prcnt_larger_val_than_max_avg_idx = 0
for i in range(len(df_close)):
    for j in range(20):
        if df_close.loc[:,j][i] >= avg_close.nlargest(1).values[0]:
            prcnt_larger_val_than_max_avg += 1
            break
prcnt_larger_val_than_max_avg = prcnt_larger_val_than_max_avg/len(df_close)

print(prcnt_larger_val_than_max_avg)

#df_close.std().add(avg_close).plot()
#avg_close.sub(df_close.std()).plot()
#df_close.std().plot()
avg_close.plot()
#avg_open.plot()
plt.show()