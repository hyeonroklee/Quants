import pandas as pd
import matplotlib.pyplot as plt
from quantom2 import *

def update_data(symbols,from_date,to_date):
    src = DataSource()
    for symbol in symbols:
        d = src.read_data_from_yahoo(symbol,from_date,to_date)
        src.write_data_to_file(symbol,d)

def initailize(context,data):
    symbols = [ 'AAPL' , 'GOOG' ]
    strategies = {}
    for symbol in symbols:
        strategy = GDCrossStrategy()
        strategy.optimize(data[symbol],short_ma_range=[5,10],long_ma_range=[14,21])
        strategies[symbol] = strategy
    context.symbols = symbols
    context.strategies = strategies

def handle_data(context,data):
    for symbol in context.symbols:
        if context.strategies[symbol].is_enter(data[symbol]):
            context.order(MarketOrder(symbol,10))
        if context.strategies[symbol].is_exit(data[symbol]):
            context.order(MarketOrder(symbol,-10))

if __name__ == '__main__':
    initial_cash = 10000
    from_date = '2016-01-01'
    to_date = '2016-11-01'
    symbols = ['AAPL', 'AMZN', 'FB', 'GOOG', 'MSFT', 'SPY']
    s = DataSource()
    # update_data(symbols,from_date,to_date)

    data = pd.Panel(
        { 'AAPL' : s.read_data_from_file('AAPL'),
          'GOOG' : s.read_data_from_file('GOOG'),
          'SPY' : s.read_data_from_file('SPY')})

    q = QSystem(from_date=from_date,to_date=to_date,data=data,
            initial_cash=initial_cash,initialize=initailize,handle_data=handle_data)
    q.run()
    q.evaluation()
    # for symbol in q._context.symbols:
    #     ax1, ax2 = q.plot(symbol)
    #     q._context.strategies[symbol].plot(q._data[symbol],ax1)
    # plt.show()