
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
    data_size = 250
    data = generate_stocks(n=data_size,price=10.)
    stock_data = data["AAPL"]

    # m,u,l = bollinger_bands(stock_data['close'])
    #
    # print m[:2]
    # print u[:2]
    # print l[:2]

    show_chart(stock_data)