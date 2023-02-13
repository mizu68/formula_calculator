import redis
from datetime import datetime, timedelta, time
import requests


class StockChannel(object):
    _freq = ['s', 'S', 'm', 'M']
    quot_http = "http://18.210.70.17:16666/manager"

    def __init__(self,stock_code,cycle):
        if len(cycle) >= 2 and cycle[-1] in self._freq:
            self.bar_step = timedelta(minutes=float(cycle[:-1])) if self._freq.index(cycle[-1]) > 1 else timedelta(seconds=int(cycle[:-1]))
        else:
            raise Exception('cycle参数错误')

        self.trade_time=[[time(9, 30, 3), time(11, 30, 0)], [time(13, 0, 0), time(15, 1, 0)]]
        self.next_bar_time = datetime(1970, 1, 1, 9, 30, 0).time()
        self.trade_date = datetime.today().strftime("%Y%m%d")
        self.resp_dict = {}
        self.redis_threading = []

        try:
            amd = requests.post(self.quot_http, json={"op_type": "listen", "type": "market", "sub_type": "l2_orderbook", "param":{"op_type": "start", "cycle": self.bar_step.seconds * 1000, "codes":stock_code}})
            if amd.status_code != 200:
                raise IOError('行情系统请求失败:%s' % amd.reason)
            resp = eval(amd.text)
            if resp['error_code']!='0':
                raise IOError('行情系统请求失败:%s' % resp['error_msg'])
        except Exception as e:
            raise e

        self.ps = self.redis_listen((resp['redis_ip'], resp['redis_port'], resp['redis_db']), resp['channel'][0])


    def run(self):
        for item in self.ps.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                yield data

    def redis_listen(self,redis_config,channel):
        rc = redis.StrictRedis(host=redis_config[0], port=redis_config[1], db=redis_config[2],password="password_123")
        ps = rc.pubsub()
        ps.subscribe(channel)
        return ps

