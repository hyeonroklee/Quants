
import numpy as np
import pandas as pd
import datetime as dt
import scipy.optimize as opt
import matplotlib.pyplot as plt

from quantom import *

if __name__ == '__main__':
    # cov=[[0.0004,0.0002,0.0002],
    #      [0.0002,0.0004,0.0002],
    #      [0.0002,0.0002,0.0004]]

    d = generate_stocks(n=30)
    close_prices = d['AAPL']['close']
    open_prices = d['AAPL']['open']

    buying_prices = None
    selling_prices = None

    for i in range(len(close_prices)):
        if np.random.randint(0,2) > 0:
            if buying_prices is None:
                buying_prices = pd.DataFrame([close_prices.values[i]],index=[close_prices.index.values[i]])
            else:
                buying_prices = buying_prices.append(pd.DataFrame([close_prices.values[i]],index=[close_prices.index.values[i]]))

    for i in range(len(open_prices)):
        if np.random.randint(0,2) > 0:
            if selling_prices is None:
                selling_prices = pd.DataFrame([open_prices.values[i]],index=[open_prices.index.values[i]])
            else:
                selling_prices = selling_prices.append(pd.DataFrame([open_prices.values[i]],index=[open_prices.index.values[i]]))

    print selling_prices

    # r,s = rsi(d['AAPL']['close'])
    # print r
    #
    # port_weights, port_rets, port_vars = optimize_portfolio(d)
    # print port_weights

    # plt.plot(port_vars,port_rets)
    # plt.show()


    # ret_close_prices = compute_return(close_prices)
    # print len(close_prices),len(ret_close_prices)
    # print np.mean(ret_close_prices), np.var(ret_close_prices)
    # np.cov

    show_chart(d['AAPL'],indicators=None,buying_prices=buying_prices,selling_prices=selling_prices)
    # show_chart(s2)
    # show_chart(s3)