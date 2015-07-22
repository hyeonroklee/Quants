import numpy as np
import pandas as pd

def generate_stocks(symbols=['AAPL','GOOG', 'AMZN'],n=250,price=1,pos=2):
    stocks = {}
    for symbol in symbols:
        stocks[symbol] = \
            pd.DataFrame(np.matrix(generate_stock(n,price,pos)).T.tolist(),columns=['open','high','low','close','volume'])
    return pd.Panel(stocks)

def generate_stock(n=250,price=1,pos=2,min_price_bound=0.,initial_volume=1000000):
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
