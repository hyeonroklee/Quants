
from quantom import *

import pandas as pd

def initialize(context):
    context.macd_strategy = MACDCross()
    context.svm_strategy = SVMClassifier(generate_stock_prices(n=600,price=context.initial_cash))
    context.nn_strategy = NNClassifier(generate_stock_prices(n=600,price=context.initial_cash))

def before_market_open(context,data):
    if context.nn_strategy.isEnter(context,data['AAPL']):
        context.order('AAPL',10,MarketOrder())
    elif context.nn_strategy.isExit(context,data['AAPL']):
        context.order('AAPL',-10,MarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    initial_price = 50000
    initial_cash =10000000

    # d = generate_stock_prices(n=100)
    # d = get_stock_prices_from_google()
    # d = get_stock_prices_from_csv('../data/stocks/a.csv')

    # data = generate_stocks(n=100,price=initial_price)
    data = pd.Panel( { 'AAPL' : generate_stock_prices(n=300,price=initial_price) } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_google(symbol='AAPL') } )
    # data = pd.Panel( { 'AAPL' : get_stock_prices_from_csv('../data/stocks/a.csv') } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_cash=initial_cash)
    ts.run(data)
    print str(ts._context)

    show_chart(data['AAPL'],indicators=['macd'],moving_average=[5,12],buying_history=ts._context.buying_history,selling_history=ts._context.selling_history)