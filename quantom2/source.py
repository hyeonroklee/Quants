import os

import datetime as dt
import numpy as np
import pandas as pd
from pandas_datareader import data

class DataSource(object):
    def __init__(self):
        self._base_dir = os.path.dirname(__file__) + '/data'
        if not os.path.exists(self._base_dir):
            os.makedirs(self._base_dir)
    def set_base_dir(self,base_dir):
        self._base_dir = base_dir
        if not os.path.exists(self._base_dir):
            os.makedirs(self._base_dir)
    def read_data_from_yahoo(self,symbol,from_date,to_date):
        return data.DataReader(symbol,'yahoo',from_date,to_date)
    def read_data_from_file(self,symbol):
        target_file = self._base_dir + '/' + symbol + '.csv'
        return pd.read_csv(target_file,index_col='Date',usecols=['Date','Open','High','Low','Close','Volume'],
                       parse_dates=['Date'],date_parser=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
                       dtype={'Open':np.float,'High':np.float,'Low':np.float,'Close':np.float,'Volume':np.int})
    def write_data_to_file(self,symbol,data):
        target_file = self._base_dir + '/' + symbol + '.csv'
        try:
            history_data = pd.read_csv(target_file,index_col='Date',usecols=['Date','Open','High','Low','Close','Volume'],
                   parse_dates=['Date'],date_parser=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
                   dtype={'Open':np.float,'High':np.float,'Low':np.float,'Close':np.float,'Volume':np.int})
            for date in data.index.values:
                history_data.loc[date] = data.loc[date]
            history_data.sort_index(inplace=True)
            history_data.index.name = 'Date'
            history_data.to_csv(target_file)
        except IOError:
            data.to_csv(target_file)