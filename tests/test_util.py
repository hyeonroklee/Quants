
import numpy as np
import pandas as pd
import datetime as dt
import scipy.optimize as opt
import matplotlib.pyplot as plt

from quantom import *

if __name__ == '__main__':
    stock_prices = pd.Series([1,2,3,4,5,6,7],index=['20110101','20110102','20110103','20110104','20110105','20110106','20110107'],dtype=float)
    market_prices = pd.Series([1,2,3,4,5,6,7],index=['20110101','20110102','20110103','20110104','20110105','20110106','20110107'],dtype=float)

    beta,alpha = calculate_alpha_beta_of_capm(stock_prices,market_prices)
    print beta,alpha