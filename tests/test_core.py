import numpy as np
import pandas as pd
from quantom import *

def initialize(context):
    print 'initialize ...'
    context.security = Symbol('AAPL')

def before_market_open(context,data):
    print 'before_market_open ...'
    print 'order = ' + str(context.order(context.security,100,style=LimitOrder(9.5)))

def after_market_close(context,data):
    print 'after_market_close ...'
    print context.get_value()

if __name__ == '__main__':
    data = generate_stock_data(n=10,price=10.)
    df = pd.DataFrame(np.matrix(data).T.tolist(),columns=['open','high','low','close'])
    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    ts.run(df)
    print str(ts._context)