import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.finance as mfinance
import matplotlib.dates as mdates

class Order(object):
    def __init__(self):
        pass

class MarketOrder(Order):
    def __init__(self,symbol,amount):
        self._symbol = symbol
        self._amount = amount

class LimitOrder(Order):
    def __init__(self,symbol,price,amount):
        self._symbol = symbol
        self._price = price
        self._amount = amount

class Asset(object):
    def __init__(self,symbol,price,amount):
        self._symbol = symbol
        self._avg_price = float(price)
        self._amount = int(amount)
    def add(self,price,amount):
        self._avg_price = (self._avg_price * self._amount + price * amount) / (self._amount + amount)
        self._amount += amount
    def remove(self,amount):
        if self._amount >= amount:
            self._amount -= amount
            if self._amount == 0:
                self._avg_price = 0
        else:
            raise ValueError('not available amount : %d > %d' % (amount,self._amount))
    def __str__(self):
        return 'avg_price = %.2f amount = %d' % (self._avg_price,self._amount)

class Portfolio(object):
    def __init__(self):
        self._assets = {}
    def add_asset(self,symbol,price,amount):
        if not symbol in self._assets:
            self._assets[symbol] = Asset(symbol,0,0)
        self._assets[symbol].add(price,amount)
    def remove_asset(self,symbol,amount):
        if symbol in self._assets:
            self._assets[symbol].remove(amount)
    def get_asset_avg_price(self,symbol):
        if symbol in self._assets:
            return self._assets[symbol]._avg_price
        else:
            return 0.
    def get_asset_amount(self,symbol):
        if symbol in self._assets:
            return self._assets[symbol]._amount
        else:
            return 0.
    def __str__(self):
        s = '{'
        for symbol in self._assets:
            s += ' %s : %s, ' % (symbol,str(self._assets[symbol]))
        s += '}'
        return s

class Context(object):
    def __init__(self,initial_cash):
        self._initial_cash = initial_cash
        self._available_cash = initial_cash
        self._portfolio = Portfolio()


class QSystem(object):

    class Callback(object):

        def __init__(self):
            super(QSystem.Callback, self).__init__()

        def initialize(self,context,data):
            pass

        def handle_data(self,context,data):
            pass

    def __init__(self,from_date,to_date,
                 data,initial_cash,callback):
        self._data = data
        self._from_date = pd.Timestamp(from_date)
        self._to_date = pd.Timestamp(to_date)
        self._orders = []
        self._context = Context(initial_cash)
        self._context.order = self._order
        self._context.evaluation = self.evaluation
        self._callback = callback
        self._buy_history = {}
        self._sell_history = {}

    def run(self):
        _dates = self._data.axes[1]
        _dates_len = len(_dates)
        self._process_initialize(self._from_date)
        for i in range(_dates.get_loc(self._from_date),_dates_len-1):
            if not _dates[i] < self._to_date:
                break
            self._process_handle_data(_dates[i])
            self._process_order(_dates[i+1])


    def _order(self,order):
        self._orders.append(order)

    def _process_initialize(self,date):
        self._callback.initialize(self._context,self._data.loc[:,:date,:])

    def _process_handle_data(self,date):
        self._callback.handle_data(self._context,self._data.loc[:,:date,:])

    def _process_order(self,date):
        while len(self._orders) > 0:
            self._orders.reverse()
            order = self._orders.pop()
            buying_price = -1
            selling_price = -1
            if isinstance(order,MarketOrder):
                try:
                    open_price = self._data[order._symbol]['Open'][date]
                    if order._amount > 0:
                        buying_price = open_price
                        if buying_price != -1:
                            self._process_buying(date,order._symbol,buying_price,order._amount)
                    else:
                        selling_price = open_price
                        if selling_price != -1:
                            self._process_selling(date,order._symbol,selling_price,np.abs(order._amount))
                except KeyError:
                    print 'Not available date',date
            elif isinstance(order,LimitOrder):
                try:
                    high_price = self._data[order._symbol]['High'][date]
                    low_price = self._data[order._symbol]['Low'][date]
                    if order._amount > 0:
                        if order._price >= low_price and order._price <= high_price:
                            buying_price = order._price
                        elif order._price > high_price:
                            buying_price = high_price
                        elif order._price < low_price:
                            print 'The order hasnt been made', order._price, '<' , low_price
                        if buying_price != -1:
                            self._process_buying(date,order._symbol,buying_price,order._amount)
                    else:
                        if order._price >= low_price and order._price <= high_price:
                            selling_price = order._price
                        elif order._price < low_price:
                            selling_price = low_price
                        elif order._price > high_price:
                            print 'The order hasnt been made', order._price, '>' , high_price
                        self._process_selling(date,order._symbol,selling_price,np.abs(order._amount))
                except KeyError:
                    print 'Not available date',date
            else:
                print 'none'

    def _process_buying(self,date,symbol,price,amount):
        # print '_process_buying',current_date,symbol,price,amount
        if self._context._available_cash >= price * amount:
            self._context._portfolio.add_asset(symbol,price,amount)
            self._context._available_cash -= price * amount
            if not self._buy_history.has_key(symbol):
                self._buy_history[symbol] = []
            self._buy_history[symbol].append([date,price,amount])
        else:
            print 'Not enough cash to buy'

    def _process_selling(self,date,symbol,price,amount):
        # print '_process_selling',current_date,symbol,price,amount
        if self._context._portfolio.get_asset_amount(symbol) >= amount:
            self._context._portfolio.remove_asset(symbol,amount)
            self._context._available_cash += price * amount
            if not self._sell_history.has_key(symbol):
                self._sell_history[symbol] = []
            self._sell_history[symbol].append([date,price,amount])
        else:
            print 'Not enough amount to sell'

    def evaluation(self):
        print '##### evaluation #################################'
        try:
            portfolio_valuation = 0.
            for symbol in self._context._portfolio._assets:

                latest_date = self._to_date
                while np.isnan(self._data[symbol]['Close'][latest_date]):
                    latest_date -= pd.Timedelta(days=1)
                latest_price = self._data[symbol]['Close'][latest_date]

                print symbol,\
                    self._context._portfolio.get_asset_amount(symbol),\
                    self._context._portfolio.get_asset_avg_price(symbol), \
                    latest_price
                portfolio_valuation += self._context._portfolio.get_asset_amount(symbol) * latest_price
            total_valuation = self._context._available_cash + portfolio_valuation
            print 'available_cash : ',self._context._available_cash
            print 'portfolio_valuation : ', portfolio_valuation
            print 'total_valuation : ', total_valuation,'(',self._context._initial_cash,')'
            print 'strategy return : ', total_valuation/self._context._initial_cash - 1.
        except KeyError as e:
            print str(e)
        print '##################################################'

    def get_buy_history(self):
        return self._buy_history

    def get_sell_history(self):
        return self._sell_history

    def get_context(self):
        return self._context