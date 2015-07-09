import numpy as np
import pandas as pd
from quantom import *

def initialize(context):
    print 'initialize ...'
    context.symbols = [ Symbol('AAPL') , Symbol('AMZN') ]


def before_market_open(context,data):
    print 'before_market_open ...'
    for sym in context.symbols:
        print 'order = ' + str(context.order(sym,10,style=LimitOrder(9.5)))

def after_market_close(context,data):
    print 'after_market_close ...'
    print context.get_value()

if __name__ == '__main__':
    data = generate_stocks(price=10.)
    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    ts.run(data)
    print str(ts._context)


    # p = {}
    # for sym in data:
    #     print data[sym][:2]
    #     p[sym] = data[sym][:2]
    #
    # p = pd.Panel(p)
    # print p