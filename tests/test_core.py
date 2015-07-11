import numpy as np
import pandas as pd
from quantom import *

def initialize(context):
    print 'initialize ...'
    context.symbols = [ Symbol('AAPL') , Symbol('AMZN') ]


def before_market_open(context,data):
    print '\n\nbefore_market_open ...'

    print str(context.portfolio)

    for sym in context.symbols:
        context.order(sym,10,LimitOrder(9.5))
        context.order(sym,-5,LimitOrder(10.5))

def after_market_close(context,data):
    print 'after_market_close ...\n\n'

if __name__ == '__main__':
    data = generate_stocks(n=200,price=10.)
    print data.shape
    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    ts.run(data)
    print str(ts._context)