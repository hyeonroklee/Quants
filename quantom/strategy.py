
from util import sma,macd,rsi
from abc import ABCMeta,abstractmethod

import random
import json
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier

class Strategy(object):
    __metaclass__  = ABCMeta

    def __init__(self,context):
        super(Strategy,self).__init__()
        self._context = context

    @abstractmethod
    def is_enter(self,data):
        pass

    @abstractmethod
    def is_exit(self,data):
        pass

class GoldenDeathCross(Strategy):
    def __init__(self,context,short=5,long=14):
        super(GoldenDeathCross,self).__init__(context)
        self._short = short
        self._long = long

    def is_enter(self,data):
        if self._short >= self._long:
            return False
        try:
            prices = data['close']
            short_ma = sma(prices,self._short,2)
            long_ma = sma(prices,self._long,2)
            if short_ma[len(short_ma)-2] < long_ma[len(long_ma)-2] and short_ma[len(short_ma)-1] > long_ma[len(long_ma)-1]:
                return True
            return False
        except Exception as e:
            return False

    def is_exit(self,data):
        if self._short >= self._long:
            return False
        try:
            prices = data['close']
            short_ma = sma(prices,self._short,2)
            long_ma = sma(prices,self._long,2)
            if short_ma[len(short_ma)-2] > long_ma[len(long_ma)-2] and short_ma[len(short_ma)-1] < long_ma[len(long_ma)-1]:
                return True
            return False
        except Exception as e:
            return False

class MACDCross(Strategy):
    def __init__(self,context,short=12,long=26,signal=9):
        super(MACDCross,self).__init__(context)
        self._short = short
        self._long = long
        self._signal = signal

    def is_enter(self,data):
        if self._short >=  self._long:
            return False
        try:
            prices = data['close']
            macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(prices,self._short,self._long,self._signal)
            if len(macd_hist) == 0 or np.any(np.isnan(macd_hist)):
                return False
            if macd_hist[len(macd_hist)-2] < 0 and macd_hist[len(macd_hist)-1] > 0:
                return True
            return False
        except Exception as e:
            return False

    def is_exit(self,data):
        if self._short >=  self._long:
            return False
        try:
            prices = data['close']
            macd_line,macd_signal,macd_hist,ma_long,ma_short = macd(prices,self._short,self._long,self._signal)
            if len(macd_hist) == 0 or np.any(np.isnan(macd_hist)):
                return False
            if macd_hist[len(macd_hist)-2] > 0 and macd_hist[len(macd_hist)-1] < 0:
                return True
            return False
        except Exception as e:
            return False

class SVMClassifier(Strategy):
    def __init__(self,context,training_data,window=90,target=10):
        super(SVMClassifier, self).__init__(context)
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

    def is_enter(self,data):
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

    def is_exit(self,data):
        if self._day_after_enter > 0:
            if self._day_after_enter == self._target:
                self._day_after_enter = 0
                return True
            else:
                self._day_after_enter += 1
        return False

class KNNClassifier(Strategy):
    def __init__(self,context,training_data,window=90,target=10):
        super(KNNClassifier,self).__init__(context)

    def is_enter(self,data):
        pass

    def is_exit(self,data):
        pass

class NNClassifier(Strategy):
    def __init__(self,context,training_data,window=90,target=10):
        super(NNClassifier,self).__init__(context)
        data = []
        prices = training_data['close'].values[1:]
        ret_prices = training_data['close'].pct_change().values[1:]
        for i in range(window,len(prices)-target):
            data.append([
                ret_prices[i-window:i].reshape(window,1) ,
                np.array( [[0],[1]] if prices[i-1] < prices[i-1+target] else [[1],[0]] )
            ])

        layers = [window,window/2,2]
        self._classifier = Network(layers)
        self._classifier.SGD(data,10,len(data)/2,0.05,monitor_training_accuracy=True,monitor_training_cost=True)
        self._window = window
        self._target = target
        self._day_after_enter = 0

    def is_enter(self,data):
        ret_prices = data['close'].pct_change().values[1:]

        # print ret_prices

        if len(ret_prices) >= self._window:
            x = ret_prices[len(ret_prices)-self._window:len(ret_prices)].reshape(self._window,1)
            # print "x = ",x
            # print self._classifier.feedforward(x),np.argmax(self._classifier.feedforward(x))
            if np.argmax(self._classifier.feedforward(x)) == 1 and self._day_after_enter == 0:
                self._day_after_enter = 1
                return True
        return False

    def is_exit(self,data):
        if self._day_after_enter > 0:
            if self._day_after_enter == self._target:
                self._day_after_enter = 0
                return True
            else:
                self._day_after_enter += 1
        return False


class QuadraticCost(object):

    @staticmethod
    def fn(a, y):
        return 0.5*np.linalg.norm(a-y)**2

    @staticmethod
    def delta(z, a, y):
        return (a-y) * sigmoid_prime(z)


class CrossEntropyCost(object):

    @staticmethod
    def fn(a, y):
        return np.sum(np.nan_to_num(-y*np.log(a)-(1-y)*np.log(1-a)))

    @staticmethod
    def delta(z, a, y):
        return (a-y)

