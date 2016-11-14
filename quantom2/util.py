import source
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

def sma(data,window=5):
    return pd.rolling_mean(data,window=window).dropna()

def compute_beta_alpha(data,benchmark):
    data_ret = np.array(data.pct_change().dropna().tolist()).reshape(-1,1)
    bechmark_ret = np.array(benchmark.pct_change().dropna().tolist()).reshape(-1,1)
    reg = LinearRegression()
    reg.fit(X=bechmark_ret,y=data_ret)
    return reg.coef_[0,0], reg.intercept_[0]

if __name__ == '__main__':
    ds = source.DataSource()
    data = ds.read_data_from_file('AAPL')
    benchmark = ds.read_data_from_file('SPY')
    print compute_beta_alpha(data['Close'],benchmark['Close'])