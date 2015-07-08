
class Asset(object):
    def __init__(self,sid):
        super(Asset, self).__init__()
        self._sid = sid

    def get_sid(self):
        return self._sid

    def __str__(self):
        return 'sid = ' + str(self._sid)

class Context(object):
    def __init__(self):
        super(Context, self).__init__()
        self.portfolio = Portfolio()

class Portfolio(object):
    def __init__(self):
        super(Portfolio, self).__init__()

class TradingSystem(object):
    def __init__(self,**kwargs):
        self._initialize = kwargs.get('initialize')
        self._handle_data = kwargs.get('handle_data')
        self._context = Context()

    def run(self,data):
        self._data = data
        self._initialize(self._context)
        for i in range(len(self._data)):
            self._handle_data(self._context,self._data[:i+1])

    def order(self,asset,amount):
        print str(asset) + ' ' + amount + ' shares are ordered'
        pass