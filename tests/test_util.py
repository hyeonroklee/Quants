
import numpy as np
import pandas as pd
import datetime as dt
import scipy.optimize as opt
import matplotlib.pyplot as plt

from quantom import *

if __name__ == '__main__':
    d1 = get_stock_prices_from_csv('../data/stocks/a.csv')
    d2 = generate_stock_prices()