
from quantom import *

import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':

    # sma test cases
    prices = [1,2,3,4]
    t1 = sma(prices)
    assert t1 is not None and len(t1) == 0
    t2 = sma(prices,4)
    assert t2 is not None and len(t2) == 1 and t2[0] == 2.5
    t3 = sma(prices,2,1)
    assert t3 is not None and len(t3) == 1 and t3[0] == 3.5

    # ema test cases
    prices = [1,32,4,8,16,32,64]
    print ema(prices)
    print sma(prices)
    print willr(prices,2)
    print rocr(prices,2)

    # optimize_portfolio
    stock_data = {}
    stocks = { 'NASDAQ' : [ 'AAPL' , 'GOOG' , 'AMZN', 'FB', 'MSFT', 'ADBE' ] }
    for exchange in stocks:
        for symbol in stocks[exchange]:
            stock_data[symbol] = read_stock_data_from_file(exchange,symbol)

    p = pd.Panel(stock_data)
    best,best_r,best_v, ws,rets,vars = optimize_portfolio(p)
    print best

    plt.plot(vars,rets)
    plt.plot(best_v,best_r,'r+')
    plt.show()

