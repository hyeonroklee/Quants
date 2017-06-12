import source
import datetime as dt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def get_beta_alpha(stock,benchmark,window=28):
    result = []
    merged_data = stock.merge(benchmark, left_index=True, right_index=True)[['Close_x', 'Close_y']]
    for i in range(window, len(merged_data) + 1):
        range_data = merged_data[i - window:i].dropna()
        date = range_data.index[-1]
        ret = range_data['Close_x'].pct_change().dropna().values.reshape(-1, 1)
        index_ret = range_data['Close_y'].pct_change().dropna().values.reshape(-1, 1)
        if len(ret) != len(index_ret):
            print range_data, len(ret), len(index_ret)
        reg = LinearRegression()
        reg.fit(X=index_ret, y=ret)
        r2 = reg.score(X=index_ret, y=ret)
        result.append([date, reg.coef_[0, 0], reg.intercept_[0], r2])

    result = pd.DataFrame(result, columns=['Date', 'Beta', 'Alpha', 'R2'])
    result.set_index(['Date'], inplace=True)
    return result

def get_rsi(stock,window=14):
    def rsi_func(s):
        sum_gain = 0
        sum_loss = 0
        for diff in s[1:] - s[:-1]:
            if diff > 0:
                sum_gain += diff
            else:
                sum_loss += np.abs(diff)
        return float(1 - 1 / (1 + sum_gain / sum_loss))
    return stock['Close'].rolling(window=window, center=False).apply(rsi_func).dropna()

def get_stochastic(stock,window=14):
    def stochastic_func(s):
        diff = np.max(s) - np.min(s)
        loc = s[-1] - np.min(s)
        return loc/diff;
    return stock['Close'].rolling(window=window,center=False).apply(stochastic_func).dropna()

def get_sma(stock,window=5):
    return stock['Close'].rolling(window=window,center=False).mean().dropna()
