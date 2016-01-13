
from util import sma
from abc import ABCMeta,abstractmethod

class Strategy(object):
    __metaclass__  = ABCMeta

    def __init__(self):
        super(Strategy,self).__init__()

    @abstractmethod
    def isEntry(self,context,data):
        pass

    @abstractmethod
    def isExit(self,context,data):
        pass

class GoldenDeathCross(Strategy):
    def __init__(self,short=5,long=14):
        super(GoldenDeathCross,self).__init__()
        self.short = short
        self.long = long

    def isEntry(self,context,data):
        prices = data['close']
        short_ma = sma(prices,self.short,2)
        long_ma = sma(prices,self.long,2)
        if short_ma[0] < long_ma[0] and short_ma[1] > long_ma[1]:
            return True
        return False

    def isExit(self,context,data):
        prices = data['close']
        short_ma = sma(prices,self.short,2)
        long_ma = sma(prices,self.long,2)
        if short_ma[0] > long_ma[0] and short_ma[1] < long_ma[1]:
            return True
        return False

