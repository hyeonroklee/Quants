
from quantom import *

if __name__ == '__main__':
    symbols = [ 'AAPL' , 'GOOG' , 'AMZN', 'ORCL', 'XOM', 'FB', 'TWTR', 'IBM', 'MSFT', 'ADBE' ]
    for symbol in symbols:
        data1 = read_stock_data_from_google(symbol,start_date='2015-01-01',end_date='2016-02-08')
        update_stock_data_file(symbol,data1)

    print read_stock_data_from_file('AAPL')
    print read_stock_data_from_all_files()['AAPL']
