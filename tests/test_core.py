
from quantom import *

def initialize(context):
    print 'initialize ...'
    context.symbols = [ Symbol('AAPL') , Symbol('AMZN') ]

def before_market_open(context,data):
    print 'before_market_open ...'

def after_market_close(context,data):
    print 'after_market_close ...'

if __name__ == '__main__':

    data = generate_stocks(n=5,price=10.)
    ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    ts.run(data)
    print str(ts._context)

    # # for i in range(5,data.shape[1]):
    # #     print np.sum(data['AAPL']['close'][i-5:i])/5
    # smv5  = sma(data['AAPL']['close'],window=5)
    # smv10 = sma(data['AAPL']['close'],window=10)
    # ma1,ma2,h = macd(data['AAPL']['close'])
    #
    # # ts = TradingSystem(initialize=initialize,before_market_open=before_market_open,after_market_close=after_market_close)
    # # ts.run(data)
    # # print str(ts._context)
    #
    # fig, (ax,ax1) = plt.subplots(2,1)
    # mondays = mdates.WeekdayLocator(mdates.MONDAY)
    # alldays = mdates.DayLocator()
    # weekFormatter = mdates.DateFormatter('%b %d')
    # dayFormatter = mdates.DateFormatter('%d')
    # fig.subplots_adjust(bottom=0.2)
    # ax.xaxis.set_major_locator(mondays)
    # ax.xaxis.set_minor_locator(alldays)
    # ax.xaxis.set_major_formatter(weekFormatter)
    # symbol = 'AAPL'
    # open_prices = data[symbol]['open']
    # high_prices = data[symbol]['high']
    # low_prices = data[symbol]['low']
    # close_prices = data[symbol]['close']
    # mfinance.candlestick2_ohlc(ax, open_prices,high_prices,low_prices, close_prices, width=0.6 , colordown=u'b', colorup=u'r' )
    # ax.plot(range(5,200),smv5)
    # ax.plot(range(10,200),smv10)
    #
    # ax1.bar(range(len(h)),h)
    #
    # ax.xaxis_date()
    # ax.autoscale_view()
    # plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    #
    # plt.show()