import numpy as np
import pandas as pd
import datetime as dt

class Strategy(object):

    def __init__(self,context):
        pass

    def is_enter(self,data):
        pass

    def is_exit(self,data):
        pass

    def optimize(self,data):
        pass

    def plot(self, data, ax):
        pass

class GDCrossStrategy(Strategy):

    def __init__(self,short_ma=5,long_ma=14):
        self._short_ma = short_ma
        self._long_ma  = long_ma

    def set_params(self,short_ma,long_ma):
        self._short_ma = short_ma
        self._long_ma  = long_ma

    def is_enter(self,data):
        price = data['Close']
        short_ma_data = price.rolling(window=self._short_ma,center=False).mean().dropna()
        long_ma_data = price.rolling(window=self._long_ma,center=False).mean().dropna()

        if short_ma_data is None or len(short_ma_data) < 2:
            return False
        if long_ma_data is None or len(long_ma_data) < 2:
            return False
        if short_ma_data.values[-2] < long_ma_data.values[-2] and short_ma_data.values[-1] > long_ma_data.values[-1]:
            return True
        return False

    def is_exit(self,data):
        price = data['Close']
        short_ma_data = price.rolling(window=self._short_ma,center=False).mean().dropna()
        long_ma_data = price.rolling(window=self._long_ma,center=False).mean().dropna()

        if short_ma_data is None or len(short_ma_data) < 2:
            return False
        if long_ma_data is None or len(long_ma_data) < 2:
            return False
        if short_ma_data.values[-2] > long_ma_data.values[-2] and short_ma_data.values[-1] < long_ma_data.values[-1]:
            return True
        return False

    def optimize(self,data,short_ma_range=[5,6],long_ma_range=[14,15]):
        best_short_ma = None
        best_long_ma = None
        best_odds = 0
        for short_ma in range(short_ma_range[0],short_ma_range[1]+1):
            for long_ma in range(long_ma_range[0],long_ma_range[1]+1):
                self.set_params(short_ma, long_ma)
                odds = self.compute_odds(data)
                if odds > best_odds:
                    best_short_ma = self._short_ma
                    best_long_ma = self._long_ma
                    best_odds = odds
        print 'best_short_ma ', best_short_ma, ' best_long_ma ', best_long_ma, ' best_odds ', best_odds
        return best_short_ma,best_long_ma,best_odds

    def compute_odds(self,data):
        count_win = 0
        count_loss = 0
        is_enter = False
        for i in range(len(data)):
            if self.is_enter(data.ix[:i]):
                enter_close_price = data.ix[i]['Close']
                is_enter = True
            elif self.is_exit(data.ix[:i]) and is_enter:
                exit_close_price = data.ix[i]['Close']
                is_enter = False
                if enter_close_price < exit_close_price:
                    count_win += 1
                else:
                    count_loss += 1
        odds = float(count_win) / (count_loss + count_win)
        print 'short_ma ',self._short_ma, ' long_ma ',self._long_ma, ' odds ',odds
        return odds

    def plot(self,data,ax1):
        price = data['Close']
        ma1 = price.rolling(window=self._short_ma,center=False).mean().dropna()
        ma2 = price.rolling(window=self._long_ma,center=False).mean().dropna()
        ma1.plot(ax=ax1)
        ma2.plot(ax=ax1)