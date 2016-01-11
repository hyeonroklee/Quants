
from quantom import *

import pandas as pd
import matplotlib.dates as mdates

def initialize(context):
    context.symbols = [ Symbol('AAPL') , Symbol('AMZN') ]

def before_market_open(context,data):
    # apply a simple strategy
    try:
        ma_short = sma(data['AAPL']['close'],window=5)[-1]
        ma_long = sma(data['AAPL']['close'],window=12)[-1]
        if ma_short > ma_long:
            context.order(Symbol('AAPL'),10,MarketOrder())
        else:
            context.order(Symbol('AAPL'),-10,MarketOrder())
    except Exception as e:
        pass

def after_market_close(context,data):
    pass

if __name__ == '__main__':
    # data = generate_stocks(n=100,price=10.)
    data = pd.Panel( { 'AAPL' : get_stock_prices_from_google() } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_csv('../data/stocks/a.csv') } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_capital=100000000.)
    ts.run(data)
    print str(ts._context)

    show_chart(data['AAPL'],indicators=['ma5','ma12'],buying_history=ts._context.buying_history,selling_history=ts._context.selling_history)