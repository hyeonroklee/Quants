
from quantom import *
from nostalgia import *

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn import svm

s = None

def initialize(context):
    pass

def before_market_open(context,data):
    if s.isEnter(context,data['AAPL']):
        context.order(Symbol('AAPL'),10,MarketOrder())
    elif s.isExit(context,data['AAPL']):
        context.order(Symbol('AAPL'),-10,MarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    initial_price  = 50000
    initial_capital= 10000000

    # d = generate_stock_prices(n=100)
    # d = get_stock_prices_from_google()
    # d = get_stock_prices_from_csv('../data/stocks/a.csv')

    # data = generate_stocks(n=300,price=15000)
    data = pd.Panel( { 'AAPL' : generate_stock_prices(n=250,price=initial_price) } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_google(symbol='AAPL') } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_csv('../data/stocks/a.csv') } )

    s = SVMClassifier(training_data=data['AAPL'])

    data = pd.Panel( { 'AAPL' : generate_stock_prices(n=100,price=initial_price) } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_capital=initial_capital)
    ts.run(data)
    print str(ts._context)

    show_chart(data['AAPL'],buying_history=ts._context.buying_history,selling_history=ts._context.selling_history)
