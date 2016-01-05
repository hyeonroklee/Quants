import numpy as np
import pandas as pd
import datetime as dt
import scipy.optimize as opt

import matplotlib.pyplot as plt
import matplotlib.finance as mfinance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

def sma(prices,window=5):
    prices = np.array(prices,dtype=float)
    moving_average = []
    for i in range(window,len(prices)+1):
        moving_average.append(np.mean(prices[i-window:i]))
    return np.array(moving_average)

def macd(prices,long=26,short=12,signal=9,ma=sma):
    ma_long = ma(prices,long)
    ma_short = ma(prices,short)
    macd_line = ma_short[-len(ma_long):] - ma_long
    macd_signal = ma(macd_line,signal)
    macd_hist = macd_line[-len(macd_signal):] - macd_signal
    return macd_line[-len(macd_signal):],macd_signal,macd_hist,ma_long[-len(macd_signal):],ma_short[-len(macd_signal):]

def bollinger_bands(prices,middle=20):
    prices = np.array(prices,dtype=float)
    middle_band = []
    upper_band = []
    lower_band = []
    for i in range(middle,len(prices)+1):
        m = np.mean(prices[i-middle:i])
        s = np.std(prices[i-middle:i])*2
        middle_band.append(m)
        upper_band.append(m+s)
        lower_band.append(m-s)

    return np.array(middle_band),np.array(upper_band),np.array(lower_band)

def rsi(prices,window=14,signal=9):
    rsi_ind = []
    prices = np.array(prices,dtype=float)
    for i in range(window,len(prices)+1):
        diff = prices[i-window+1:i] - prices[i-window:i-1]
        up_avarage = np.mean(diff[diff >= 0] if diff[diff >= 0].size > 0 else 0.01)
        down_avarage = np.mean(diff[diff < 0] if diff[diff < 0].size > 0 else 0.01)
        # print diff,diff[diff >= 0],diff[diff < 0],up_avarage,down_avarage,up_avarage/np.abs(down_avarage),100 - 100/(1+up_avarage/np.abs(down_avarage))
        rsi_ind.append(100 - 100/(1+up_avarage/np.abs(down_avarage)))
    return np.array(rsi_ind),sma(rsi_ind,signal)

def compute_return(prices):
    prices = np.array(prices,dtype=float)
    return (prices[1:] - prices[:-1]) / prices[:-1]

def optimize_portfolio(prices):
    n = len(prices)
    ret_close_prices = []
    r = []
    for symbol in prices:
        ret_close_price = prices[symbol]['close'].pct_change().values[1:]
        ret_close_prices.append(ret_close_price)
        r.append(np.mean(ret_close_price))

    w = np.matrix(np.ones(n)/n)
    r = np.matrix(r).T
    c = np.matrix(np.cov(ret_close_prices))

    def calculate_mean_var(W,R,C):
        return W*R,W*C*W.T

    def fitness(W,R=r,C=c,rf=0.0):
        W = np.matrix(W)
        port_mean,port_var = calculate_mean_var(W,R,C)
        # util = (port_mean - rf) / np.sqrt(port_var)
        return port_var + 100*abs(port_mean-rf)

    rets = []
    vars = []
    ws = []

    for rf in np.linspace(min(r)[0,0],max(r)[0,0],num=20):
        n = 3
        w = np.matrix(np.ones(n)/n)
        _b = [ (0.,1.) for i in range(n)]
        _c = ({'type':'eq', 'fun': lambda W: sum(W)-1. })
        result = opt.minimize(fitness, w, args=(r,c,rf) ,method='SLSQP',constraints=_c,bounds=_b)
        ret,var = calculate_mean_var(np.matrix(result.x),r,c)
        ws.append(result.x)
        rets.append(ret[0,0])
        vars.append(var[0,0])

    return ws,rets,vars

