
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
        return isinstance(other,Symbol) and other.get_sid() == self._sid

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
        else:
            raise Exception('No such asset in Portfolio : ' + asset.get_symbol().get_sid())

    def get_assets(self):
        return self._assets

    def __str__(self):
        msg = ''
        if len(self._assets) > 0:
            for symbol in self._assets:
                asset = self._assets[symbol]
                msg += str(asset) + '\n'
        else:
            msg += 'no assets in Portfolio'
        return msg


class Context(object):
    def __init__(self,trading_system,initial_capital=10000.):
        super(Context, self).__init__()
        self._trading_system = trading_system
        self.portfolio = Portfolio()
        self.initial_capital = initial_capital
        self.cash_used_for_buying = 0.
        self.cash_obtained_from_selling = 0.
        self.cash = initial_capital

    def get_portfolio_value(self):
        return self._trading_system._do_portfolio_valuation()

    def order(self,symbol,amount,style=MarketOrder()):
        return self._trading_system._order(symbol,amount,style)

    def __str__(self):
        msg = '>>>>>> Context >>>>>\n'
        msg += 'initial_capital = ' + str(self.initial_capital) + '\n'
        msg += 'capital_used_for_buying = ' + str(self.cash_used_for_buying) + '\n'
        msg += 'capital_obtained_from_selling = ' + str(self.cash_obtained_from_selling) + '\n'
        msg += 'cash = ' + str(self.cash) + '\n'
        msg += 'portfolio value = ' + str(self.get_portfolio_value()) + '\n'
        msg += 'total value = ' + str(self.cash + self.get_portfolio_value()) + '\n'
        msg += 'return = ' + str( ((self.cash + self.get_portfolio_value()) / self.initial_capital) - 1 ) + '\n'
        assets = self.portfolio.get_assets()
        for symbol in assets:
            msg += '  ' + str(assets[symbol].get_symbol()) + ' ' + str(assets[symbol].get_amount()) + ' ' + str(assets[symbol].get_avg_buying_price()) + '\n'
        msg += '<<<<<< Context <<<<<<'
        return msg