class Network(object):

    def __init__(self, sizes, cost=CrossEntropyCost):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.default_weight_initializer()
        self.cost=cost

    def default_weight_initializer(self):
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x)/np.sqrt(x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def large_weight_initializer(self):
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def feedforward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a)+b)
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            lmbda = 0.0,
            evaluation_data=None,
            monitor_evaluation_cost=False,
            monitor_evaluation_accuracy=False,
            monitor_training_cost=False,
            monitor_training_accuracy=False):
        if evaluation_data: n_data = len(evaluation_data)
        n = len(training_data)
        evaluation_cost, evaluation_accuracy = [], []
        training_cost, training_accuracy = [], []
        for j in xrange(epochs):
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in xrange(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(
                    mini_batch, eta, lmbda, len(training_data))
            # print "Epoch %s training complete" % j
            if monitor_training_cost:
                cost = self.total_cost(training_data, lmbda)
                training_cost.append(cost)
                print "Cost on training data: {}".format(cost)
            if monitor_training_accuracy:
                accuracy = self.accuracy(training_data, convert=True)
                training_accuracy.append(accuracy)
                print "Accuracy on training data: {} / {}".format(
                    accuracy, n)
            if monitor_evaluation_cost:
                cost = self.total_cost(evaluation_data, lmbda, convert=True)
                evaluation_cost.append(cost)
                print "Cost on evaluation data: {}".format(cost)
            if monitor_evaluation_accuracy:
                accuracy = self.accuracy(evaluation_data)
                evaluation_accuracy.append(accuracy)
                print "Accuracy on evaluation data: {} / {}".format(
                    self.accuracy(evaluation_data), n_data)
            print
        return evaluation_cost, evaluation_accuracy, \
            training_cost, training_accuracy

    def update_mini_batch(self, mini_batch, eta, lmbda, n):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [(1-eta*(lmbda/n))*w-(eta/len(mini_batch))*nw
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
        delta = (self.cost).delta(zs[-1], activations[-1], y)
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for l in xrange(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def accuracy(self, data, convert=False):
        if convert:
            results = [(np.argmax(self.feedforward(x)), np.argmax(y))
                       for (x, y) in data]
        else:
            results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in data]
        return sum(int(x == y) for (x, y) in results)

    def total_cost(self, data, lmbda, convert=False):
        cost = 0.0
        for x, y in data:
            a = self.feedforward(x)
            if convert: y = vectorized_result(y)
            cost += self.cost.fn(a, y)/len(data)
        cost += 0.5*(lmbda/len(data))*sum(
            np.linalg.norm(w)**2 for w in self.weights)
        return cost

    def save(self, filename):
        data = {"sizes": self.sizes,
                "weights": [w.tolist() for w in self.weights],
                "biases": [b.tolist() for b in self.biases],
                "cost": str(self.cost.__name__)}
        f = open(filename, "w")
        json.dump(data, f)
        f.close()

def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e

def sigmoid(z):
    return 1.0/(1.0+np.exp(-z))

def sigmoid_prime(z):
    return sigmoid(z)*(1-sigmoid(z))

def optimize_strategy(**kwargs):

    strategy = kwargs['strategy']
    data = kwargs['data']
    grid_args = []

    if strategy.__name__ == GoldenDeathCross.__name__:
        shorts = kwargs['short']
        longs = kwargs['long']
        for short in shorts:
            for long in longs:
                grid_args.append({'context' : None, 'short' : short ,  'long' : long})
    elif strategy.__name__ == MACDCross.__name__:
        shorts = kwargs['short']
        longs = kwargs['long']
        signals = kwargs['signal']
        for short in shorts:
            for long in longs:
                for signal in signals:
                    grid_args.append({'context' : None, 'short' : short ,  'long' : long, 'signal' : signal})
    elif strategy.__name__ == SVMClassifier.__name__:
        training_data = kwargs['training_data']
        windows = kwargs['window']
        targets = kwargs['target']
        for window in windows:
            for target in targets:
                grid_args.append({'context' : None, 'training_data' : training_data, 'window' : window, 'target' : target})
    elif strategy.__name__ == KNNClassifier.__name__:
        training_data = kwargs['training_data']
        windows = kwargs['window']
        targets = kwargs['target']
        for window in windows:
            for target in targets:
                grid_args.append({'context' : None, 'training_data' : training_data, 'window' : window, 'target' : target})
    elif strategy.__name__ == NNClassifier.__name__:
        training_data = kwargs['training_data']
        windows = kwargs['window']
        targets = kwargs['target']
        for window in windows:
            for target in targets:
                grid_args.append({'context' : None, 'training_data' : training_data, 'window' : window, 'target' : target})

    optimal_return = -np.Inf
    optimal_args = None

    for args in grid_args:
        s = strategy(**args)
        is_buying_state = False
        buying_price = 0.
        total_buying_price = 0.
        total_selling_price = 0.
        for symbol in data:
            prices = data[symbol]
            for k in range(len(prices)):
                if not is_buying_state and s.is_enter(prices[:k]):
                    is_buying_state = True
                    buying_price = prices['close'][k]
                if is_buying_state and s.is_exit(prices[:k]):
                    is_buying_state = False
                    total_buying_price += buying_price
                    total_selling_price += prices['close'][k]

        profit_rate = (total_selling_price/total_buying_price - 1)
        if profit_rate > optimal_return:
            optimal_return = profit_rate
            optimal_args = args

    return optimal_return,optimal_args