def generate_stocks(symbols=['AAPL','GOOG', 'AMZN'],n=250,price=10.,pos=2,initial_volume=1000000,mean=[0.,0.,0.],cov=[[0.0004,0.,0.],[0.,0.0004,0.],[0.,0.,0.0004]],start_date=dt.datetime.today()):
    stocks = {}
    for symbol in symbols:
        stocks[symbol] = []
    dates = [(start_date + dt.timedelta(days=i)).strftime('%Y%m%d') for i in range(n)]

    for i in np.arange(0,n):
        r = np.random.multivariate_normal(mean,cov,size=4)

        for j in range(len(symbols)):
            prices = []

            prev_price = np.round(price,pos)
            if len(stocks[symbols[j]]) > 0:
                prev_price = stocks[symbols[j]][-1][-2]

            prices.append(max(np.round(prev_price + prev_price * r[0][j],pos),0))
            prices.append(max(np.round(prices[0] + prices[0] * r[1][j],pos),0))
            prices.append(max(np.round(prices[1] + prices[1] * r[2][j],pos),0))
            prices.append(max(np.round(prices[2] + prices[2] * r[3][j],pos),0))

            open_price = prices[0]
            high_price = np.max(prices)
            low_price = np.min(prices)
            close_price = prices[3]
            volume = initial_volume

            stocks[symbols[j]].append([open_price,high_price,low_price,close_price,volume])

    ss = {}
    for symbol in stocks:
        ss[symbol] = pd.DataFrame(stocks[symbol],columns=['open','high','low','close','volumes'],index=dates)

    return pd.Panel(ss)

def generate_stock_prices(n=250,price=1,pos=2,min_price_bound=0.,initial_volume=1000000,start_date=dt.datetime.today()):
    start_price = np.round(price,pos)

    open_prices = [start_price]
    high_prices = [start_price]
    low_prices = [start_price]
    close_prices = [start_price]
    volumes = [initial_volume]

    dates = [ (start_date + dt.timedelta(days=i)).strftime('%Y%m%d') for i in range(n) ]

    for i in np.arange(1,n):
        prices = []
        prices.append(max(np.round(close_prices[i-1] + close_prices[i-1] * np.random.normal(scale=0.02),pos), min_price_bound))
        prices.append(max(np.round(prices[0] + prices[0] * np.random.normal(scale=0.03),pos),min_price_bound) )
        prices.append(max(np.round(prices[1] + prices[1] * np.random.normal(scale=0.03),pos),min_price_bound) )
        prices.append(max(np.round(prices[2] + prices[2] * np.random.normal(scale=0.02),pos),min_price_bound) )

        open_prices = np.append(open_prices,prices[0])
        high_prices = np.append(high_prices,np.max(prices))
        low_prices = np.append(low_prices,np.min(prices))
        close_prices.append(prices[3])
        volumes = np.append(volumes,volumes[i-1])

    return pd.DataFrame(np.matrix([open_prices,high_prices,low_prices,close_prices,volumes]).T.tolist(),columns=['open','high','low','close','volumes'],index=dates)

def show_chart(prices,indicator_type='macd'):

    dates = [ mdates.date2num(dt.datetime.strptime(date,'%Y%m%d')) for date in prices.index.values]
    open_prices = prices['open']
    high_prices = prices['high']
    low_prices = prices['low']
    close_prices = prices['close']
    volumes = prices['volumes']

    chart_data = np.matrix([dates,open_prices,high_prices,low_prices,close_prices]).T.tolist()

    fig = plt.figure()
    ax1 = plt.subplot2grid((5,4),(0,0),rowspan=4,colspan=4)
    mfinance.candlestick_ohlc(ax1,chart_data,width=1,colorup='r',colordown='b')
    ax1.grid(True)
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.ylabel('Stock price')
    ax2 = plt.subplot2grid((5,4),(4,0),sharex=ax1,rowspan=1,colspan=4)
    ax2.grid(True)

    middle,upper,lower = bollinger_bands(close_prices)
    ax1.plot(dates[-len(middle):],middle)
    ax1.plot(dates[-len(upper):],upper)
    ax1.plot(dates[-len(lower):],lower)

    if indicator_type == 'macd':
        macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(close_prices)
        ax1.plot(dates[-len(ma_long):],ma_long)
        ax1.plot(dates[-len(ma_short):],ma_short)

        ax2.plot(dates[-len(macd_line):],macd_line)
        ax2.plot(dates[-len(macd_signal):],macd_signal)
        ax2.bar(dates[-len(macd_hist):],macd_hist)
        ax2.axes.yaxis.set_ticklabels([])

        plt.ylabel('MACD')
    elif indicator_type == 'rsi':
        r,s = rsi(close_prices)
        ax2.plot(dates[-len(r):],r)
        ax2.plot(dates[-len(s):],s)
        plt.ylabel('RSI')
    else:
        plt.ylabel('Volumes')
        ax2.axes.yaxis.set_ticklabels([])

    fig.subplots_adjust(hspace=0)
    plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.setp(ax1.get_xticklabels(),visible=False)
    ax1.set_yticks(ax1.get_yticks()[1:])
    plt.show()
