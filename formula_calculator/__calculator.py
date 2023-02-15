import re
from collections.abc import Iterable
from formula_calculator import __operators
from .__operators import *


def calculator(channel, **formulas):
    '''
    ###公式计算器###
    该函数实现了在channel外的一层装饰器，除了可以迭代获取channel返回的数据外，同时实现formulas中定义的公式计算，并将计算结果update到channel的返回结果中

    :param channel: 可迭代对象，迭代返回item数据，item数据格式dict、Series均可
    :param formulas: 公式集，传入后可对每一个公式进行流式数据的计算。公式的输入应为key-value形式,其中key为计算结果的名称，value为公式内容，且均为字符串，如factor1='max(rolling(high,20))'，或{'factor1':'max(rolling(high,20))'}
    :return: Iterable，每次返回的内容包含channel每次迭代返回的item和公式计算结果，其中item[key]为公式计算结果。

    :example

    #定义迭代对象channel
    import redis
    def channel(ip,port,db,channel_name):
        rc = redis.StrictRedis(host=ip, port=port, db=db)
        ps = rc.pubsub()
        ps.subscribe(channel_name)
        for item in ps.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                yield data
    #定义公式集
    formulas = {'formula1' : "max(rolling(close,10))-shift(close,10-argmax(rolling(close,10)))",
                'formula2' : "sum(abs(rolling(delta(close,1),20)))/abs(sum(rolling(delta(close,1),20)))-trace(close,20)",
                'formula3' : "mean(sign(rolling(if(max(rolling(close,30))>=min(rolling(close,30)),1,-1),30)))"}
    #执行公式计算器的装饰运行
    for i in calculator(channel("127.0.0.1",6379,0,"whatever_name"),**formulas):
        print(i)

    '''
    buffer_max_size = 1
    if not isinstance(channel,Iterable):
        raise AssertionError("channel参数应为可迭代对象")
    if not isinstance(formulas,dict):
        raise AssertionError("公式的输入应为key-value形式,其中key为计算结果的名称，value为公式内容，且均为字符串，如factor1='max(rolling(high,20))'，或{'factor1':'max(rolling(high,20))'}")
    param_list = []
    formula_list = []
    for key,value in formulas.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise AssertionError("公式名和公式应为字符串形式")
        param_list.append(key)
        formula_list.append(value)
        buffer_max_size = max([int(x[1:]) for x in re.findall(r",[0-9.]+", value)] + [buffer_max_size, ])
    formula_code = ", ".join(formula_list)
    formula_code = formula_code.replace("if(", "ifelse(")
    variable_list = re.findall(r"[a-zA-Z]+", formula_code)
    value_list = []
    for key in set(variable_list):
        if key not in dir(__operators):
            value_list.append(key)
        elif isinstance(getattr(__operators, key), BufferOpt.__class__):
            for i in range(variable_list.count(key)):
                new_name = key+'{0}('.format(i)
                formula_code = formula_code.replace(key + '(', new_name, 1)
                exec("{0}={1}(buffer_max_size)".format(new_name[:-1],key))

    exec_code = ""
    for name in param_list:
        exec_code = exec_code + "item['" + name + "'],"
    exec_code = exec_code[:-1] + " = " + formula_code
    for item in channel:
        for value in value_list:
            exec("{0}=float({1})".format(value,item[value]))
        exec(exec_code)
        yield item
