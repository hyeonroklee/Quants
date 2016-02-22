
from quantom import *
from nostalgia import *

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn import svm

def initialize(context):
    training_data = generate_stock_prices(n=500,price=initial_price)
    context.strategy = SVMClassifier(training_data=training_data,window=20,target=5)

def before_market_open(context,data):
    if context.strategy.isEnter(context,data['AAPL']):
        context.order('AAPL',100,MarketOrder())
    elif context.strategy.isExit(context,data['AAPL']):
        context.order('AAPL',-100,MarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    initial_price  = 50000
    initial_cash = 10000000

    # d = generate_stock_prices(n=100)
    # d = read_stock_data_from_google('AAPL')
    # d = read_stock_data_from_file('AAPL')

    # data = generate_stocks(n=100,price=initial_price)
    # data = pd.Panel( { 'AAPL' : generate_stock_prices(n=300,price=initial_price) } )
    data = pd.Panel( { 'AAPL' : read_stock_data_from_google('AAPL') } )
    # data = pd.Panel( { 'AAPL' : read_stock_data_from_file('AAPL') } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_cash=initial_cash)
    ts.run(data)
    print str(ts._context)

    show_chart(data['AAPL'],buying_history=ts._context.buying_history,selling_history=ts._context.selling_history)
