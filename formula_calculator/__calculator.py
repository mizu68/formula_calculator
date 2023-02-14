import re
from collections.abc import Iterable
from formula_calculator import __operators
from .__operators import *


def calculator(channel,formula,name=None):

    if not isinstance(channel,Iterable):
        raise AssertionError("channel参数应为可迭代对象")
    if not isinstance(formula,str):
        raise AssertionError("formula参数应为字符串")
    if name is not None and not isinstance(name,str):
        raise AssertionError("指定的name参数应为字符串")

    formula = formula.replace("if(", "ifelse(")
    nums = re.findall(r"\d+",formula)
    nums = [int(x) for x in nums]
    buffer_max_size = max(nums)
    names = re.findall(r"[a-zA-Z]+",formula)

    value_list = []
    for key in set(names):
        if key not in dir(__operators):
            value_list.append(key)
        elif isinstance(getattr(__operators, key), BufferOpt.__class__):
            for i in range(names.count(key)):
                new_name = key+'{0}('.format(i)
                formula = formula.replace(key+'(',new_name,1)
                exec("{0}={1}(buffer_max_size)".format(new_name[:-1],key))

    for item in channel:
        for value in value_list:
            exec("{0}=float({1})".format(value,item[value]))
        result = eval(formula)
        if name is None:
            yield item,result
        else:
            item[name] = result
            yield item
