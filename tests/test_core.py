
from quantom import *

import pandas as pd

def initialize(context):
    print 'initialize ...'
    context.symbols = [ Symbol('AAPL') , Symbol('AMZN') ]

def before_market_open(context,data):
    print 'before_market_open ...'
    context.order(Symbol('AAPL'),10,LimitOrder(103))


def after_market_close(context,data):
    print 'after_market_close ...'

if __name__ == '__main__':

    # data = generate_stocks(n=100,price=10.)

    # print data["asdf"], data.shape

    # a1 = Asset(Symbol('ASDF'))
    # a1.add(10,100)
    # a1.add(20,200)
    #
    # a2 = Asset(Symbol('ASDF'))
    # a2.add(30,200)
    #
    # p = Portfolio()
    # p.add_asset(a1.get_symbol(),a1.get_amount(),a1.get_avg_price())
    # p.add_asset(a2.get_symbol(),a2.get_amount(),a2.get_avg_price())
    # print p

    stock_prices = pd.DataFrame(data=[ [100,105,95,102,1000],
                                       [101,106,96,103,1000] ],
                                columns=['open','high','low','close','volume'],dtype=float)
    data = pd.Panel({ "AAPL" : stock_prices })
    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    ts.run(data)
    print str(ts._context)