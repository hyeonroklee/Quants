import numpy as np
import pandas as pd
from quantom import *

global ts

def initialize(context):
    print 'initialize ...'
    context.security = Symbol('AAPL')

def before_market_open(context):
    print 'before_market_open ...'

def handle_data(context,data):
    print 'handle_data ...'
    ts.order(context.security,100)

if __name__ == '__main__':
    data = generate_stock_data(n=3,price=10.)
    df = pd.DataFrame(np.matrix(data).T.tolist(),columns=['open','high','low','close'])
    ts = TradingSystem(initialize=initialize,handle_data=handle_data,before_market_open=before_market_open)
    ts.run(df)
    print str(ts._context)