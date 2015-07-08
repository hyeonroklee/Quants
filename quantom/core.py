
class Symbol(object):
    def __init__(self,sid):
        super(Symbol, self).__init__()
        self._sid = sid
    def get_sid(self):
        return self._sid
    def __str__(self):
        return 'symbol = ' + str(self._sid)

class Asset(object):
    def __init__(self,symbol,price,amount):
        super(Asset, self).__init__()
        self._symbol = symbol
        self._price = price
        self._amount = amount
    def get_price(self):
        return self._price
    def get_amount(self):
        return self._amount
    def __str__(self):
        return str(self._symbol) + ' price = ' + str(self._price) + ' amount = ' + str(self._amount)

class Context(object):
    def __init__(self,initial_capital=10000.):
        super(Context, self).__init__()
        self.portfolio = Portfolio()
        self.initial_capital = initial_capital
        self.capital_used = 0.
    def __str__(self):
        msg = '>>>>>> Context >>>>>\n'
        msg += 'initial_capital = ' + str(self.initial_capital) + '\n'
        msg += 'capital_used = ' + str(self.capital_used) + '\n'
        msg += str(self.portfolio)
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
    def __str__(self):
        msg = ''
        for asset in self._assets:
            msg += str(asset) + '\n'
        return msg

class MarketOrder(object):
    def __init__(self):
        super(MarketOrder, self).__init__()

class LimitOrder(object):
    def __init__(self,price):
        super(LimitOrder, self).__init__()

class StopOrder(object):
    def __init__(self,price):
        super(StopOrder, self).__init__()

class Order(object):
    def __init__(self):
        super(Order, self).__init__()


class TradingSystem(object):
    def __init__(self,**kwargs):
        self._initialize = kwargs.get('initialize')
        self._handle_data = kwargs.get('handle_data')
        self._before_market_open = kwargs.get('before_market_open')
        self._context = Context()
        self._order_queue = []

    def run(self,data):
        self._data = data
        self._initialize(self._context)
        for i in range(len(self._data)):
            self._current_index = i
            self._before_market_open(self._context)
            self._execute_orders()
            self._handle_data(self._context,self._data[:i+1])

    def order(self,symbol,amount,style=MarketOrder()):
        order = Order()
        order.symbol = symbol
        order.amount = amount
        order.style = style
        self._order_queue.append(order)

    def _execute_orders(self):

        open_price = self._data['open'][self._current_index]
        high_price = self._data['high'][self._current_index]
        low_price = self._data['low'][self._current_index]
        close_price = self._data['close'][self._current_index]

        for order in self._order_queue:
            if isinstance(order.style,MarketOrder):
                if order.amount >= 0:
                    print 'buying ... '
                    adjust_buying_price = open_price # add some slippage
                    self._context.capital_used += adjust_buying_price * order.amount
                    asset = Asset(order.symbol,adjust_buying_price,order.amount)
                    self._context.portfolio.add_asset(asset)
                else:
                    pass
            elif isinstance(order.style,LimitOrder):
                if order.amount >= 0:
                    pass
                else:
                    pass
            elif isinstance(order.style,StopOrder):
                if order.amount >= 0:
                    pass
                else:
                    pass

        self._order_queue = []