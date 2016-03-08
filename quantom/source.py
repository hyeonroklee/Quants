import os
import datetime as dt
import urllib as url

import numpy as np
import pandas as pd

stock_exchange_path = {
    'NASDAQ' : '/../data/usa/NASDAQ/',
    'NYSE' : '/../data/usa/NYSE/',
    'KOSDAQ' : '/../data/korea11/KOSDAQ/',
    'KOSPI' : '/../data/korea11/KOSPI/'
}

def update_stock_data_file(exchange,symbol,data):
    target_file = os.path.dirname(__file__)  + stock_exchange_path[exchange] + symbol + '.csv'
    try:
        history_data =  pd.read_csv(target_file,index_col='date',usecols=['date','open','high','low','close','volume'],
                           parse_dates=['date'],date_parser=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
                           dtype={'open':np.float,'high':np.float,'low':np.float,'close':np.float,'volume':np.int})
        for date in data.index.values:
            history_data.loc[date] = data.loc[date]
        history_data.sort_index(inplace=True)
        history_data.index.name = 'date'
        history_data.to_csv(target_file)
    except IOError:
        data.to_csv(target_file)


def read_stock_data_from_google(exchange,symbol,start_date='2015-06-04',end_date='2016-01-08'):
    sym = symbol.upper()
    start = dt.date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]))
    end = dt.date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]))
    url_string = "http://www.google.com/finance/historical?q={0}".format(sym)
    url_string += "&startdate={0}&enddate={1}&output=csv".format(start.strftime('%b %d, %Y'),end.strftime('%b %d, %Y'))
    csv = url.urlopen(url_string).readlines()[1:]
    csv.reverse()

    result = pd.DataFrame([],columns=['open','high','low','close','volume'])
    result.to_csv()
    for line in csv:
        _date, _open, _high , _low, _close, _volume = line.rstrip().split(',')
        open_price, high_price, low_price, close_price = [float(x) for x in [_open,_high,_low,_close]]
        date = dt.datetime.strptime(_date,'%d-%b-%y')
        result = result.append(pd.DataFrame([[open_price,high_price,low_price,close_price,_volume]],columns=['open','high','low','close','volume'],index=[date]))
    result.index.name = 'date'
    return result

def read_stock_data_from_file(exchange,symbol):
    target_file = os.path.dirname(__file__) + stock_exchange_path[exchange] + '/' + symbol + '.csv'
    return pd.read_csv(target_file,index_col='date',usecols=['date','open','high','low','close','volume'],
                       parse_dates=['date'],date_parser=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
                       dtype={'open':np.float,'high':np.float,'low':np.float,'close':np.float,'volume':np.int})

def read_stock_data_from_all_files():
    stock_data = {}
    for exchange in stock_exchange_path:
        try:
            for f in os.listdir(os.path.dirname(__file__) + stock_exchange_path[exchange]):
                if f.endswith(".csv"):
                    symbol = f.split('.')[0]
                    stock_data[symbol] = read_stock_data_from_file(exchange,symbol)
        except Exception as e:
            print str(e)
    return pd.Panel(stock_data)