
from quantom import *

import pandas as pd

def initialize(context):
    pass

def before_market_open(context,data):
    s = GoldenDeathCross()
    m = MACDCross()
    if m.isEntry(context,data['AAPL']):
        context.order(Symbol('AAPL'),10,MarketOrder())
    elif m.isExit(context,data['AAPL']):
        context.order(Symbol('AAPL'),-10,MarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    # d = generate_stock_prices(n=100)
    # d = get_stock_prices_from_google()
    # d = get_stock_prices_from_csv('../data/stocks/a.csv')

    data = generate_stocks(n=100)
    # data = pd.Panel( { 'AAPL' : generate_stock_prices(n=100) } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_google(symbol='AAPL') } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_csv('../data/stocks/a.csv') } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_capital=100000.)
    ts.run(data)
    print str(ts._context)

    show_chart(data['AAPL'],indicators=['macd'],moving_average=[5,12],buying_history=ts._context.buying_history,selling_history=ts._context.selling_history)