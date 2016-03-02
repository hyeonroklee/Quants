
from util import sma,macd,rsi
from abc import ABCMeta,abstractmethod

import random
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm

class Strategy(object):
    __metaclass__  = ABCMeta

    def __init__(self):
        super(Strategy,self).__init__()

    @abstractmethod
    def isEnter(self,context,data):
        pass

    @abstractmethod
    def isExit(self,context,data):
        pass

class GoldenDeathCross(Strategy):
    def __init__(self,short=5,long=14):
        super(GoldenDeathCross,self).__init__()
        self._short = short
        self._long = long

    def isEnter(self,context,data):
        prices = data['close']
        short_ma = sma(prices,self._short,2)
        long_ma = sma(prices,self._long,2)
        if short_ma[len(short_ma)-2] < long_ma[len(long_ma)-2] and short_ma[len(short_ma)-1] > long_ma[len(long_ma)-1]:
            return True
        return False

    def isExit(self,context,data):
        prices = data['close']
        short_ma = sma(prices,self._short,2)
        long_ma = sma(prices,self._long,2)
        if short_ma[len(short_ma)-2] > long_ma[len(long_ma)-2] and short_ma[len(short_ma)-1] < long_ma[len(long_ma)-1]:
            return True
        return False

class MACDCross(Strategy):
    def __init__(self,short=12,long=26,signal=9):
        super(MACDCross,self).__init__()
        self._short = short
        self._long = long
        self._signal = signal

    def isEnter(self,context,data):
        prices = data['close']
        macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(prices,self._short,self._long,self._signal)
        if macd_hist[len(macd_hist)-2] < 0 and macd_hist[len(macd_hist)-1] > 0:
            return True
        return False

    def isExit(self,context,data):
        prices = data['close']
        macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(prices,self._short,self._long,self._signal)
        if macd_hist[len(macd_hist)-2] > 0 and macd_hist[len(macd_hist)-1] < 0:
            return True
        return False

class SVMClassifier(Strategy):
    def __init__(self,training_data,window=90,target=10):
        x = []
        y = []
        prices = training_data['close'].values[1:]
        ret_prices = training_data['close'].pct_change().values[1:]
        for i in range(window,len(prices)-target):
            x.append(ret_prices[i-window:i])
            y.append(1 if prices[i] < prices[i+target] else 0)
        x = np.array(x)
        y = np.array(y)
        scaler = StandardScaler().fit(x)
        scaled_x = scaler.transform(x)
        self._classifier = svm.SVC()
        self._classifier.fit(scaled_x,y)
        self._scaler = scaler
        self._window = window
        self._target = target
        self._day_after_enter = 0

    def isEnter(self,context,data):
        x = []
        ret_prices = data['close'].pct_change().values[1:]
        if len(ret_prices) >= self._window:
            x.append(ret_prices[len(ret_prices)-self._window:len(ret_prices)])
            x = np.array(x)
            x = self._scaler.transform(x)
            if self._classifier.predict(x)[0] == 1 and self._day_after_enter == 0:
                self._day_after_enter = 1
                return True
        return False

    def isExit(self,context,data):
        if self._day_after_enter > 0:
            if self._day_after_enter == self._target:
                self._day_after_enter = 0
                return True
            else:
                self._day_after_enter += 1
        return False


class NNClassifier(Strategy):
    def __init__(self,training_data,window=90,target=10):
        data = []
        prices = training_data['close'].values[1:]
        ret_prices = training_data['close'].pct_change().values[1:]
        for i in range(window,len(prices)-target):
            data.append( [ret_prices[i-window:i].reshape(window,1) ,
                         np.array([1 if prices[i] < prices[i+target] else 0])])
        self._classifier = Network([window,window/2,1])
        self._classifier.SGD(data,10,len(data),0.01)
        self._window = window
        self._target = target
        self._day_after_enter = 0

    def isEnter(self,context,data):
        x = []
        ret_prices = data['close'].pct_change().values[1:]
        if len(ret_prices) >= self._window:
            x.append( ret_prices[len(ret_prices)-self._window:len(ret_prices)].reshape(self._window,1) )
            if self._classifier.feedforward(x[0])[0][0] > 0.50 and self._day_after_enter == 0:
                self._day_after_enter = 1
                return True
        return False

    def isExit(self,context,data):
        if self._day_after_enter > 0:
            if self._day_after_enter == self._target:
                self._day_after_enter = 0
                return True
            else:
                self._day_after_enter += 1
        return False

class Network(object):

    def __init__(self, sizes):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a)+b)
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            test_data=None):
        if test_data: n_test = len(test_data)
        n = len(training_data)
        for j in xrange(epochs):
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in xrange(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(mini_batch, eta)
            if test_data:
                print "Epoch {0}: {1} / {2}".format(
                    j, self.evaluate(test_data), n_test)
            else:
                print "Epoch {0} complete".format(j)

    def update_mini_batch(self, mini_batch, eta):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta/len(mini_batch))*nw
                        for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb
                       for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        # backward pass
        delta = self.cost_derivative(activations[-1], y) * \
            sigmoid_prime(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for l in xrange(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def evaluate(self, test_data):
        test_results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)

    def cost_derivative(self, output_activations, y):
        return (output_activations-y)

def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

def sigmoid_prime(z):
    return sigmoid(z)*(1-sigmoid(z))
