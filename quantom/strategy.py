
from util import sma,macd,rsi
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
        if short_ma[len(short_ma)-2] < long_ma[len(long_ma)-2] and short_ma[len(short_ma)-1] > long_ma[len(long_ma)-1]:
            return True
        return False

    def isExit(self,context,data):
        prices = data['close']
        short_ma = sma(prices,self.short,2)
        long_ma = sma(prices,self.long,2)
        if short_ma[len(short_ma)-2] > long_ma[len(long_ma)-2] and short_ma[len(short_ma)-1] < long_ma[len(long_ma)-1]:
            return True
        return False

class MACDCross(Strategy):
    def __init__(self,short=12,long=26,signal=9):
        super(MACDCross,self).__init__()
        self._short = short
        self._long = long
        self._signal = signal

    def isEntry(self,context,data):
        prices = data['close']
        macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(prices,self._short,self._long,self._signal)
        if macd_hist[len(macd_hist)-2] < 0 and macd_hist[len(macd_hist)-1] > 0:
            return True
        return False

    def isExit(self,context,data):
        prices = data['close']
        macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(prices,self._short,self._long,self._signal)
        if macd_hist[len(macd_hist)-2] > 0 and macd_hist[len(macd_hist)-1] < 0:
            return True
        return False
