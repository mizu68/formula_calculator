import re
import pandas as pd
from utils import RingBuffer,StockChannel
import operators
from operators import *

def calculator(formula,stoch_code,cycle):
    formula = formula.replace("if(", "ifelse(")
    nums = re.findall(r"\d+",formula)
    nums = [int(x) for x in nums]
    buffer_max_size = max(nums)
    names = re.findall(r"[a-zA-Z]+",formula)

    value_list = []
    for key in set(names):
        if key not in dir(operators):
            value_list.append(key)
        elif isinstance(getattr(operators,key),BufferOpt.__class__):
            for i in range(names.count(key)):
                new_name = key+'{0}('.format(i)
                formula = formula.replace(key+'(',new_name,1)
                exec("{0}={1}(buffer_max_size)".format(new_name[:-1],key))

    channel = StockChannel(stoch_code,cycle)
    for item in channel.run():
        for value in value_list:
            exec("{0}=float({1})".format(value,item[value]))
        result = eval(formula)
        yield item['time'],result

if __name__== "__main__":
    formula = "mean(rolling(close,20))"

    for i in calculator(formula,'000002.SZ','3S'):
        print(i)