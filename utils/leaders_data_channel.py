import numpy as np
import pandas as pd
import redis
import time as os_time
from datetime import datetime, timedelta, time
from utils.data_channel import DataChannel
import threading
import requests


class LeadersDataChannel(DataChannel):
    _freq = ['s', 'S', 'm', 'M']

    def __init__(self,index_code,args_data,cycle):
        if len(cycle) >= 2 and cycle[-1] in self._freq:
            self.bar_step = timedelta(minutes=float(cycle[:-1])) if self._freq.index(cycle[-1]) > 1 else timedelta(seconds=int(cycle[:-1]))
        else:
            raise Exception('cycle参数错误')
        self.trade_time=[[time(9, 30, 3), time(11, 30, 0)], [time(13, 0, 0), time(15, 1, 0)]]
        self.next_bar_time = datetime(1970, 1, 1, 9, 30, 0).time()

        index_data = args_data.loc[index_code,:]
        leaders_data = args_data.drop(index_code)
        self.index_pre_price = index_data['pre_close']
        self.leaders_pre_close = np.dot(leaders_data['weight'],leaders_data['pre_close'])
        self.index_code = index_code
        leaders_data['weight'] = np.round(leaders_data['weight']/self.leaders_pre_close,6)
        self.params = dict()
        for key, value in zip(leaders_data.index, leaders_data.to_dict(orient='records')):
            self.params[key] = value
        self.trade_date = datetime.today().strftime("%Y%m%d")
        self.resp_dict = {}
        self.redis_threading = []
        self.alias = self.index_code+".leaders_index_flow"
        self.price = np.zeros((2,4),dtype=np.float)
        self.buy1 = np.nan
        self.sale1 = np.nan
        self.sale1_volume = np.nan
        self.buy1_volume = np.nan
        self.cash_flow = 0

        try:
            amd = requests.post(self.quot_http, json={"op_type": "listen", "type": "utils", "sub_type": "weighted", "param":{"op_type": "start", "alias": self.alias, "cycle": 1000, "codes":self.params}})
            if amd.status_code != 200:
                raise IOError('行情系统请求失败:%s' % amd.reason)
            resp = eval(amd.text)
            if resp['error_code']!='0':
                raise IOError('行情系统请求失败:%s' % resp['error_msg'])
        except Exception as e:
            raise e
        redis_args = (resp['redis_ip'], resp['redis_port'], resp['redis_db'])
        self.ps = self.redis_listen(redis_args,resp['channel'][0])

        try:
            amd = requests.post(self.quot_http, json={"op_type": "listen", "type": "market", "sub_type": "l2_orderbook", "param":{"op_type": "start", "cycle": 100, "codes":[self.index_code,]}})
            if amd.status_code != 200:
                raise IOError('行情系统请求失败:%s' % amd.reason)
            resp = eval(amd.text)
            if resp['error_code']!='0':
                raise IOError('行情系统请求失败:%s' % resp['error_msg'])
        except Exception as e:
            raise e
        redis_args = (resp['redis_ip'], resp['redis_port'], resp['redis_db'])
        self.threading_etf = threading.Thread(target=self.etf_redis_listen, args=(redis_args, resp['channel'][0]))
        self.threading_etf.start()

    def run(self):
        for item in self.ps.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                print(data)
                if 'alias' in data.keys():
                    self.price[1, :] = [data['nav'], data['amount'], float(data['in_cash_flow']),float(data['out_cash_flow'])]
                    exchange_time = datetime.now().time()
                    print(exchange_time,data)
                    if not self.threading_etf.is_alive():
                        raise RuntimeError('行情监控线程异常退出')
                    if exchange_time >= self.next_bar_time:
                        result = self._pop_price(exchange_time)
                    else:
                        result = self._get_price(exchange_time)
                    if result is not None and result.isna().sum() == 0:
                        yield exchange_time, result

    def redis_listen(self,redis_config,channel):
        rc = redis.StrictRedis(host=redis_config[0], port=redis_config[1], db=redis_config[2],password="password_123")
        ps = rc.pubsub()
        ps.subscribe(channel)
        return ps

    def etf_redis_listen(self,redis_config,channel):
        ps = self.redis_listen(redis_config,channel)
        for item in ps.listen():
            if item['type'] == 'message':
                data = eval(item['data'])
                if 'stock_code' in data.keys() and data['stock_code'] == self.index_code:
                    self.price[0, :] = [data['close'], data['amount'], float(data['in_cash_flow']) + float(data['out_cash_flow']),np.nan]
                    if 'sale_price' in data.keys() and len(data['sale_price']) > 0:
                        self.buy1 = float(data['buy_price'][0])
                        self.sale1 = float(data['sale_price'][0])
                        self.sale1_volume = int(float(data['sale_volume'][0]))
                        self.buy1_volume = int(float(data['buy_volume'][0]))

    def _is_trade_period(self, curr_time):
        for trade_period in self.trade_time:
            if trade_period[0] <= curr_time <= trade_period[1]:
                return True
        return False

    def _pop_price(self, curr_time):
        bar_time = str(self.next_bar_time)
        self.next_bar_time = list(filter(lambda x:x>curr_time,[(datetime(1970, 1, 1, curr_time.hour, curr_time.minute, 0) + x * self.bar_step).time() for x in range(int(timedelta(minutes=1)/self.bar_step)+2)]))[0]
        if self.trade_time[0][1] < self.next_bar_time and self.next_bar_time < self.trade_time[1][0]:
            self.next_bar_time = datetime(1970, 1, 1, 13, 0, 0).time()
        if self.next_bar_time > self.trade_time[1][1]:
            self.next_bar_time = datetime(1970, 1, 1, 9, 30, 0).time()
        if self._is_trade_period(curr_time):
            result = pd.Series()
            result['time'] = str(self.next_bar_time)
            result['leaders'], result['amount'], result['leaders_in_cash_flow'],result['leaders_out_cash_flow'] = self.price[1,:]
            result[self.index_code],result['etf_amount'],result['etf_cash_flow'] = self.price[0,:-1]
            result['leaders'] = self.index_pre_price * result['leaders']
            result['buy1'], result['sale1'], result['buy1_volume'], result['sale1_volume'] = self.buy1,self.sale1,self.buy1_volume,self.sale1_volume
            result['gap'] = round(result['sale1'] - result['buy1'],3)
            return result

    def _get_price(self, curr_time):
        if self._is_trade_period(curr_time):
            result = pd.Series()
            result['time'] = str(self.next_bar_time)
            result['leaders'], result['amount'], result['leaders_in_cash_flow'],result['leaders_out_cash_flow'] = self.price[1,:]
            result[self.index_code],result['etf_amount'],result['etf_cash_flow'] = self.price[0,:-1]
            result['leaders'] = self.index_pre_price * result['leaders']
            result['buy1'], result['sale1'], result['buy1_volume'], result['sale1_volume'] = self.buy1,self.sale1,self.buy1_volume,self.sale1_volume
            result['gap'] = round(result['sale1'] - result['buy1'],3)
            return result