class TradingSystem(object):
    def __init__(self,**kwargs):
        self._initialize = kwargs.get('initialize')
        self._before_market_open = kwargs.get('before_market_open')
        self._after_market_close = kwargs.get('after_market_close')
        self._context = Context(self)
        self._order_queue = []
        self._data = []
        self._current_time_index = 0

    def run(self,data):
        self._data = data
        self._initialize(self._context)

        for i in range(1,self._data.shape[1]):

            cut_off_data1 = {}
            cut_off_data2 = {}
            for sym in self._data:
                cut_off_data1[sym] = self._data[sym][:i-1]
                cut_off_data2[sym] = self._data[sym][:i]
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
        value = 0.
        assets = self._context.portfolio.get_assets()
        for symbol in assets:
            asset = assets[symbol]
            close_price = self._data[asset.get_symbol().get_sid()]['close'][self._current_time_index]
            value += asset.get_amount() * close_price
        return value

    def _execute_orders(self):

        for order in self._order_queue:

            open_price = self._data[order.symbol.get_sid()]['open'][self._current_time_index]
            high_price = self._data[order.symbol.get_sid()]['high'][self._current_time_index]
            low_price = self._data[order.symbol.get_sid()]['low'][self._current_time_index]
            close_price = self._data[order.symbol.get_sid()]['close'][self._current_time_index]

            if open_price <=0 or high_price <=0 or low_price <=0 or close_price <=0:
                print 'price can not be under 0'
                continue

            print str(order.symbol.get_sid()) + ' ' + str(open_price) + ' ' + str(high_price) + ' ' + str(low_price) + ' ' + str(close_price)

            slippage = np.random.normal(0,0.0005)
            adjust_buying_price = -1.
            adjust_selling_price = -1.
            if isinstance(order.style,MarketOrder):
                adjust_buying_price = open_price + open_price * slippage
                adjust_selling_price = open_price +  open_price * slippage
            elif isinstance(order.style,LimitOrder):
                ordered_price = order.style.get_price()
                if low_price <= ordered_price:
                    adjust_buying_price = ordered_price + ordered_price * slippage
                if ordered_price <= high_price:
                    adjust_selling_price = ordered_price + ordered_price * slippage
            elif isinstance(order.style,StopOrder):
                pass
            else:
                raise Exception('Not support OrderStyle : ' + str(order.style))

            if order.amount >= 0:
                if adjust_buying_price < 0:
                    continue

                cash_used_for_buying = adjust_buying_price * order.amount
                if cash_used_for_buying <= self._context.cash:
                    self._context.cash_used_for_buying += cash_used_for_buying
                    self._context.cash -= cash_used_for_buying
                    asset = Asset(order.symbol,order.amount,adjust_buying_price)
                    self._context.portfolio.add_asset(asset)
                else:
                    print 'not enough cash to buy : ' + str(order.symbol) + ' amount = ' + str(order.amount)
            else:
                if adjust_selling_price < 0:
                    continue

                order.amount = np.abs(order.amount)
                cash_obtained_from_selling = adjust_selling_price * order.amount
                if self._context.portfolio.get_assets().has_key(order.symbol) and self._context.portfolio.get_assets()[order.symbol].get_amount() >= order.amount:
                    self._context.cash_obtained_from_selling += cash_obtained_from_selling
                    self._context.cash += cash_obtained_from_selling
                    asset = Asset(order.symbol,order.amount,adjust_selling_price)
                    self._context.portfolio.remove_asset(asset)
                else:
                    print 'not enough shares to sell : ' + str(order.symbol) + ' amount = ' + str(order.amount)

            # if isinstance(order.style,MarketOrder):
            #     if order.amount >= 0:
            #         slippage = 0.001 + np.random.normal(0,0.0005)
            #         adjust_buying_price = open_price + open_price * slippage
            #         cash_used_for_buying = adjust_buying_price * order.amount
            #         if cash_used_for_buying <= self._context.cash:
            #             self._context.cash_used_for_buying += cash_used_for_buying
            #             self._context.cash -= cash_used_for_buying
            #             asset = Asset(order.symbol,order.amount,adjust_buying_price)
            #             self._context.portfolio.add_asset(asset)
            #         else:
            #             print 'not enough cash to buy : ' + str(order.symbol) + ' amount = ' + str(order.amount)
            #     else:
            #         order.amount = np.abs(order.amount)
            #         slippage = -0.001 + np.random.normal(0,0.0005)
            #         adjust_selling_price = open_price + open_price * slippage
            #         cash_obtained_from_selling = adjust_selling_price * order.amount
            #         if self._context.portfolio._assets.has_key(order.symbol) and self._context.portfolio._assets[order.symbol].get_amount() >= order.amount:
            #             self._context.cash_obtained_from_selling += cash_obtained_from_selling
            #             self._context.cash += cash_obtained_from_selling
            #             asset = Asset(order.symbol,np.abs(order.amount),adjust_selling_price)
            #             self._context.portfolio.remove_asset(asset)
            #         else:
            #             print 'not enough shares to sell : ' + str(order.symbol) + ' amount = ' + str(order.amount)
            # elif isinstance(order.style,LimitOrder):
            #     if order.amount >= 0:
            #         ordered_price = order.style.get_price()
            #     else:
            #         order.amount = np.abs(order.amount)
            #         ordered_price = order.style.get_price()

            # if isinstance(order.style,MarketOrder):
            #     if order.amount >= 0:
            #         slippage = 0.001 + np.random.normal(0,0.0005)  # add some slippage , doesn't care about the impact of the buying
            #         adjust_buying_price = open_price + open_price * slippage
            #
            #         self._context.cash_used_for_buying += adjust_buying_price * order.amount
            #         self._context.cash -= self._context.cash_used_for_buying
            #         asset = Asset(order.symbol,order.amount,adjust_buying_price)
            #         self._context.portfolio.add_asset(asset)
            #     else:
            #         slippage = -0.001 + np.random.normal(0,0.0005)  # add some slippage , doesn't care about the impact of the buying
            #         adjust_selling_price = open_price + open_price * slippage
            #
            #         self._context.cash_obtained_from_selling += adjust_selling_price * np.abs(order.amount)
            #         self._context.cash += self._context.cash_obtained_from_selling
            #         asset = Asset(order.symbol,np.abs(order.amount),adjust_selling_price)
            #         self._context.portfolio.remove_asset(asset)
            # elif isinstance(order.style,LimitOrder):
            #     if order.amount >= 0:
            #         ordered_price = order.style.get_price()
            #         if ordered_price <= high_price and low_price <= ordered_price:
            #             slippage = 0.001 + np.random.normal(0,0.0005)
            #             adjust_buying_price = ordered_price + ordered_price * slippage
            #
            #             self._context.cash_used_for_buying += adjust_buying_price * order.amount
            #             self._context.cash -= self._context.cash_used_for_buying
            #             asset = Asset(order.symbol,order.amount,adjust_buying_price)
            #             self._context.portfolio.add_asset(asset)
            #         else:
            #             print 'cancel the order since there is no matched order ... : ' + str(order.symbol) + ' amount = ' + str(order.amount)
            #     else:
            #         if self._context.portfolio._assets.has_key(order.symbol) and self._context.portfolio._assets[order.symbol].get_amount() >= order.amount:
            #             ordered_price = order.style.get_price()
            #             if ordered_price <= high_price and low_price <= ordered_price:
            #                 slippage = -0.001 + np.random.normal(0,0.0005)
            #                 adjust_selling_price = ordered_price + ordered_price * slippage
            #
            #                 self._context.cash_obtained_from_selling += adjust_selling_price * np.abs(order.amount)
            #                 self._context.cash += self._context.cash_obtained_from_selling
            #                 asset = Asset(order.symbol,np.abs(order.amount),adjust_selling_price)
            #                 self._context.portfolio.remove_asset(asset)
            #             else:
            #                 print 'cancel the order since there is no matched order ... : ' + str(order.symbol) + ' amount = ' + str(order.amount)
            #         else:
            #             print 'Can not execute order ... : ' + str(order.symbol) + ' amount = ' + str(order.amount)
            # elif isinstance(order.style,StopOrder):
            #     if order.amount >= 0:
            #         pass
            #     else:
            #         pass

        self._order_queue = []