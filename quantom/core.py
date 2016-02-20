
import numpy as np
import pandas as pd


class MarketOrder(object):
    def __init__(self):
        super(MarketOrder,self).__init__()

    def __str__(self):
        return 'MarketOrder'

class LimitOrder(object):
    def __init__(self,price):
        super(LimitOrder,self).__init__()
        self._price = float(price)

    def get_price(self):
        return self._price

    def __str__(self):
        return 'LimitOrder %f' % self._price

class Order(object):
    def __init__(self):
        super(Order,self).__init__()
        pass

    def get_id(self):
        return self.__hash__()

class Asset(object):
    def __init__(self,symbol,amount=0,price=0):
        super(Asset,self).__init__()
        self._symbol = symbol
        self._avg_price = float(price)
        self._amount = int(amount)
        self._total_profit = 0.
        self._total_buying_price = float(price) * amount
        self._total_selling_price = 0.

    def buy(self,amount,price):
        self._avg_price = ((self._avg_price * self._amount) + (float(price) * amount)) / (self._amount + amount)
        self._amount += amount
        self._total_buying_price += (float(price) * amount)

    def sell(self,amount,price):
        if self._amount < amount:
            raise Exception('Not enough shares : %d < %d' % (self._amount, amount))
        self._amount -= amount
        self._total_profit += (price - self._avg_price) * amount
        self._total_selling_price += (float(price) * amount)

    def get_amount(self):
        return self._amount

    def get_symbol(self):
        return self._symbol

    def get_avg_price(self):
        return self._avg_price

    def get_profit(self):
        return self._total_profit

    def __str__(self):
        return '%s avg_price %f amount %d total_buying_price %f total_selling_price %f total_profit %f' % \
               (self._symbol,self._avg_price, self._amount,self._total_buying_price,self._total_selling_price,self._total_profit)

class Portfolio(object):
    def __init__(self):
        super(Portfolio,self).__init__()
        self._assets = {}

    def buy_asset(self,symbol,amount,price):
        if not self._assets.has_key(symbol):
            self._assets[symbol] = Asset(symbol,amount,price)
        else:
            self._assets[symbol].buy(amount,price)
        return self._assets[symbol]

    def sell_asset(self,symbol,amount,price):
        try:
            self._assets[symbol].sell(amount,price)
            return self._assets[symbol]
        except KeyError:
            raise Exception('No such asset in Portfolio : %s ' % symbol)

    def has_asset(self,symbol):
        if self._assets.has_key(symbol):
            return True
        else:
            return False

    def get_asset_amount(self,symbol):
        if self._assets.has_key(symbol):
            return self._assets[symbol].get_amount()
        else:
            return 0

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
    def __init__(self,trading_system,initial_cash=10000.):
        super(Context, self).__init__()
        self.portfolio = Portfolio()
        self.initial_cash = initial_cash
        self.cash_used_for_buying = 0.
        self.cash_obtained_from_selling = 0.
        self.cash = initial_cash
        self.do_portfolio_valuation = trading_system._do_portfolio_valuation
        self.order = trading_system._order
        self.buying_history = pd.Series([])
        self.selling_history = pd.Series([])

    def __str__(self):
        msg = '>>>>>> Context >>>>>\n'
        msg += 'initial_cash = %f ' % self.initial_cash + '\n'
        msg += 'cash_used_for_buying = %f ' % self.cash_used_for_buying + '\n'
        msg += 'cash_obtained_from_selling = %f ' % self.cash_obtained_from_selling + '\n'
        msg += 'cash = %f ' % self.cash + '\n'

        msg += 'portfolio value = %f ' % self.do_portfolio_valuation() + '\n'
        msg += 'total value = %f ' % (self.cash + self.do_portfolio_valuation()) + '\n'
        msg += 'return = %f ' % (((self.cash + self.do_portfolio_valuation()) / self.initial_cash)-1) + '\n'
        msg += '<<<<<< Context <<<<<<'
        return msg

