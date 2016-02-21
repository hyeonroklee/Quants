import os
import datetime as dt
import urllib as url

import numpy as np
import pandas as pd

def update_stock_data_file(symbol,data):
    target_file = os.path.dirname(__file__) + '/../data/' + symbol + '.csv'
    #
    # current_date = pd.to_datetime(str(data.index.values[0])).strftime('%Y-%m-%d')
    # da =  pd.read_csv(target_file,index_col='date',usecols=['date','open','high','low','close','volume'],
    #                    parse_dates=['date'],date_parser=lambda x: dt.datetime.strptime(x, '%Y-%m-%d'),
    #                    dtype={'open':np.float32,'high':np.float32,'low':np.float32,'close':np.float32,'volume':np.int32})


def read_stock_data_from_google(symbol,start_date='2015-06-04',end_date='2016-01-08'):
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
    return result

if __name__ == '__main__':
    symbol = 'AAPL'
    data = read_stock_data_from_google(symbol)
    update_stock_data_file(symbol,data)
