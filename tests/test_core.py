
from quantom import *

def initialize(context):
    print 'initialize ...'
    context.symbols = [ Symbol('AAPL') , Symbol('AMZN') ]

def before_market_open(context,data):
    print 'before_market_open ...'
    context.order(Symbol('AAPL'),100,MarketOrder())


def after_market_close(context,data):
    print 'after_market_close ...'

if __name__ == '__main__':

    data = generate_stocks(n=100,price=10.)
    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    ts.run(data)
    print str(ts._context)