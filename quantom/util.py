import numpy as np

def generate_stock_data(n=250,price=1,pos=2):
    start_price = round(price,pos)
    open_prices = np.array([start_price])
    high_prices = np.array([start_price])
    low_prices = np.array([start_price])
    close_prices = np.array([start_price])

    for i in np.arange(1,n):
        prices = np.array([])
        prices = np.append(prices,round(close_prices[i-1] + close_prices[i-1] * np.random.normal(scale=0.02),pos) )
        prices = np.append(prices,round(prices[0] + prices[0] * np.random.normal(scale=0.03),pos) )
        prices = np.append(prices,round(prices[1] + prices[1] * np.random.normal(scale=0.03),pos) )
        prices = np.append(prices,round(prices[2] + prices[2] * np.random.normal(scale=0.02),pos) )

        open_prices = np.append(open_prices,prices[0])
        high_prices = np.append(high_prices,np.max(prices))
        low_prices = np.append(low_prices,np.min(prices))
        close_prices = np.append(close_prices,prices[3])

    return open_prices,high_prices,low_prices,close_prices


def sma(data,window=5):
    pass

def ema(data,window=5):
    pass