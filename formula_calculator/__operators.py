import numpy as np
from .__ring_buffer import RingBuffer

def sign(*args):
    return np.sign(*args)

def abs(*args):
    return np.abs(*args)

def max(*args):
    return np.max(*args)

def min(*args):
    return np.min(*args)

def argmax(*args):
    return np.argmax(*args)

def argsmin(*args):
    return np.argmin(*args)

def sum(*args):
    return np.sum(*args)

def mean(*args):
    return np.mean(*args)

def std(*args):
    return np.std(*args)

def var(*args):
    return np.var(*args)

def ln(*args):
    return np.log(*args)

def log(arr,logarithm):
    return np.log(arr)/np.log(logarithm)

def exp(*args):
    return np.exp(*args)

def power(arr,xp):
    return np.power(arr,xp)

def tanh(*args):
    return np.tanh(*args)

def sigmoid(df):
    return 1 / (1 + exp(-df))

def corr(df1,df2):
    return np.corrcoef(df1,df2)

def rank(df):
    return np.sort(df)

def cov(df1,df2):
    return np.cov(df1,df2)

def ifelse(judge,tr,fl):
    return tr if judge else fl


class BufferOpt(object):
    buffer = None

    def __init__(self,size):
        self.buffer = RingBuffer(size)


class delta(BufferOpt):

    def __init__(self,size):
        self.buffer = RingBuffer(size+1)

    def __call__(self, value,size):
        self.buffer.append(value)
        return self.buffer.data[-1] - self.buffer.data[-1-size]


class div(BufferOpt):

    def __init__(self, size):
        self.buffer = RingBuffer(size + 1)

    def __call__(self, value, size):
        self.buffer.append(value)
        return self.buffer.data[-1] / self.buffer.data[-1 - size]


class shift(BufferOpt):

    def __init__(self,size):
        self.buffer = RingBuffer(size+1)

    def __call__(self, value,size):
        self.buffer.append(value)
        return self.buffer.data[-size]


class rolling(BufferOpt):

    def __call__(self, value,size):
        self.buffer.append(value)
        return self.buffer.data[-size:]


class trace(BufferOpt):

    def __init__(self,size):
        BufferOpt.__init__(self,size)
        self.rolling0 = rolling(size)
        self.rolling1 = rolling(size)
        self.delta0 = delta(1)
        self.delta1 = delta(1)

    def __call__(self, value,size):
        self.buffer.append(value)
        return sum(abs(self.rolling0(self.delta0(value, 1), size))) / abs(sum(self.rolling1(self.delta1(value, 1), size)))