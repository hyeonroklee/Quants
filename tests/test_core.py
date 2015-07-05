import numpy as np
import pandas as pd
from quantom.core import TradingSystem
from quantom.util import generate_stock_data

def initialize(context):
    print 'initialize'

def handle_data(context,data):
    print 'handle_data'
    print data

if __name__ == '__main__':
    data = generate_stock_data(n=3,price=1000.)
    df = pd.DataFrame(np.matrix(data).T.tolist(),columns=['open','high','low','close'])
    trading_system = TradingSystem(initialize=initialize,handle_data=handle_data)
    trading_system.run(df)