class TradingSystem(object):
    def __init__(self,**kwargs):
        super(TradingSystem,self).__init__()

        self._initialize = kwargs['initialize']
        self._before_market_open = kwargs['before_market_open']
        self._after_market_close = kwargs['after_market_close']

        self._context = Context(self,initial_cash=kwargs['initial_cash'] if 'initial_cash' in kwargs else 10000.)
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
                cut_off_data1[sym] = self._data[sym][:i]
                cut_off_data2[sym] = self._data[sym][:i+1]
            new_data1 = pd.Panel(cut_off_data1)
            new_data2 = pd.Panel(cut_off_data2)

            self._current_time_index = i
            try:
                self._before_market_open(self._context,new_data1)
            except Exception as e:
                # print '[Error] before_market_open : ' + str(e)
                pass

            try:
                self._execute_orders()
            except Exception as e:
                # print '[Error] execute_orders : ' + str(e)
                pass

            try:
                self._after_market_close(self._context,new_data2)
            except Exception as e:
                # print '[Error] after_market_close : ' + str(e)
                pass

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
            close_price = self._data[asset.get_symbol()]['close'][self._current_time_index]
            value += asset.get_amount() * close_price
        return value

    def _execute_orders(self):

        for order in self._order_queue:

            date = self._data[order.symbol]['open'].index.values[self._current_time_index]
            date_str = pd.to_datetime(str(date)).strftime('%Y-%m-%d')
            open_price = self._data[order.symbol]['open'][self._current_time_index]
            high_price = self._data[order.symbol]['high'][self._current_time_index]
            low_price = self._data[order.symbol]['low'][self._current_time_index]
            close_price = self._data[order.symbol]['close'][self._current_time_index]

            if open_price <=0 or high_price <=0 or low_price <=0 or close_price <=0:
                print 'price can not be under 0'
                continue

            slippage = np.random.normal(0,0.0005)
            adjust_buying_price = -1.
            adjust_selling_price = -1.
            if isinstance(order.style,MarketOrder):
                adjust_buying_price = open_price + open_price * slippage
                if adjust_buying_price < low_price:
                    adjust_buying_price = low_price
                if adjust_buying_price > high_price:
                    adjust_buying_price = high_price
                adjust_selling_price = open_price +  open_price * slippage
                if adjust_selling_price < low_price:
                    adjust_selling_price = low_price
                if adjust_selling_price > high_price:
                    adjust_selling_price = high_price
            elif isinstance(order.style,LimitOrder):
                ordered_price = order.style.get_price()
                if low_price <= ordered_price:
                    if ordered_price <= high_price:
                        adjust_buying_price = ordered_price
                    else:
                        adjust_buying_price = high_price
                if ordered_price <= high_price:
                    if low_price <= ordered_price:
                        adjust_selling_price = ordered_price
                    else:
                        adjust_selling_price = low_price

                print adjust_buying_price,adjust_selling_price

            else:
                print 'Not support OrderStyle : %s ' % order.style
                continue

            if order.amount >= 0:
                if adjust_buying_price < 0:
                    print '(BUY  :%s) buying order hasnt been executed : %s , %s ' % (date_str,order.style,adjust_buying_price)
                    continue

                cash_used_for_buying = adjust_buying_price * order.amount
                if cash_used_for_buying <= self._context.cash:
                    self._context.cash_used_for_buying += cash_used_for_buying
                    self._context.cash -= cash_used_for_buying
                    asset = self._context.portfolio.buy_asset(order.symbol,order.amount,adjust_buying_price)
                    self._context.buying_history = self._context.buying_history.append(pd.Series([adjust_buying_price],index=[date]))
                    print '(BUY  :%s) %s' % (date_str,asset)
                else:
                    print '(BUY  :%s) not enough cash to buy : %s , amount = %d' % (date_str,order.symbol,order.amount)
            else:
                if adjust_selling_price < 0:
                    print '(BUY  :%s) selling order hasnt been executed : %s , %s ' % (date_str,order.style,adjust_selling_price)
                    continue

                order.amount = np.abs(order.amount)
                adjust_selling_price_with_fee = adjust_selling_price - (adjust_selling_price * 0.0033) # tax + transaction fee
                cash_obtained_from_selling = adjust_selling_price_with_fee * order.amount
                if self._context.portfolio.has_asset(order.symbol) and self._context.portfolio.get_asset_amount(order.symbol) >= order.amount:
                    self._context.cash_obtained_from_selling += cash_obtained_from_selling
                    self._context.cash += cash_obtained_from_selling
                    asset = self._context.portfolio.sell_asset(order.symbol,order.amount,adjust_selling_price_with_fee)
                    self._context.selling_history = self._context.selling_history.append(pd.Series([adjust_selling_price],index=[date]))
                    print '(SELL :%s) %s' % (date_str,asset)
                else:
                    print '(SELL :%s) not enough shares to sell : %s , amount = %d' % (date_str,order.symbol,order.amount)

        self._order_queue = []