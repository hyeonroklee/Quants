import numpy as np
import pandas as pd

def sma(prices,window=5):
    prices = np.array(prices,dtype=float)
    moving_average = []
    for i in range(window,len(prices)+1):
        moving_average.append(np.sum(prices[i-window:i]) / np.float(window) )
    return np.array(moving_average)

def macd(prices,long=26,short=12,signal=9,ma=sma):
    ma_long = ma(prices,long)
    ma_short = ma(prices,short)
    macd_line = ma_short[-len(ma_long):] - ma_long
    macd_signal = ma(macd_line,signal)
    macd_hist = macd_line[-len(macd_signal):] - macd_signal
    return macd_line[-len(macd_signal):],macd_signal,macd_hist,ma_long[-len(macd_signal):],ma_short[-len(macd_signal):]

def bollinger_bands():
    pass

def compute_return(prices):
    prices = np.array(prices,dtype=float)
    return (prices[1:] - prices[:-1]) / prices[:-1]


def generate_stocks(symbols=['AAPL','GOOG', 'AMZN'],n=250,price=1,pos=2):
    stocks = {}
    for symbol in symbols:
        stocks[symbol] = \
            pd.DataFrame(np.matrix(generate_stock_prices(n,price,pos)).T.tolist(),columns=['open','high','low','close','volume'])
    return pd.Panel(stocks)

def generate_stock_prices(n=250,price=1,pos=2,min_price_bound=0.,initial_volume=1000000):
    start_price = np.round(price,pos)
    open_prices = np.array([start_price])
    high_prices = np.array([start_price])
    low_prices = np.array([start_price])
    close_prices = np.array([start_price])
    volumes = np.array([initial_volume])

    for i in np.arange(1,n):
        prices = np.array([])
        prices = np.append(prices, max(np.round(close_prices[i-1] + close_prices[i-1] * np.random.normal(scale=0.02),pos),min_price_bound) )
        prices = np.append(prices, max(np.round(prices[0] + prices[0] * np.random.normal(scale=0.03),pos),min_price_bound) )
        prices = np.append(prices, max(np.round(prices[1] + prices[1] * np.random.normal(scale=0.03),pos),min_price_bound) )
        prices = np.append(prices, max(np.round(prices[2] + prices[2] * np.random.normal(scale=0.02),pos),min_price_bound) )

        open_prices = np.append(open_prices,prices[0])
        high_prices = np.append(high_prices,np.max(prices))
        low_prices = np.append(low_prices,np.min(prices))
        close_prices = np.append(close_prices,prices[3])
        volumes = np.append(volumes,volumes[i-1])
    return open_prices,high_prices,low_prices,close_prices,volumes

def show_chart(**kwargs):
    pass