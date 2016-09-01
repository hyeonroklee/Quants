import numpy as np
import pandas as pd
from pandas_datareader import data

from source import DataSource

class Stock(object):
    def __init__(self,symbol):
        self._symbol = symbol

if __name__ == '__main__':
    from_date = '2016-02-01'
    to_date = '2016-03-01'
    stock_symbols = ['AAPL','GOOG','AMZN','FB','MSFT']
    benchmark_symbol = 'SPY'

    ds = DataSource()
    d = ds.read_stock_data_from_yahoo('AAPL',from_date,to_date)
    ds.write_stock_data_to_file('AAPL',d)
    df = ds.read_stock_data_from_file('AAPL')
    print df