
from util import sma,macd,rsi
from abc import ABCMeta,abstractmethod

import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm

class Strategy(object):
    __metaclass__  = ABCMeta

    def __init__(self):
        super(Strategy,self).__init__()

    @abstractmethod
    def isEnter(self,context,data):
        pass

    @abstractmethod
    def isExit(self,context,data):
        pass

class GoldenDeathCross(Strategy):
    def __init__(self,short=5,long=14):
        super(GoldenDeathCross,self).__init__()
        self.short = short
        self.long = long

    def isEnter(self,context,data):
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

    def isEnter(self,context,data):
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

class SVMClassifier(Strategy):
    def __init__(self,training_data,window=10,target=5):
        x = []
        y = []
        prices = training_data['close'].values[1:]
        ret_prices = training_data['close'].pct_change().values[1:]
        for i in range(window,len(prices),window):
            x.append(ret_prices[i-window:i])
            y.append(1 if prices[i-1] < prices[i+target] else 0)
        x = np.array(x)
        y = np.array(y)
        scaler = StandardScaler().fit(x)
        scaled_x = scaler.transform(x)
        self._classifier = svm.SVC()
        self._classifier.fit(scaled_x,y)
        self._scaler = scaler
        self._window = window
        self._target = target
        self._day_after_enter = 0

    def isEnter(self,context,data):
        x = []
        ret_prices = data['close'].pct_change().values[1:]
        if len(ret_prices) >= self._window:
            x.append(ret_prices[len(ret_prices)-self._window:len(ret_prices)])
            x = np.array(x)
            x = self._scaler.transform(x)
            if self._classifier.predict(x)[0] == 1 and self._day_after_enter == 0:
                self._day_after_enter = 1
                return True
        return False

    def isExit(self,context,data):
        if self._day_after_enter > 0:
            if self._day_after_enter == self._target:
                self._day_after_enter = 0
                return True
            else:
                self._day_after_enter += 1
        return False