

import time,random
from requests import request
from collections import OrderedDict
import hashlib
import json
import demjson
from libs.utils.mytime import UtilTime

class LastPassBase(object):

    def __init__(self,**kwargs):
        self.secret = kwargs.get('secret')
        self.data = kwargs.get('data',{})

    def _sign(self):
        pass

class LastPass_TONGYU(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="https://8oep1k.apolo-pay.com/unifiedorder"
        self.secret = "ed0556b7d7414ab3bef6dac7ac69b47a"
        self.businessId = "10000044"

        self.response = None

        self.signature =None

    def _sign(self):

        valid_data = {}
        # 去掉value为空的值
        for item in self.data:
            if str(self.data[item]) and len(str(self.data[item])):
                valid_data[item] = self.data[item]

        # 排序固定位置
        valid_data_keys = sorted(valid_data)
        valid_orders_data = OrderedDict()
        for key in valid_data_keys:
            valid_orders_data[key] = valid_data[key]

        # 将数据变成待加密串
        encrypted = ("biz_content={}&key={}".format(demjson.encode(valid_orders_data), self.secret)).encode("utf-8")
        print(encrypted)
        self.signature = hashlib.md5(encrypted).hexdigest().upper()

    # def check_sign(self):
    #     sign = self.data.pop('sign',False)
    #     self._sign()
    #     if self.data['pay_md5sign'] != sign:
    #         raise PubErrorCustom("签名不正确")

    def _request(self,data):
        print(data)
        result = request(method='POST', url=self.create_order_url, params=data, verify=True)
        print(result.url)
        self.response =  json.loads(result.content.decode('utf-8'))

    def run(self):
        self.data.setdefault('mch_id',self.businessId)
        self.data.setdefault('pay_platform','WXPAY')
        self.data.setdefault('pay_type','MWEB')
        self.data.setdefault('cur_type','CNY')
        self.data.setdefault('body','夏季服装')
        self.data.setdefault('bill_create_ip','123.12.12.123')

        self.data.setdefault('notify_url',"http://www.baidu.com")

        self._sign()

        data={
            "sign_type":"MD5",
            "signature" : self.signature,
            "biz_content" : demjson.encode(self.data)
        }

        try:
            self._request(data)
            return (False, self.response['ret_msg']) if str(self.response['ret_code'])!='0' else (True,self.response['biz_content']['mweb_url'])
        except Exception as e:
            return (False,str(e))


    # def call_run(self):
    #     self.check_sign()
    #     if not self.data.get("memberid") or self.data.get("memberid")!= self.businessId:
    #         raise PubErrorCustom("商户ID不存在!")
    #     if not self.data.get("amount") :
    #         raise PubErrorCustom("金额不能为空!")
    #     if not self.data.get("orderid"):
    #         raise PubErrorCustom("商户订单号为空!")
    #
    #     if self.data.get("returncode") == '00':
    #         try:
    #             order = Order.objects.select_for_update().get(ordercode=self.data.get("orderid"))
    #         except Order.DoesNotExist:
    #             raise PubErrorCustom("订单号不正确!")
    #
    #         if order.status == '0':
    #             raise PubErrorCustom("订单已处理!")
    #
    #         PayCallLastPass().run(order=order)



if __name__=='__main__':

    request_data={
        "out_order_no":"fasdfs1",
        "payment_fee":100 * 100
    }

    res = LastPass_TONGYU(data=request_data).run()


    print(res)
