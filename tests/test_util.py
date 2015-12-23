
import numpy as np
import pandas as pd

from quantom import *

import matplotlib.pyplot as plt
import matplotlib.finance as mfinance
import matplotlib.dates as mdates

if __name__ == '__main__':

    data_size = 200
    data = generate_stocks(n=data_size,price=10.)
    stock_data = data["AAPL"]

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

    macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(close_prices)
    ax1.plot(range(data_size-len(ma_short),data_size),ma_short)
    ax1.plot(range(data_size-len(ma_long),data_size),ma_long)

    ax2.plot(range(data_size-len(macd_line),data_size),macd_line)
    ax2.plot(range(data_size-len(macd_signal),data_size),macd_signal)
    ax2.bar(range(data_size-len(macd_hist),data_size),macd_hist)
    ax2.set_xlim([0,data_size])

    # fig.subplots_adjust(bottom=0.2)

    plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()