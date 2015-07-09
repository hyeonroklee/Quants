
import numpy as np
import pandas as pd

class Symbol(object):
    def __init__(self,sid):
        super(Symbol, self).__init__()
        self._sid = sid
    def get_sid(self):
        return self._sid
    def __str__(self):
        return 'symbol = ' + str(self._sid)

class Asset(object):
    def __init__(self,symbol,buying_price,amount):
        super(Asset, self).__init__()
        self._symbol = symbol
        self._buying_price = buying_price
        self._amount = amount
    def get_price(self):
        return self._buying_price
    def get_amount(self):
        return self._amount
    def __str__(self):
        return str(self._symbol) + ' price = ' + str(self._buying_price) + ' amount = ' + str(self._amount)

class MarketOrder(object):
    def __init__(self):
        super(MarketOrder, self).__init__()

class LimitOrder(object):
    def __init__(self,price):
        super(LimitOrder, self).__init__()
        self._price = price
    def get_price(self):
        return self._price

class StopOrder(object):
    def __init__(self,price):
        super(StopOrder, self).__init__()
        self._price = price
    def get_price(self):
        return self._price

class Order(object):
    def __init__(self):
        super(Order, self).__init__()
    def get_id(self):
        return self.__hash__()

class Context(object):
    def __init__(self,trading_system,initial_capital=10000.):
        super(Context, self).__init__()
        self._trading_system = trading_system
        self.portfolio = Portfolio()
        self.initial_capital = initial_capital
        self.capital_used = 0.

    def get_value(self):
        return self._trading_system._do_portfolio_valuation()

    def order(self,symbol,amount,style=MarketOrder()):
        return self._trading_system._order(symbol,amount,style)

    def __str__(self):
        msg = '>>>>>> Context >>>>>\n'
        msg += 'initial_capital = ' + str(self.initial_capital) + '\n'
        msg += 'capital_used = ' + str(self.capital_used) + '\n'
        msg += str(self.portfolio)
        msg += 'portfolio value = ' + str(self.get_value()) + '\n'
        msg += 'portfolio total buying price = ' + str(self.portfolio.get_total_buying_price()) + '\n'
        if self.portfolio.get_total_buying_price() != 0:
            msg += 'portfolio return = ' + str( self.get_value() /  self.portfolio.get_total_buying_price() - 1) + '\n'
        msg += '<<<<<< Context <<<<<<'
        return msg

class Portfolio(object):
    def __init__(self):
        super(Portfolio, self).__init__()
        self._assets = []
    def add_asset(self,asset):
        self._assets.append(asset)
    def remove_asset(self,asset):
        self._assets.remove(asset)
    def get_total_buying_price(self):
        total_price = 0.
        for asset in self._assets:
            total_price += asset.get_price() * asset.get_amount()
        return total_price
    def __str__(self):
        msg = ''
        for asset in self._assets:
            msg += str(asset) + '\n'
        return msg

class TradingSystem(object):
    def __init__(self,**kwargs):
        self._initialize = kwargs.get('initialize')
        self._before_market_open = kwargs.get('before_market_open')
        self._after_market_close = kwargs.get('after_market_close')
        self._context = Context(self)
        self._order_queue = []

    def run(self,data):
        self._data = data
        self._initialize(self._context)
        for i in range(1,self._data.shape[1]-1):

            cut_off_data1 = {}
            cut_off_data2 = {}
            for sym in self._data:
                cut_off_data1[sym] = self._data[sym][:i]
                cut_off_data2[sym] = self._data[sym][:i+1]
            new_data1 = pd.Panel(cut_off_data1)
            new_data2 = pd.Panel(cut_off_data2)

            self._current_time_index = i
            self._before_market_open(self._context,new_data1)
            self._execute_orders()
            self._after_market_close(self._context,new_data2)

    def _order(self,symbol,amount,style=MarketOrder()):
        order = Order()
        order.symbol = symbol
        order.amount = amount
        order.style = style
        self._order_queue.append(order)
        return order.get_id()

    def _do_portfolio_valuation(self):
        print 'evaluation portfolio'
        value = 0.
        for asset in self._context.portfolio._assets:
            close_price = self._data[asset._symbol.get_sid()]['close'][self._current_time_index-1]
            value += asset.get_amount() * close_price
        return value

    def _execute_orders(self):

        for order in self._order_queue:

            open_price = self._data[order.symbol.get_sid()]['open'][self._current_time_index]
            high_price = self._data[order.symbol.get_sid()]['high'][self._current_time_index]
            low_price = self._data[order.symbol.get_sid()]['low'][self._current_time_index]
            close_price = self._data[order.symbol.get_sid()]['close'][self._current_time_index]

            if isinstance(order.style,MarketOrder):
                if order.amount >= 0:
                    slippage = 0.001 + np.random.normal(0,0.0005)  # add some slippage , doesn't care about the impact of the buying
                    adjust_buying_price = open_price + open_price * slippage
                    self._context.capital_used += adjust_buying_price * order.amount
                    asset = Asset(order.symbol,adjust_buying_price,order.amount)
                    self._context.portfolio.add_asset(asset)
                else:
                    pass
            elif isinstance(order.style,LimitOrder):
                if order.amount >= 0:
                    ordered_price = order.style.get_price()
                    if ordered_price <= high_price and low_price <= ordered_price:
                        slippage = 0.001 + np.random.normal(0,0.0005)
                        adjust_buying_price = ordered_price + ordered_price * slippage
                        self._context.capital_used += adjust_buying_price * order.amount
                        asset = Asset(order.symbol,adjust_buying_price,order.amount)
                        self._context.portfolio.add_asset(asset)
                    else:
                        # cancel the order since there is no matched order
                        pass
                else:
                    pass
            elif isinstance(order.style,StopOrder):
                if order.amount >= 0:
                    pass
                else:
                    pass

        self._order_queue = []