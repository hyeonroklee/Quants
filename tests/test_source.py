
from quantom import *

if __name__ == '__main__':
    symbols = [ 'AAPL' , 'GOOG' , 'AMZN' ]
    for symbol in symbols:
        data1 = read_stock_data_from_google(symbol,start_date='2015-06-04',end_date='2016-01-08')
        update_stock_data_file(symbol,data1)
        data2 = read_stock_data_from_google(symbol,start_date='2015-12-04',end_date='2016-02-08')
        update_stock_data_file(symbol,data2)

    print read_stock_data_from_file('AAPL')
