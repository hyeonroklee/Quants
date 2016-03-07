
from quantom import *

import pandas as pd

def initialize(context):
    context.macd_strategy = MACDCross(context)

def before_market_open(context,data):
    if context.macd_strategy.is_enter(data['AAPL']):
        context.order('AAPL',10,CloseMarketOrder())
    elif context.macd_strategy.is_exit(data['AAPL']):
        context.order('AAPL',-10,CloseMarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    initial_price = 50000
    initial_cash =10000000

    data = pd.Panel( { 'AAPL' : read_stock_data_from_google('AAPL') } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_cash=initial_cash).run(data)
    print str(ts.context)

    show_chart(data['AAPL'],indicators=['macd'],moving_average=[5,12],buying_history=ts.context.buying_history['AAPL'],selling_history=ts.context.selling_history['AAPL'])