
from quantom import *

if __name__ == '__main__':
    stocks = { 'NASDAQ' : [ 'AAPL' , 'GOOG' , 'AMZN', 'FB', 'MSFT', 'ADBE' ] }
    for exchange in stocks:
        for symbol in stocks[exchange]:
            data1 = read_stock_data_from_google(exchange,symbol,start_date='2015-01-01',end_date='2016-02-08')
            update_stock_data_file(exchange,symbol,data1)

    print read_stock_data_from_file('NASDAQ','AAPL')
    print read_stock_data_from_all_files()['AAPL']
