import numpy as np
import pandas as pd
from quantom import *

global trading_system
global order

def initialize(context):
    print 'initialize'
    context.security = Asset('AAPL')

def handle_data(context,data):
    print 'handle_data : ' + str(context.security)
    order(context.security,100)

if __name__ == '__main__':
    data = generate_stock_data(n=3,price=1000.)
    df = pd.DataFrame(np.matrix(data).T.tolist(),columns=['open','high','low','close'])
    trading_system = TradingSystem(initialize=initialize,handle_data=handle_data)
    order = trading_system.order
    trading_system.run(df)