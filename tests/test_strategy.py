
from quantom import *

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn import svm

def initialize(context):
    context.strategy = SVMClassifier(context,training_data=generate_stock_prices(n=500,price=initial_price),window=20,target=5)

def before_market_open(context,data):
    if context.strategy.is_enter(data['AAPL']):
        context.order('AAPL',100,MarketOrder())
    elif context.strataegy.is_exit(data['AAPL']):
        context.order('AAPL',-100,MarketOrder())

def after_market_close(context,data):
    pass

def optimize_strategy(data):

    optimal_return = -np.Inf
    optimal_short = 0
    optimal_long = 0

    cnt = 0
    for i in range(5,20):
        for j in range(i+5,i+20):
            short = i
            long = j
            profit_rate = 0.
            is_buy = False
            buy_price = 0.
            s = GoldenDeathCross(context=None,short=short,long=long)
            for symbol in data:
                print symbol,
                prices = data[symbol]
                for k in range(long+1,len(prices)):
                    if not is_buy and s.is_enter(prices[:k]):
                        is_buy = True
                        buy_price = prices['close'][k]
                    if is_buy and s.is_exit(prices[:k]):
                        is_buy = False
                        profit_rate += (prices['close'][k]/buy_price - 1)
            cnt += 1
            if cnt % 30:
                print '.',
            else:
                print '.'

            if profit_rate > optimal_return:
                optimal_return = profit_rate
                optimal_short = short
                optimal_long = long

    print ''
    print optimal_return,optimal_short,optimal_long

if __name__ == '__main__':

    initial_price  = 50000
    initial_cash = 10000000

    # d = generate_stock_prices(n=100)
    # d = read_stock_data_from_google('AAPL')
    # d = read_stock_data_from_file('AAPL')

    # data = generate_stocks(n=100,price=initial_price)
    # data = pd.Panel( { 'AAPL' : generate_stock_prices(n=300,price=initial_price) } )
    data = pd.Panel( { 'AAPL' : read_stock_data_from_file('AAPL') ,
                       'GOOG' : read_stock_data_from_file('GOOG')
                       } )
    # data = pd.Panel( { 'AAPL' : read_stock_data_from_file('AAPL') } )

    optimize_strategy(data)

    # ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close,initial_cash=initial_cash).run(data)
    # print str(ts.context)

    # show_chart(data['AAPL'],buying_history=ts.context.buying_history,selling_history=ts.context.selling_history)
