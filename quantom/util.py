import source
import datetime as dt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def compute_beta_alpha(stock_price,benchmark_price):
    stock_ret = np.array(stock_price.pct_change().dropna().tolist()).reshape(-1,1)
    bechmark_ret = np.array(benchmark_price.pct_change().dropna().tolist()).reshape(-1,1)
    reg = LinearRegression()
    reg.fit(X=bechmark_ret,y=stock_ret)
    return reg.coef_[0,0], reg.intercept_[0]
