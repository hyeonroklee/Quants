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

    def read_stock_data(self,symbol,from_date,to_date):
        stock_data_file = self._base_dir + '/' + symbol + '.csv'
        from_date_time = dt.datetime.strptime(from_date, '%Y-%m-%d')
        to_date_time = dt.datetime.strptime(to_date, '%Y-%m-%d')
        if os.path.exists(stock_data_file):
            history_data = pd.read_csv(stock_data_file, index_col='Date',
                usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
                parse_dates=['Date'], date_parser=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
                dtype={'Open': np.float, 'High': np.float, 'Low': np.float, 'Close': np.float,'Volume': np.float})
            try:
                history_data.ix[from_date_time]
                history_data.ix[to_date_time]
            except KeyError:
                stock_data = data.DataReader(symbol, 'google', from_date, to_date)
                for date in stock_data.index.values:
                    history_data.ix[date] = stock_data.ix[date]
                history_data.sort_index(inplace=True)
                history_data.index.name = 'Date'
                history_data.to_csv(stock_data_file)
        else:
            history_data = data.DataReader(symbol, 'google', from_date, to_date)
            history_data.sort_index(inplace=True)
            history_data.index.name = 'Date'
            history_data.to_csv(stock_data_file)
        return history_data.ix[from_date_time:to_date_time]

    def read_all_stocks_data(self,symbols,from_date,to_date):
        stocks_data = {}
        for symbol in symbols:
            stocks_data[symbol] = self.read_stock_data(symbol,from_date=from_date,to_date=to_date)
        return pd.Panel(stocks_data)
