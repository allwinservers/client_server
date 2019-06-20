import hashlib
import json
import requests
import time
from requests import request
from libs.utils.log import logger

def send_request(url, headers={}, method='get', params=None, data=None):
    try:
        result = request(method, url, headers=headers, params=params, json=data, verify=False)
        status_code = result.status_code
        result = result.json()
        if result.get('rescode') == '10000':
            return True, result.get('data')
        return "1", result.get('msg')
    except Exception as ex:
        return "2", '{0}'.format(ex)

class FmlCallbackClass(object):

    def __init__(self,mobile=None,password=None,time_wait=3,callback=None):

        """
        付临门聚合码支付获取交易数据
        :param mobile: 登录账号
        :param password: 密码
        :param time_wait: 监控等待秒数
        :param callback: 回调函数处理
        """

        self.mobile=mobile
        self.password = hashlib.md5((password + 'superpw1234_!QAZ').encode('utf-8')).hexdigest()

        self.login_url = 'https://smzf.yjpal.com/payQRCode/loginCheck.htm'
        self.tranlist_url = 'https://smzf.yjpal.com/payQRCode/newQrcodeTransjnlsList.htm'

        self.time_wait=time_wait
        self.callback=callback

        self.token = None
        self.tranlist_obj = None

    def _login(self):
        try:
            response = requests.post(url=self.login_url, data={
                "mobileNo" : self.mobile,
                "password" : self.password
            })
            response = json.loads(response.content.decode('utf-8'))

            self.token = response['token']

            return response['code']
        except Exception :
            return None

    def _tranlist(self):

        try:
            headers = {
                "AccessToken" : self.token
            }
            response = requests.post(url=self.tranlist_url, headers=headers , data={
                "mobileNo" : self.mobile,
                "pageNo" : 20,
                "time" : 201905
            })
            self.tranlist_obj = json.loads(response.content.decode('utf-8'))

            return self.tranlist_obj['code']
        except Exception :
            return None

    def login(self):
        while self._login() != '0000':
            pass

    def tranlist(self):

        while True:
            res =  self._tranlist()
            if res:
                return res

    def run(self):
        if not self.mobile or not self.password or not self.callback:
            return None

        while True:
            if self.tranlist() != '0000':
                self.login()
            self.callback(tranlist_obj = self.tranlist_obj)
            time.sleep(self.time_wait)

class WechatCallbackClass(object):

    def __init__(self, mobile=None, password=None, time_wait=3, callback=None):
        pass

def flmQuery():

    data= {
        "page" : 1,
        "page_size" : 99999999
    }

    res = send_request(
        url='allwin6666.com/api/paycall/flm_tranlist_get',
        method='GET',
        params={"data":data})
    return res[1]

def flmInsert(tranlist):

    data= {
        "tranlist" : tranlist
    }
    res = send_request(
        url='allwin6666.com/api/paycall/flm_callback',
        method='POST',
        data={"data" : data})
    return None

def callback(tranlist_obj):

    res = flmQuery()

    ordercodes = [ res['ordercode'] for item in res ]

    tranlist = [ item for item in tranlist_obj['transList'] if item['status']=='交易成功' and item['orderNo'] not in ordercodes ]

    if len(tranlist):
        flmInsert(tranlist)

if __name__ == '__main__':
    FlmClass = FmlCallbackClass(mobile=15060073200,password='a123456',callback=callback)
    FlmClass.run()
