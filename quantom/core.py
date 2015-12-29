
import numpy as np
import pandas as pd


class MarketOrder(object):
    def __init__(self):
        super(MarketOrder,self).__init__()

class LimitOrder(object):
    def __init__(self,price):
        super(LimitOrder,self).__init__()
        self._price = float(price)

    def get_price(self):
        return self._price

class StopOrder(object):
    def __init__(self,price):
        super(StopOrder,self).__init__()
        self._price = float(price)

    def get_price(self):
        return self._price

class Order(object):
    def __init__(self):
        super(Order,self).__init__()
        pass

    def get_id(self):
        return self.__hash__()

class Symbol(object):
    def __init__(self,sid):
        super(Symbol,self).__init__()
        self._sid = sid

    def get_sid(self):
        return self._sid

    def __eq__(self, other):
        return isinstance(other,Symbol) and other._sid == self._sid

    def __str__(self):
        return 'symbol = %s ' % self._sid

class Asset(object):
    def __init__(self,symbol,amount=0,price=0.):
        super(Asset,self).__init__()
        self._symbol = symbol
        self._avg_price = float(price)
        self._amount = int(amount)

    def add(self,amount,price):
        self._avg_price = ((self._avg_price * self._amount) + (float(price) * amount)) / (self._amount + amount)
        self._amount += amount

    def sub(self,amount):
        self._amount -= amount

    def get_amount(self):
        return self._amount

    def get_symbol(self):
        return self._symbol

    def get_avg_price(self):
        return self._avg_price

    def __str__(self):
        return str(self._symbol) + ' amount = %d ' % self._amount + ' avg = %f ' % self._avg_price

class Portfolio(object):
    def __init__(self):
        super(Portfolio,self).__init__()
        self._assets = {}

    def add_asset(self,symbol,amount,price):
        sid = symbol.get_sid()
        if not self._assets.has_key(sid):
            self._assets[sid] = Asset(symbol,amount,price)
        else:
            self._assets[sid].add(amount,price)

    def sub_asset(self,symbol,amount):
        sid = symbol.get_sid()
        if self._assets.has_key(sid):
            self._assets[sid].sub(amount)
        else:
            raise Exception('No such asset in Portfolio : %s ' % symbol)

    def has_asset(self,symbol):
        sid = symbol.get_sid()
        if self._assets.has_key(sid):
            return True
        else:
            return False

    def get_asset_amount(self,symbol):
        sid = symbol.get_sid()
        if self._assets.has_key(sid):
            return self._assets[sid].get_amount()
        else:
            return 0

    def get_assets(self):
        return self._assets

    def __str__(self):
        msg = ''
        if len(self._assets) > 0:
            for sid in self._assets:
                asset = self._assets[sid]
                msg += str(asset) + '\n'
        else:
            msg += 'no assets in Portfolio'
        return msg


class Context(object):
    def __init__(self,trading_system,initial_capital=10000.):
        super(Context, self).__init__()
        self.portfolio = Portfolio()
        self.initial_capital = initial_capital
        self.cash_used_for_buying = 0.
        self.cash_obtained_from_selling = 0.
        self.cash = initial_capital
        self.do_portfolio_valuation = trading_system._do_portfolio_valuation
        self.order = trading_system._order

    def __str__(self):
        msg = '>>>>>> Context >>>>>\n'
        msg += 'initial_capital = %f ' % self.initial_capital + '\n'
        msg += 'capital_used_for_buying = %f ' % self.cash_used_for_buying + '\n'
        msg += 'capital_obtained_from_selling = %f ' % self.cash_obtained_from_selling + '\n'
        msg += 'cash = %f ' % self.cash + '\n'

        msg += 'portfolio value = %f ' % self.do_portfolio_valuation() + '\n'
        msg += 'total value = %f ' % (self.cash + self.do_portfolio_valuation()) + '\n'
        msg += 'return = %f ' % (((self.cash + self.do_portfolio_valuation()) / self.initial_capital)-1) + '\n'

        assets = self.portfolio.get_assets()
        for symbol in assets:
            msg += '  ' + str(assets[symbol].get_symbol()) + ' ' + str(assets[symbol].get_amount()) + ' ' + str(assets[symbol].get_avg_price()) + '\n'
        msg += '<<<<<< Context <<<<<<'
        return msg

class TradingSystem(object):
    def __init__(self,**kwargs):
        super(TradingSystem,self).__init__()

        self._initialize = kwargs.get('initialize')
        self._before_market_open = kwargs.get('before_market_open')
        self._after_market_close = kwargs.get('after_market_close')

        self._context = Context(self)
        self._current_time_index = 0

        self._order_queue = []
        self._data = []

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

            slippage = np.random.normal(0,0.0005)
            adjust_buying_price = -1.
            adjust_selling_price = -1.
            if isinstance(order.style,MarketOrder):
                adjust_buying_price = open_price + open_price * slippage
                adjust_selling_price = open_price +  open_price * slippage
            elif isinstance(order.style,LimitOrder):
                ordered_price = order.style.get_price()
                if low_price <= ordered_price:
                    adjust_buying_price = ordered_price
                if ordered_price <= high_price:
                    adjust_selling_price = ordered_price
            elif isinstance(order.style,StopOrder):
                pass
            else:
                print 'Not support OrderStyle : %s ' % order.style
                continue

            if order.amount >= 0:
                if adjust_buying_price < 0:
                    print 'buying order hasnt been executed : %s , %s ' % (order.style,adjust_buying_price)
                    continue

                cash_used_for_buying = adjust_buying_price * order.amount
                if cash_used_for_buying <= self._context.cash:
                    self._context.cash_used_for_buying += cash_used_for_buying
                    self._context.cash -= cash_used_for_buying
                    self._context.portfolio.add_asset(order.symbol,order.amount,adjust_buying_price)
                else:
                    print 'not enough cash to buy : %s , amount = %d' % (order.symbol,order.amount)
            else:
                if adjust_selling_price < 0:
                    print 'selling order hasnt been executed : %s , %s ' % (order.style,adjust_selling_price)
                    continue

                order.amount = np.abs(order.amount)
                cash_obtained_from_selling = adjust_selling_price * order.amount
                if self._context.portfolio.has_asset(order.symbol) and self._context.portfolio.get_asset_amount(order.symbol) >= order.amount:
                    self._context.cash_obtained_from_selling += cash_obtained_from_selling
                    self._context.cash += cash_obtained_from_selling
                    self._context.portfolio.sub_asset(order.symbol,order.amount)
                else:
                    print 'not enough shares to sell : %s , amount = %d' % (order.symbol,order.amount)

        self._order_queue = []