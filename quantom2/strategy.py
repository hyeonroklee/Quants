import numpy as np
import pandas as pd

class Strategy(object):
    def __init__(self,context):
        pass
    def is_enter(self,data):
        pass
    def is_exit(self,data):
        pass
    def plot(self,data,ax):
        pass
    def optimize(self,data):
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
        short_ma_data = pd.rolling_mean(price,window=self._short_ma).dropna()
        long_ma_data = pd.rolling_mean(price,window=self._long_ma).dropna()
        if short_ma_data is None or len(short_ma_data) < 2:
            return False
        if long_ma_data is None or len(long_ma_data) < 2:
            return False
        if short_ma_data.values[-2] < long_ma_data.values[-2] and short_ma_data.values[-1] > long_ma_data.values[-1]:
            return True
        return False
    def is_exit(self,data):
        price = data['Close']
        short_ma_data = pd.rolling_mean(price,window=self._short_ma)
        long_ma_data = pd.rolling_mean(price,window=self._long_ma)
        if short_ma_data is None or len(short_ma_data) < 2:
            return False
        if long_ma_data is None or len(long_ma_data) < 2:
            return False
        if short_ma_data.values[-2] > long_ma_data.values[-2] and short_ma_data.values[-1] < long_ma_data.values[-1]:
            return True
        return False
    def plot(self,data,ax1):
        price = data['Close']
        ma1 = pd.rolling_mean(price,window=self._short_ma).dropna()
        ma2 = pd.rolling_mean(price,window=self._long_ma).dropna()
        ma1.plot(ax=ax1)
        ma2.plot(ax=ax1)
    def optimize(self,data,short_ma_range=[5,6],long_ma_range=[14,15]):
        best_long_ma = None
        best_short_ma = None
        best_return = 0
        from_date = str(data.axes[0][0])
        to_date = str(data.axes[0][-1])
        for short_ma in short_ma_range:
            for long_ma in long_ma_range:
                self.set_params(short_ma,long_ma)
                _from = pd.Timestamp(from_date)
                _to = pd.Timestamp(to_date)
                _delta = pd.Timedelta(days=1)
                buying_price = []
                selling_price = []
                while _from != _to:
                    if self.is_enter(data.loc[:_from,:]):
                        try:
                            buying_price.append(data['Open'][_from+_delta])
                        except Exception as e:
                            pass
#                             print 'optimize error ',str(e)
                    if self.is_exit(data.loc[:_from,:]):
                        try:
                            selling_price.append(data['Open'][_from+_delta])
                        except Exception as e:
                            pass
#                             print 'optimize error ',str(e)
                    _from += _delta
                if np.mean(selling_price)/np.mean(buying_price) > best_return:
                    best_long_ma = long_ma
                    best_short_ma = short_ma
                    best_return = np.mean(selling_price)/np.mean(buying_price)
        print 'optimize : ', best_short_ma,best_long_ma,best_return
        if best_short_ma is not None and best_long_ma is not None:
            self.set_params(best_short_ma,best_long_ma)
        return best_short_ma,best_long_ma
