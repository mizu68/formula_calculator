# 针对流式数据的公式计算器
- 该工具主要针对流式数据在获取过程中实时执行公式计算的功能；
- 核心方法为formula_calculator.calculator；
- calculator需要传入channel和公式集合，channel可以是包装好的redis函数调用以及其它任何形式的可迭代对象；
- 示例代码：

```python
import redis
from formula_calculator import calculator

#可迭代的数据流channel（redis样例）
def channel(ip,port,db,channel_name):
    rc = redis.StrictRedis(host=ip, port=port, db=db)
    ps = rc.pubsub()
    ps.subscribe(channel_name)
    for item in ps.listen():
        if item['type'] == 'message':
            data = eval(item['data'])
            yield data
#公式集样例
formulas = {'formula1' : "max(rolling(close,10))-shift(close,10-argmax(rolling(close,10)))",
            'formula2' : "sum(abs(rolling(delta(close,1),20)))/abs(sum(rolling(delta(close,1),20)))-trace(close,20)",
            'formula3' : "mean(sign(rolling(if(max(rolling(close,30))>=min(rolling(close,30)),1,-1),30)))"}
#调用演示
for i in calculator(channel("127.0.0.1",6379,0,"whatever_name"),**formulas):
    print(i)
#其它调用方式
for i in calculator(channel("127.0.0.1",6379,0,"whatever_name"),factor1="sum(abs(rolling(delta(close,1),20)))/abs(sum(rolling(delta(close,1),20)))-trace(close,20)"):
    print(i)
```
