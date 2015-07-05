

class TradingSystem():
    def __init__(self,**kwargs):
        self._initialize = kwargs.get('initialize')
        self._handle_data = kwargs.get('handle_data')

    def run(self,data):
        self._data = data
        self._initialize(self)
        for i in range(len(self._data)):
            self._handle_data(self,self._data[:i+1])