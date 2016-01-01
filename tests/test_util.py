
import numpy as np
import pandas as pd
import datetime as dt
import scipy.optimize as opt
import matplotlib.pyplot as plt

from quantom import *

if __name__ == '__main__':
    cov=[[0.0004,0.0002,0.0002],
         [0.0002,0.0004,0.0002],
         [0.0002,0.0002,0.0004]]
    d = generate_stocks(n=100)

    port_rets, port_vars = optimize_portfolio(d)
    plt.plot(port_vars,port_rets)
    plt.show()


    # ret_close_prices = compute_return(close_prices)
    # print len(close_prices),len(ret_close_prices)
    # print np.mean(ret_close_prices), np.var(ret_close_prices)
    # np.cov

    # show_chart(s1)
    # show_chart(s2)
    # show_chart(s3)