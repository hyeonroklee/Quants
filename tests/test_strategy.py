
from quantom import *

import numpy as np
import pandas as pd

def initialize(context):
    data = pd.Panel( { 'AAPL' : read_stock_data_from_file('NASDAQ','AAPL')[:100] } )

    optimal_return,optimal_args = optimize_strategy(strategy=GoldenDeathCross,data=data,short=range(5,10),long=range(11,20))
    optimal_args['context'] = context
    context.strategy = GoldenDeathCross(**optimal_args)
    context.optimal_short = optimal_args['short']
    context.optimal_long = optimal_args['long']
    print optimal_return,optimal_args['short'],optimal_args['long']

    # optimal_return,optimal_args = optimize_strategy(strategy=MACDCross,data=data,short=range(5,10),long=range(11,20),signal=range(9,10))
    # optimal_args['context'] = context
    # context.strategy = MACDCross(**optimal_args)

    # optimal_return,optimal_args = optimize_strategy(strategy=SVMClassifier,data=data,training_data=data['AAPL'],window=range(5,20),target=range(5,15))
    # optimal_args['context'] = context
    # context.strategy = SVMClassifier(**optimal_args)
    # print optimal_return,optimal_args['window'],optimal_args['target']

    # optimal_return,optimal_args = optimize_strategy(strategy=NNClassifier,data=data,training_data=data['AAPL'],window=range(5,10),target=range(5,10))
    # optimal_args['context'] = context
    # context.strategy = NNClassifier(**optimal_args)
    # print optimal_return,optimal_args['window'],optimal_args['target']

    # context.macd_strategy = MACDCross(context,short=12,long=26,signal=9)
    # context.svm_strategy = SVMClassifier(context,training_data=generate_stock_prices(n=500,price=initial_price),window=20,target=5)
    # context.nn_strategy = NNClassifier(context,read_stock_data_from_file('AAPL'),window=20,target=5)

def before_market_open(context,data):
    if context.strategy.is_enter(data['AAPL']):
        context.order('AAPL',100,CloseMarketOrder())
    elif context.strategy.is_exit(data['AAPL']):
        context.order('AAPL',-100,CloseMarketOrder())

def after_market_close(context,data):
    pass

if __name__ == '__main__':

    initial_price = 50000
    initial_cash = 10000000

    data = pd.Panel( { 'AAPL' : read_stock_data_from_file('NASDAQ','AAPL')[:100] ,
                       'GOOG' : read_stock_data_from_file('NASDAQ','GOOG')[:100] } )

    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_cash=initial_cash).run(data)
    print str(ts.context)

    show_chart(data['AAPL'],moving_average=[ts.context.optimal_short,ts.context.optimal_long],buying_history=ts.context.buying_history['AAPL'],selling_history=ts.context.selling_history['AAPL'])