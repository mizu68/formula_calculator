import re
import pandas as pd
from utils import RingBuffer,StockChannel
import operators
from operators import *

if __name__== "__main__":
    formula = "mean(sign(rolling(if(max(rolling(close,20))>=min(rolling(close,20)),1,-1),20)))"

    channel = StockChannel('000002.SZ',"3S")

    formula = formula.replace("if(", "ifelse(")
    nums = re.findall(r"\d+",formula)
    nums = [int(x) for x in nums]
    buffer_max_size = max(nums)
    names = re.findall(r"[a-zA-Z]+",formula)

    value_list = []
    for key in set(names):
        if key not in dir():
            value_list.append(key)
        elif isinstance(getattr(operators,key),BufferOpt.__class__):
            for i in range(names.count(key)):
                new_name = key+'{0}('.format(i)
                formula = formula.replace(key+'(',new_name,1)
                exec("{0}={1}(buffer_max_size)".format(new_name[:-1],key))

    for item in channel.run():
        for value in value_list:
            exec("{0}=float({1})".format(value,item[value]))
        result = eval(formula)
        print(item['time'],result)