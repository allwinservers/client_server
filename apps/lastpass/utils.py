from requests import request
import json
from urllib.parse import urlencode
from collections import OrderedDict
import hashlib
from libs.utils.mytime import UtilTime
from utils.exceptions import PubErrorCustom
from apps.order.models import Order
from apps.paycall.utils import PayCallLastPass
from apps.utils import url_join
import time,random
from libs.utils.log import logger
import demjson

import base64
#
# if __name__ == '__main__':
#     data = {
#         "body" : "1",
#         'charset'  : 'utf-8',
#         'isApp' : 'web',
#         'merchantId' : '102000000002524',
#         'notifyUrl' : 'http://allwin6666.com/api/lastpass/lastpass_callback',
#         "returnUrl" : "http://allwin6666.com/api/lastpass/lastpass_callback",
#         "orderNo" : "4",
#         "paymentType" : "1",
#         'paymethod' : 'bankPay',
#         'defaultbank' : 'ALIPAY',
#         'service' : 'online_pay',
#         'title' : '电脑',
#         'totalFee' : 401.00
#     }
#
#     sign(data)
#     data['sign'] = sign(data)
#     data['signType'] = "SHA"
#     print(data)
#
#     url = 'https://ebank.ssfoo.vip/payment/v1/order/{}-{}'.format(data['merchantId'],data['orderNo'])
#
#     result = request(method='POST', url=url, data=data, verify=True)
#     print(result.url)
#
#     print(result)
#
#
# class SignBase(object):
#
#     def __init__(self):
#         pass
#
#     def jm_sign(self,data):
#         new_dict = OrderedDict()
#         new_data = []
#         for item in data:
#             if data[item] and len(data[item]):
#                 new_data[item] = data[item]
#         keys = sorted(new_data)
#         for item in keys:
#             new_dict[item] = data[item]
#
#         for key in data:
#             new_dict[key] = data[key]
#
#         key = '89d50bea1f06406abaf73997a822ecd6'
#
#         j = ""
#         for item in new_dict:
#             j += "{}={}&".format(item, new_dict[item])
#         new_dict = (j[:-1] + key)
#         print(new_dict)
#         new_dict = new_dict.encode("utf-8")
#
#         return hashlib.sha1(new_dict).hexdigest()
#
#     def gaozong_sign(self,data):
#
#         new_dict = OrderedDict()
#         keys = sorted(data)
#         for item in keys:
#             new_dict[item] = data[item]
#
#         for key in data:
#             new_dict[key] = data[key]
#         j = ""
#         for item in new_dict:
#             j += "{}={}&".format(item, new_dict[item])
#         new_dict = j[:-1]
#         new_dict = new_dict.encode("utf-8")
#         print(new_dict)
#
#         return hashlib.md5(new_dict).hexdigest()

class LastPassBase(object):

    def __init__(self,**kwargs):
        self.secret = kwargs.get('secret')
        self.data = kwargs.get('data',{})

    def _sign(self):
        pass

class LastPass_JLF(LastPassBase):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #测试环境
        # self.create_order_url = "http://pre.api.otcbank.net/pay/createPayOrder"
        # self.secret = "89d50bea1f06406abaf73997a822ecd6"
        # self.businessId = "10012"

        #生产环境
        self.create_order_url="http://api.otcbank.net/pay/createPayOrder"
        self.secret = "7f9b8d71340441d89f4ab8523b0f9a79"
        self.businessId = "10015"

        self.response = None

    def _sign(self):

        valid_data={}
        #去掉value为空的值
        for item in self.data:
            if str(self.data[item]) and len(str(self.data[item])):
                valid_data[item] = self.data[item]

        valid_data['secret'] = self.secret

        #排序固定位置
        valid_data_keys=sorted(valid_data)
        valid_orders_data = OrderedDict()
        for key in valid_data_keys:
            valid_orders_data[key] = valid_data[key]

        #将数据变成待加密串
        encrypted=str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        self.data['sign']=hashlib.md5(encrypted).hexdigest()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response =  json.loads(result.content.decode('utf-8'))

    def run(self):
        self.data.setdefault('businessId',int(self.businessId))
        self.data.setdefault('signType','MD5')
        self.data.setdefault('payTitle','商品1')
        self.data.setdefault('random',UtilTime().timestamp)
        self.data.setdefault('payMethod',0)
        self.data.setdefault('dataType',0)
        # self.data.setdefault('returnUrl',url_join("/pay/#/juli"))
        self._sign()
        try:
            self._request()
            return (False, self.response['errorDesc']) if not self.response['successed'] else (True,self.response['returnValue'])
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        self.check_sign()
        if not self.data.get("businessId") or self.data.get("businessId")!= self.businessId:
            raise PubErrorCustom("商户ID不存在!")
        if not self.data.get("amount") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("signType") or self.data.get("signType")!= 'MD5':
            raise PubErrorCustom("签名类型不正确")
        if not self.data.get("outTradeNo"):
            raise PubErrorCustom("商户订单号为空!")
        if not self.data.get("orderState"):
            raise PubErrorCustom("订单状态为空!")

        if self.data.get("orderState") == 'success':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("outTradeNo"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)



