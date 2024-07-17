import numpy as np
import pandas as pd

file_path = 'C:\\Users\\Tadek\\Documents\\TickData\\EURUSD_202406030000_202406282358.csv'

file_reader = pd.read_csv(file_path, header=0, names=['Date_time', 'Bid', 'Ask', 'Vol'], index_col=['Date_time'], parse_dates=['Date_time'], chunksize=10000)















#p_h5 = 'C:/Users/Tadek/Desktop/inf/serious/FX-bullshit/py_data_storage.h5'

#h5_file = pd.HDFStore(p_h5, complevel=5, complib='blosc')  

#i = 1
#for chunk in file_reader:
#    h5_file.append('fx_tick_data', chunk, complevel=5, complib='blosc')
#    i += 1
#    print('Writing Chunk no.{}'.format(i))
