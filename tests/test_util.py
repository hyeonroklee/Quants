
import numpy as np
import pandas as pd
import datetime as dt

from quantom import *

import matplotlib.pyplot as plt
import matplotlib.finance as mfinance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

from matplotlib.finance import quotes_historical_yahoo_ohlc

if __name__ == '__main__':
    cov=[[0.0004,0.0002,0.0002],
         [0.0002,0.0004,0.0002],
         [0.0002,0.0002,0.0004]]
    d = generate_stocks(n=100,cov=cov)
    s1 = d['AAPL']
    s2 = d['GOOG']
    s3 = d['AMZN']

    # m,u,l = bollinger_bands(stock_data['close'])
    #
    # print m[:2]
    # print u[:2]
    # print l[:2]

    show_chart(s1)
    show_chart(s2)
    show_chart(s3)