class LastPass_TY(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://www.vzzfrb.cn/Pay_Index.html"
        self.secret = "vygqv8iil8h3g1e2xc50j1xddy2g525p"
        self.businessId = "190623841"

        self.response = None

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

        valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        self.data['pay_md5sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['pay_md5sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def Md5str(src):
        m = hashlib.md5(src.encode("utf8"))
        return m.hexdigest().upper()

    def obtaindate(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def _request(self):
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)

        self.response = result.text
        logger.info(self.response)

    def run(self):
        self.data.setdefault('pay_memberid',self.businessId)
        self.data.setdefault('pay_applydate',self.obtaindate())
        # self.data.setdefault('pay_bankcode',"904")
        self.data.setdefault('pay_callbackurl',url_join("/pay/#/juli"))
        self._sign()

        self.data.setdefault('pay_productname',"商品")
        self.data.setdefault('create_order_url',self.create_order_url)

        return self.data

    def call_run(self):
        self.check_sign()
        if not self.data.get("memberid") or self.data.get("memberid")!= self.businessId:
            raise PubErrorCustom("商户ID不存在!")
        if not self.data.get("amount") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("orderid"):
            raise PubErrorCustom("商户订单号为空!")

        if self.data.get("returncode") == '00':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("orderid"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

class LastPass_YZL(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://39.109.0.189/PayOrder/payorder"
        self.secret = "nMuNRjQd8hEFFX4u8JNCBNM6pEn35PdW"
        self.businessId = "658431973136167"
        self.businessNo = "048628"

        self.response = None

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

        # valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = (encrypted[:-1]+self.secret).encode("utf-8")
        self.data['sign'] = hashlib.md5(encrypted).hexdigest()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        encrypted = (str(self.data['out_order_no'])+str(self.data['total_fee'])+str(self.data['trade_status'])+str(self.businessId)+str(self.secret)).encode("utf-8")
        print(encrypted)
        self.data['sign'] = hashlib.md5(encrypted).hexdigest()

        print(self.data['sign'])
        print(sign)
        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response = result.text

    def run(self):

        self.data.setdefault('subject',"商品M")
        self.data.setdefault('body','商品MM')
        self.data.setdefault('return_url', url_join("/pay/#/juli"))
        self.data.setdefault('partner', self.businessId)
        self.data.setdefault('user_seller', self.businessNo)
        self._sign()

        self.data.setdefault('pay_type',"zfbh5")
        self.data.setdefault('http_referer', "allwin6666.com")

        try:
            self._request()
            return (True,self.response)
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        if not self.data.get("total_fee") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("out_order_no"):
            raise PubErrorCustom("商户订单号为空!")
        self.check_sign()

        if self.data.get("trade_status") == 'TRADE_SUCCESS':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("out_order_no"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)


class LastPass_DD(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://zf.da12.cc/Pay_Index.html"
        self.secret = "785g5ykawr9jkzgw9qpkh562w5dhvsfp"
        self.businessId = "190649615"

        self.response = None

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

        valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        self.data['pay_md5sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['pay_md5sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def Md5str(src):
        m = hashlib.md5(src.encode("utf8"))
        return m.hexdigest().upper()

    def obtaindate(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def _request(self):
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response = result.text

    def run(self):
        self.data.setdefault('pay_memberid',self.businessId)
        self.data.setdefault('pay_applydate',self.obtaindate())
        self.data.setdefault('pay_callbackurl',url_join("/pay/#/juli"))
        self._sign()

        self.data.setdefault('pay_productname',"商品")

        try:
            self._request()
            return (True,self.response)
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        self.check_sign()
        if not self.data.get("memberid") or self.data.get("memberid")!= self.businessId:
            raise PubErrorCustom("商户ID不存在!")
        if not self.data.get("amount") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("orderid"):
            raise PubErrorCustom("商户订单号为空!")

        if self.data.get("returncode") == '00':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("orderid"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

class LastPass_OSB(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://www.yitengkeji.top/index/api/order"
        self.secret = "5ab569e8ed79c369e76fb1e4b02f7b8131fa4ce96ba0a37b4fb21022a493b1c6"
        self.businessId = "69659de1f6b175d0663ec453f648677f"

        self.response = None

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

        # valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}{}".format(item, valid_orders_data[item])
        encrypted = (self.secret+encrypted+self.secret).encode("utf-8")
        print(encrypted)
        self.data['sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        print(self.data)
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response=json.loads(result.content.decode('utf-8'))
        print(self.response)

    def run(self):

        self.data.setdefault('client_id',self.businessId)
        self.data.setdefault('timestamp',UtilTime().timestamp*1000)
        self._sign()

        try:
            self._request()
            return (False, self.response['msg']) if self.response['code'] != 200 else (True,self.response['data'])
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        self.check_sign()
        if not self.data.get("total") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("api_order_sn"):
            raise PubErrorCustom("商户订单号为空!")

        if self.data.get("callbacks") == 'CODE_SUCCESS':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("api_order_sn"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

class LastPass_BAOZHUANKA(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://www.gudad.cn/pay/acp"
        self.secret = "67eh6aatf8megjz4pkoob4d7cohxzew8"
        self.businessId = "23"

        self.response = None

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

        valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        self.data['sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        print(self.data)
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response = result.text
        print(self.response)
    def run(self):
        self.data.setdefault('u',self.businessId)

        # self.data.setdefault('pay_bankcode',"904")
        self._sign()

        try:
            self._request()
            return (True,self.response)
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        self.check_sign()

        if not self.data.get("amount") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("orderid"):
            raise PubErrorCustom("商户订单号为空!")

        if self.data.get("returncode") == '00':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("orderid"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

class LastPass_LIMAFU(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://api.ponypay1.com/"
        self.secret = "1359859484107426286869760710762572181072460749407628796928543285"
        self.businessId = "95560"

        self.response = None

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

        valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        print(encrypted)
        self.data['sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):

        parastring=(self.data['merchant_id'] + self.data['orderid']+self.data['money']+self.secret).encode("gb2312")

        sign = hashlib.md5(parastring).hexdigest()

        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        print(self.data)
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response = json.loads(result.content.decode('utf-8'))
    def run(self):

        self.data.setdefault('merchant_id',self.businessId)
        self.data.setdefault('paytype','YSF')
        self.data.setdefault('callbackurl','http://www.baidu.com')

        parastring = (self.data['merchant_id']+self.data['orderid']+self.data['paytype']+self.data['notifyurl']+self.data['callbackurl']+self.data['money']+self.secret).encode("gb2312")
        self.data['sign'] = hashlib.md5(parastring).hexdigest()


        try:
            self._request()
            print(self.response)
            return (False, self.response['message']) if self.response['status']!='1' else (True,self.response['data'])
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        self.check_sign()
        if not self.data.get("money") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("orderid"):
            raise PubErrorCustom("商户订单号为空!")

        if self.data.get("status") == '1':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("orderid"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

class LastPass_JUXING(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://118.31.8.186:3020/api/pay/create_order"
        self.secret = "QRG0S1WNGWNPIGCU6UEFBTHXAIR7YL4VTEIWRIBZKZPFD9FLTGE84CFLJWFYYVEPJRMRJJIGE4NPM6YIVZETDFAUCBEPTS7NRFPMUMOJRWTSICWZK5SOP8CUDBSQJC51"
        self.businessId = 20000041
        self.appId='1a3e473671434f06a06a31ab1f6dad13'
        self.productId=8023

        self.response = None

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

        valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        print(encrypted)
        self.data['sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self):
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)
        self.response = json.loads(result.content.decode('utf-8'))

    def run(self):
        self.data.setdefault('mchId',self.businessId)
        self.data.setdefault('appId',self.appId)


        self.data.setdefault('currency','cny')

        self.data.setdefault('productId', self.productId)
        self.data.setdefault('subject','商品P')
        self.data.setdefault('body', '商品P6666')

        # self.data.setdefault('pay_bankcode',"904")
        self._sign()


        try:
            self._request()
            print(self.response)
            return (False, self.response['retMsg']) if self.response['retCode']!='SUCCESS' else (True,self.response['payParams']['payUrl'])
        except Exception as e:
            return (False,str(e))

    def call_run(self):
        self.check_sign()
        if not self.data.get("amount") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("mchOrderNo"):
            raise PubErrorCustom("商户订单号为空!")

        self.data["amount"] = float(self.data.get("amount")) / 100.0

        if str(self.data.get("status")) == '2':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("mchOrderNo"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

class LastPass_MK(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


        #生产环境
        self.create_order_url="http://www.lianermei.cn/Pay_Index.html"
        self.secret = "2pztqmsktehj76exsw1c9sjjtd4lfqmi"
        self.businessId = "10213"

        self.response = None

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

        valid_orders_data['key']=self.secret

        # 将数据变成待加密串
        encrypted = str()
        for item in valid_orders_data:
            encrypted += "{}={}&".format(item, valid_orders_data[item])
        encrypted = encrypted[:-1].encode("utf-8")
        self.data['pay_md5sign'] = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self):
        sign = self.data.pop('sign',False)
        self._sign()
        if self.data['pay_md5sign'] != sign:
            raise PubErrorCustom("签名不正确")

    def Md5str(src):
        m = hashlib.md5(src.encode("utf8"))
        return m.hexdigest().upper()

    def obtaindate(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def _request(self):
        result = request(method='POST', url=self.create_order_url, data=self.data, verify=True)

        self.response = result.text
        logger.info(self.response)

    def run(self):
        self.data.setdefault('pay_memberid',self.businessId)
        self.data.setdefault('pay_applydate',self.obtaindate())
        # self.data.setdefault('pay_bankcode',"904")
        self.data.setdefault('pay_callbackurl',url_join("/pay/#/juli"))
        self._sign()

        self.data.setdefault('pay_productname',"商品")

        self.data.setdefault('create_order_url',self.create_order_url)

        return self.data

    def call_run(self):
        self.check_sign()
        if not self.data.get("memberid") or self.data.get("memberid")!= self.businessId:
            raise PubErrorCustom("商户ID不存在!")
        if not self.data.get("amount") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("orderid"):
            raise PubErrorCustom("商户订单号为空!")

        if self.data.get("returncode") == '00':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("orderid"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)


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
            valid_data[item] = self.data[item]

        # 排序固定位置
        valid_data_keys = sorted(valid_data)
        valid_orders_data = OrderedDict()
        for key in valid_data_keys:
            valid_orders_data[key] = valid_data[key]

        # 将数据变成待加密串
        encrypted = ("biz_content={}&key={}".format(demjson.encode(valid_orders_data), self.secret)).encode("utf-8")
        self.signature = hashlib.md5(encrypted).hexdigest().upper()

    def check_sign(self,sign):
        self._sign()
        if self.signature != sign:
            raise PubErrorCustom("签名不正确")

    def _request(self,data):
        result = request(method='POST', url=self.create_order_url, params=data, verify=True)
        self.response =  json.loads(result.content.decode('utf-8'))

    def run(self):
        self.data.setdefault('mch_id',self.businessId)
        self.data.setdefault('pay_platform','WXPAY')
        self.data.setdefault('pay_type','MWEB')
        self.data.setdefault('cur_type','CNY')
        self.data.setdefault('body','夏季服装')


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


    def call_run(self):

        status =str(self.data.get("ret_code"))
        signature = self.data.pop('signature',False)

        self.data = self.data.get("biz_content")

        print(self.data)
        print(type(self.data))

        self.check_sign(signature)

        # self.data["payment_fee"] = float(self.data.get("payment_fee")) / 100.0

        if not self.data.get("mch_id") or self.data.get("mch_id")!= self.businessId:
            raise PubErrorCustom("商户ID不存在!")
        if not self.data.get("payment_fee") :
            raise PubErrorCustom("金额不能为空!")
        if not self.data.get("out_order_no"):
            raise PubErrorCustom("商户订单号为空!")

        if status == '0':
            try:
                order = Order.objects.select_for_update().get(ordercode=self.data.get("out_order_no"))
            except Order.DoesNotExist:
                raise PubErrorCustom("订单号不正确!")

            if order.status == '0':
                raise PubErrorCustom("订单已处理!")

            PayCallLastPass().run(order=order)

if __name__=="__main__":

    request_data = {
        "uid": "1",
        "amount": 1000.0,
        "outTradeNo": "5",
        "ip": "192.168.0.1",
        "notifyUrl": "http://allwin6666.com/api/pay_call/wechat_test"
    }
    res = LastPass_JLF(data=request_data).run()














