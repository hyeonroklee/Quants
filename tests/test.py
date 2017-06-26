from quantom import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class QSystemCallback(QSystem.Callback):
    def __init__(self):
        super(QSystemCallback, self).__init__()

    def initialize(self, context, data):
        super(QSystemCallback, self).initialize(context, data)
        symbols = ['GOOG','AAPL','FB','AMZN', 'MSFT']
        strategies = {}
        for symbol in symbols:
            strategy = GDCrossStrategy()
            strategy.optimize(data[symbol], short_ma_range=[5, 6], long_ma_range=[14, 15])
            strategies[symbol] = strategy
        context.symbols = symbols
        context.strategies = strategies

    def handle_data(self, context, data):
        super(QSystemCallback, self).handle_data(context, data)
        for symbol in context.symbols:
            if context.strategies[symbol].is_enter(data[symbol]):
                context.order(MarketOrder(symbol,1))
            if context.strategies[symbol].is_exit(data[symbol]):
                context.order(MarketOrder(symbol,-1))

if __name__ == '__main__':
    initial_cash = 2000
    begin_date = '2015-01-01'
    from_date = '2016-06-01'
    to_date = '2016-12-01'
    symbols = ['GOOG','AAPL','FB','AMZN', 'MSFT']

    s = DataSource()
    # s.update_stock_data(symbols,from_date,to_date)
    data = s.read_stock_data(symbols)[:,pd.Timestamp(begin_date):,:]
    q = QSystem(from_date=from_date,to_date=to_date,data=data,
            initial_cash=initial_cash,callback=QSystemCallback())
    q.run()
    q.evaluation()

    buying_history = q.get_buy_history()
    selling_history = q.get_sell_history()
    ctx = q.get_context()
    for symbol in symbols:
        ax1, ax2 = plot_stock(data[symbol][pd.Timestamp(from_date):],buying_history[symbol],selling_history[symbol])
        ctx.strategies[symbol].plot(data[symbol][pd.Timestamp(from_date):],ax1)
    plt.show()
