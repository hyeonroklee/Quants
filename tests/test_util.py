
from quantom import *

if __name__ == '__main__':

    # sma test cases
    prices = [1,2,3,4]
    t1 = sma(prices)
    assert t1 is not None and len(t1) == 0
    t2 = sma(prices,4)
    assert t2 is not None and len(t2) == 1 and t2[0] == 2.5
    t3 = sma(prices,2,1)
    assert t3 is not None and len(t3) == 1 and t3[0] == 3.5

    # ema test cases
    prices = [1,32,4,8,16,32,64]
    print ema(prices)
    print sma(prices)
    print willr(prices,2)
    print rocr(prices,2)
