import numpy as np
import pandas as pd

from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.finance as mfinance
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

def sma(data,window=5):
    series = []
    for i in range(window,len(data)):
        series.append( np.sum(data[i-window:i]) / window )
    return pd.Series(series)

def macd(data,long=26,short=12,signal=9,ma=sma):
    long_ma = ma(data,window=long)
    short_ma = ma(data,window=short)[long-short:]

    ma = (np.array(short_ma.tolist()) - np.array(long_ma.tolist()))
    ma1 = ma[signal:]
    ma2 = sma(ma,signal)
    hist = np.array(ma1) - np.array(ma2)

    return ma1,ma2,hist,long_ma,short_ma

def compute_return(prices):
    daily_ret = (prices[1:prices.shape[0],:] - prices[0:prices.shape[0]-1,:]) / prices[0:prices.shape[0]-1,:]
    mean_ret = (daily_ret.T * np.asmatrix(np.ones( [daily_ret.shape[0],1] ))) / daily_ret.shape[0]
    diff = (daily_ret - mean_ret.T)
    cov_ret = (diff.T * diff) / daily_ret.shape[0]
    return daily_ret,mean_ret,cov_ret

def compute_return_risk_pf(mean_ret,cov_ret,w):
    pf_expected_return = mean_ret.T * w
    pf_risk = w.T * cov_ret * w
    return pf_expected_return,pf_risk

def compute_moving_avarage(series):
    s = [0]
    for i in range(1,len(series)-1):
        s.append( (series[i-1] + series[i] + series[i+1]) * (1./3) )
    s.append(0)
    return s

def show_chart(stock_data,**kwargs):

    macd_params = kwargs.get('macd')

    open_prices = stock_data['open']
    high_prices = stock_data['high']
    low_prices = stock_data['low']
    close_prices = stock_data['close']

    fig, (ax1,ax2) = plt.subplots(2,1)

    mondays = mdates.WeekdayLocator(mdates.MONDAY)
    alldays = mdates.DayLocator()
    weekFormatter = mdates.DateFormatter('%b %d')
    dayFormatter = mdates.DateFormatter('%d')

    ax1.xaxis.set_major_locator(mondays)
    ax1.xaxis.set_minor_locator(alldays)
    ax1.xaxis.set_major_formatter(weekFormatter)
    mfinance.candlestick2_ohlc(ax1, open_prices,high_prices,low_prices, close_prices, width=0.6 , colordown=u'b', colorup=u'r' )
    ax1.xaxis_date()
    ax1.autoscale_view()

    if macd_params is not None:
        ma1,ma2,h,long_ma,short_ma = macd(close_prices,macd_params[0],macd_params[1],macd_params[2])
        ax1.plot(range(macd_params[1],macd_params[1]+len(short_ma)),short_ma)
        ax1.plot(range(macd_params[0],macd_params[0]+len(long_ma)),long_ma)

        ax2.plot(range(macd_params[0],macd_params[0]+len(ma1)),ma1)
        ax2.plot(range(macd_params[0]+macd_params[2],macd_params[0]+macd_params[2]+len(ma2)),ma2)
        ax2.bar(range(macd_params[0]+macd_params[2],macd_params[0]+macd_params[2]+len(h)),h)
        ax2.set_xlim([0,200])

    # fig.subplots_adjust(bottom=0.2)

    plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()