
import numpy as np
import pandas as pd

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

class Symbol(object):
    def __init__(self,sid):
        super(Symbol, self).__init__()
        self._sid = sid
    def get_sid(self):
        return self._sid
    def __eq__(self, other):
        return isinstance(other,Symbol) and other._sid == self._sid
    def __str__(self):
        return 'symbol = ' + str(self._sid)

class Asset(object):
    def __init__(self,symbol,amount,buying_price):
        super(Asset, self).__init__()
        self._symbol = symbol
        self._amount = amount
        self._avg_buying_price = buying_price
    def add_amount(self,amount,buying_price):
        self._avg_buying_price = ((self._avg_buying_price * self._amount) + (buying_price * amount)) / (self._amount + amount)
        self._amount += amount
    def remove_amount(self,amount):
        self._amount -= amount
    def get_amount(self):
        return self._amount
    def get_symbol(self):
        return self._symbol
    def get_avg_buying_price(self):
        return self._avg_buying_price
    def __str__(self):
        return str(self._symbol) + ' amount = ' + str(self._amount) + ' avg = ' + str(self._avg_buying_price)

class Portfolio(object):
    def __init__(self):
        super(Portfolio, self).__init__()
        self._assets = {}
    def add_asset(self,asset):
        if not self._assets.has_key(asset.get_symbol()):
            self._assets[asset.get_symbol()] = asset
        else:
            self._assets[asset.get_symbol()].add_amount(asset.get_amount(),asset.get_avg_buying_price())
    def remove_asset(self,asset):
        if self._assets.has_key(asset.get_symbol()):
            self._assets[asset.get_symbol()].remove_amount(asset.get_amount())

    def get_total_buying_price(self):
        total_price = 0.
        for symbol in self._assets:
            asset = self._assets[symbol]
            total_price += asset.get_avg_buying_price() * asset.get_amount()
        return total_price
    def __str__(self):
        msg = ''
        for symbol in self._assets:
            asset = self._assets[symbol]
            msg += str(asset) + '\n'
        return msg

class Context(object):
    def __init__(self,trading_system,initial_capital=10000.):
        super(Context, self).__init__()
        self._trading_system = trading_system
        self.portfolio = Portfolio()
        self.initial_capital = initial_capital
        self.capital_used_for_buying = 0.
        self.capital_obtained_from_selling = 0.
        self.cash = initial_capital

    def get_value(self):
        return self._trading_system._do_portfolio_valuation()

    def order(self,symbol,amount,style=MarketOrder()):
        return self._trading_system._order(symbol,amount,style)

    def __str__(self):
        msg = '>>>>>> Context >>>>>\n'
        msg += 'initial_capital = ' + str(self.initial_capital) + '\n'
        msg += 'capital_used_for_buying = ' + str(self.capital_used_for_buying) + '\n'
        msg += 'capital_obtained_from_selling = ' + str(self.capital_obtained_from_selling) + '\n'
        msg += str(self.portfolio)
        msg += 'portfolio value = ' + str(self.get_value()) + '\n'
        msg += 'portfolio total buying price = ' + str(self.portfolio.get_total_buying_price()) + '\n'
        if self.portfolio.get_total_buying_price() != 0:
            msg += 'portfolio return = ' + str( self.get_value() /  self.portfolio.get_total_buying_price() - 1) + '\n'
        msg += '<<<<<< Context <<<<<<'
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
        for symbol in self._context.portfolio._assets:
            asset = self._context.portfolio._assets[symbol]
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
                    self._context.cash -= adjust_buying_price * order.amount

                    self._context.capital_used_for_buying += adjust_buying_price * order.amount
                    asset = Asset(order.symbol,adjust_buying_price,order.amount)
                    self._context.portfolio.add_asset(asset)
                else:
                    slippage = -0.001 + np.random.normal(0,0.0005)  # add some slippage , doesn't care about the impact of the buying
                    adjust_selling_price = open_price + open_price * slippage
                    self._context.cash += adjust_selling_price * order.amount

                    self._context.capital_obtained_from_selling += adjust_selling_price * order.amount
                    asset = Asset(order.symbol,adjust_selling_price,order.amount)
                    self._context.portfolio.remove_asset(asset)
            elif isinstance(order.style,LimitOrder):
                if order.amount >= 0:
                    ordered_price = order.style.get_price()
                    if ordered_price <= high_price and low_price <= ordered_price:
                        slippage = 0.001 + np.random.normal(0,0.0005)
                        adjust_buying_price = ordered_price + ordered_price * slippage
                        self._context.capital_used_for_buying += adjust_buying_price * order.amount
                        asset = Asset(order.symbol,adjust_buying_price,order.amount)
                        self._context.portfolio.add_asset(asset)
                    else:
                        # cancel the order since there is no matched order
                        pass
                else:
                    if self._context.portfolio._assets.has_key(order.symbol) and self._context.portfolio._assets[order.symbol].get_amount() >= order.amount:
                        ordered_price = order.style.get_price()
                        if ordered_price <= high_price and low_price <= ordered_price:
                            slippage = -0.001 + np.random.normal(0,0.0005)
                            adjust_selling_price = ordered_price + ordered_price * slippage
                            self._context.capital_obtained_from_selling += adjust_selling_price * order.amount
                            asset = Asset(order.symbol,adjust_selling_price,np.abs(order.amount))
                            self._context.portfolio.remove_asset(asset)
                        else:
                            # cancel the order since there is no matched order
                            pass
                    else:
                        print 'Can not execute order ...'
            elif isinstance(order.style,StopOrder):
                if order.amount >= 0:
                    pass
                else:
                    pass

        self._order_queue = []