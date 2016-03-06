
from quantom import *

import time
import sys
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn import svm

def initialize(context):
    data = pd.Panel( { 'AAPL' : read_stock_data_from_file('AAPL') } )

    # optimal_return,optimal_args = optimize_strategy(strategy=GoldenDeathCross,data=data,short=range(5,10),long=range(11,20))
    # optimal_args['context'] = context
    # context.gdc_strategy = GoldenDeathCross(**optimal_args)

    optimal_return,optimal_args = optimize_strategy(strategy=MACDCross,data=data,short=range(5,10),long=range(11,20),signal=range(9,10))
    optimal_args['context'] = context
    context.macd_strategy = MACDCross(**optimal_args)

    print optimal_return,optimal_args

    # context.macd_strategy = MACDCross(context,short=12,long=26,signal=9)
    # context.svm_strategy = SVMClassifier(context,training_data=generate_stock_prices(n=500,price=initial_price),window=20,target=5)
    # context.nn_strategy = NNClassifier(context,read_stock_data_from_file('AAPL'),window=20,target=5)

    context.strategy = context.macd_strategy

def before_market_open(context,data):
    if context.strategy.is_enter(data['AAPL']):
        context.order('AAPL',100,MarketOrder())
    elif context.strategy.is_exit(data['AAPL']):
        context.order('AAPL',-100,MarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    initial_price = 50000
    initial_cash = 10000000

    data = pd.Panel( { 'AAPL' : read_stock_data_from_file('AAPL') ,
                       'GOOG' : read_stock_data_from_file('GOOG') } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_cash=initial_cash).run(data)
    print str(ts.context)

    show_chart(data['AAPL'],buying_history=ts.context.buying_history,selling_history=ts.context.selling_history)
