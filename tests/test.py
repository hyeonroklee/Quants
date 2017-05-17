from quantom import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class QSystemCallback(QSystem.Callback):
    def __init__(self):
        super(QSystemCallback, self).__init__()

    def initialize(self, context, data):
        super(QSystemCallback, self).initialize(context, data)
        symbols = ['GOOG']
        strategies = {}
        for symbol in symbols:
            strategy = GDCrossStrategy()
            strategy.optimize(data[symbol], short_ma_range=[5, 10], long_ma_range=[14, 20])
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
    begin_date = '2015-01-02'
    from_date = '2016-06-01'
    to_date = '2016-12-01'
    symbols = ['SPY', 'GOOG']

    s = DataSource()
    stock_data = s.read_all_stocks_data(symbols,begin_date,to_date)

    q = QSystem(from_date=from_date,to_date=to_date,data=stock_data,
            initial_cash=initial_cash,callback=QSystemCallback())
    q.run()
    q.evaluation()

    symbol = 'GOOG'
    ax1, ax2 = q.plot(symbol,from_date,to_date)
    ctx = q.get_context()
    data = q.get_data(symbol,from_date,to_date)
    ctx.strategies[symbol].plot(data,ax1)
    plt.show()
