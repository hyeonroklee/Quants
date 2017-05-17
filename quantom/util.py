import source
import datetime as dt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def sma(prices,window=5):
    return pd.rolling_mean(prices,window=window).dropna()

def compute_beta_alpha(prices,benchmark):
    data_ret = np.array(prices.pct_change().dropna().tolist()).reshape(-1,1)
    # bechmark_ret = np.array(benchmark.pct_change().dropna().tolist()).reshape(-1,1)
    reg = LinearRegression()
    reg.fit(X=bechmark_ret,y=data_ret)
    return reg.coef_[0,0], reg.intercept_[0]

def compute_return(prices):
    return prices.pct_change().dropna()


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + dt.timedelta(days=4)
    return next_month - dt.timedelta(days=next_month.day)


    def plot(self,symbol):
        prices = self._data[symbol]

        dates = [ mdates.date2num(date) for date in prices.index]
        open_prices = prices['Open']
        high_prices = prices['High']
        low_prices = prices['Low']
        close_prices = prices['Close']
        volumes = prices['Volume'] if 'Volume' in prices.columns else None

        chart_data = np.matrix([dates,open_prices,high_prices,low_prices,close_prices]).T.tolist()

        fig = plt.figure(figsize=(15,8))
        ax1 = plt.subplot2grid((5,4),(0,0),rowspan=4,colspan=4)
        mfinance.candlestick_ohlc(ax1,chart_data,colorup='r',colordown='b',alpha=0.7)
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.ylabel('Price')

        ax2 = plt.subplot2grid((5,4),(4,0),sharex=ax1,rowspan=1,colspan=4)
        ax2.grid(True)

        fig.subplots_adjust(hspace=0)
        plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.setp(ax1.get_xticklabels(),visible=False)
        ax1.set_yticks(ax1.get_yticks()[1:])

        b = np.array(self._buy_history)
        s = np.array(self._sell_history)
        if len(b) > 0:
            idx_b = (b[:,1] == symbol)
            ax1.plot(b[idx_b,0],b[idx_b,2],'ro')
        if len(s) > 0:
            idx_s = (s[:,1] == symbol)
            ax1.plot(s[idx_s,0],s[idx_s,2],'bo')

        return ax1,ax2
