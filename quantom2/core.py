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

    def __init__(self,from_date,to_date,
                 data,initial_cash,initialize=None,handle_data=None):
        self._data = data
        self._from_date = from_date
        self._to_date = to_date
        self._orders = []
        self._context = Context(initial_cash)
        self._context.order = self._order
        self._context.evaluation = self.evaluation
        self._context.record = self._record
        self._current_date = None
        self._initialize = initialize
        self._handle_data = handle_data
        self._buy_history = []
        self._sell_history = []
        self._history = {}

    def run(self):
        self._current_date = pd.Timestamp(self._from_date)
        _delta = pd.Timedelta(days=1)
        _dates = self._data.axes[1]
        _dates_len = len(_dates)
        while not self._current_date in _dates:
            self._current_date += _delta
            if self._current_date > _dates[-1]:
                raise ValueError('date outbounded')

        self._process_initialize(self._current_date)
        for i in range(_dates.get_loc(self._current_date),_dates_len-1):
            self._current_date = _dates[i]
            try:
                self._process_handle_data(self._current_date)
            except Exception as e:
                print str(e)
            self._process_order(_dates[i+1])

    def _order(self,order):
        self._orders.append(order)

    def _process_initialize(self,current_date):
        if self._initialize is not None:
            self._initialize(self._context,self._data.loc[:,:current_date,:])

    def _process_handle_data(self,current_date):
        if self._handle_data is not None:
            self._handle_data(self._context,self._data.loc[:,:current_date,:])

    def _process_order(self,current_date):
        while len(self._orders) > 0:
            self._orders.reverse()
            order = self._orders.pop()
            buying_price = -1
            selling_price = -1
            if isinstance(order,MarketOrder):
                try:
                    open_price = self._data[order._symbol]['Open'][current_date]
                    if order._amount > 0:
                        buying_price = open_price
                        if buying_price != -1:
                            self._process_buying(current_date,order._symbol,buying_price,order._amount)
                    else:
                        selling_price = open_price
                        if selling_price != -1:
                            self._process_selling(current_date,order._symbol,selling_price,np.abs(order._amount))
                except KeyError:
                    print 'Not available date',current_date
            elif isinstance(order,LimitOrder):
                try:
                    high_price = self._data[order._symbol]['High'][current_date]
                    low_price = self._data[order._symbol]['Low'][current_date]
                    if order._amount > 0:
                        if order._price >= low_price and order._price <= high_price:
                            buying_price = order._price
                        elif order._price > high_price:
                            buying_price = high_price
                        elif order._price < low_price:
                            print 'The order hasnt been made', order._price, '<' , low_price
                        if buying_price != -1:
                            self._process_buying(current_date,order._symbol,buying_price,order._amount)
                    else:
                        if order._price >= low_price and order._price <= high_price:
                            selling_price = order._price
                        elif order._price < low_price:
                            selling_price = low_price
                        elif order._price > high_price:
                            print 'The order hasnt been made', order._price, '>' , high_price
                        self._process_selling(current_date,order._symbol,selling_price,np.abs(order._amount))
                except KeyError:
                    print 'Not available date',current_date
            else:
                print 'none'

    def _process_buying(self,current_date,symbol,price,amount):
        # print '_process_buying',current_date,symbol,price,amount
        if self._context._available_cash >= price * amount:
            self._context._portfolio.add_asset(symbol,price,amount)
            self._context._available_cash -= price * amount
            self._buy_history.append([current_date,symbol,price,amount])
        else:
            print 'Not enought cash to buy'

    def _process_selling(self,current_date,symbol,price,amount):
        # print '_process_selling',current_date,symbol,price,amount
        if self._context._portfolio.get_asset_amount(symbol) >= amount:
            self._context._portfolio.remove_asset(symbol,amount)
            self._context._available_cash += price * amount
            self._sell_history.append([current_date,symbol,price,amount])
        else:
            print 'Not enought amount to sell'

    def evaluation(self):
        print '##### evaluation ########'
        try:
            portfolio_valuation = 0.
            for symbol in self._context._portfolio._assets:
                print symbol,\
                    self._context._portfolio.get_asset_amount(symbol),\
                    self._context._portfolio.get_asset_avg_price(symbol),\
                    self._data[symbol]['Close'][-1]
                portfolio_valuation += self._context._portfolio.get_asset_amount(symbol) * self._data[symbol]['Close'][self._current_date]
            total_valuation = self._context._available_cash + portfolio_valuation
            print self._context._available_cash,portfolio_valuation,total_valuation,self._context._initial_cash
            print 'strategy return : ', total_valuation/self._context._initial_cash - 1.
        except KeyError as e:
            print str(e)
        print '#########################'

    def _record(self,symbol,**kwarg):
        if not symbol in self._history:
            self._history[symbol] = {}
        for key in kwarg:
            value = kwarg[key]
            if not key in self._history[symbol]:
                self._history[symbol][key] = []
            self._history[symbol][key].append(value)

    def plot(self,symbol):
        prices = self._data[symbol]

        dates = [ mdates.date2num(date) for date in prices.index]
        open_prices = prices['Open']
        high_prices = prices['High']
        low_prices = prices['Low']
        close_prices = prices['Close']
        volumes = prices['Volume'] if 'Volume' in prices.columns else None

        chart_data = np.matrix([dates,open_prices,high_prices,low_prices,close_prices]).T.tolist()

        fig = plt.figure(figsize=(15,8))
        ax1 = plt.subplot2grid((5,4),(0,0),rowspan=4,colspan=4)
        mfinance.candlestick_ohlc(ax1,chart_data,colorup='r',colordown='b',alpha=0.7)
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.ylabel('Price')

        ax2 = plt.subplot2grid((5,4),(4,0),sharex=ax1,rowspan=1,colspan=4)
        ax2.grid(True)

        fig.subplots_adjust(hspace=0)
        plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.setp(ax1.get_xticklabels(),visible=False)
        ax1.set_yticks(ax1.get_yticks()[1:])

        b = np.array(self._buy_history)
        s = np.array(self._sell_history)
        if len(b) > 0:
            idx_b = (b[:,1] == symbol)
            ax1.plot(b[idx_b,0],b[idx_b,2],'ro')
        if len(s) > 0:
            idx_s = (s[:,1] == symbol)
            ax1.plot(s[idx_s,0],s[idx_s,2],'bo')

        return ax1,ax2


