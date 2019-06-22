
import time
import demjson
from django.utils import timezone
import json
import urllib
from apps.public.models import Qrcode

from apps.pay.utils import get_Rate
from apps.order.models import Order

from apps.user.models import UserLink
from include.data.redislockkey import PAY_ADMIN_UPD_BAL
from utils.exceptions import PubErrorCustom,InnerErrorCustom

from apps.user.models import Users
from libs.utils.http_request import send_request

from django.core.serializers.json import DjangoJSONEncoder
from libs.core.decorator.response import encrypt

from apps.paycall.models import PayCallList,FlmTranList
import hashlib
from libs.utils.mytime import UtilTime

from apps.pay.utils import QrCodeWechat,QrCodeFlm
from apps.utils import upd_bal
from apps.pay.models import PayPass
from requests import request

from include.data.choices_list import Choices_to_Dict
from libs.utils.log import logger

class PayCallBase(object) :

    def __init__(self, **kwargs):
        """
        回调类
        :param kwargs:
            name : 名称
            amount : 金额
        self :
            qrcode_obj : 二维码对象
            order_obj : 订单对象
            flag : 处理标志
                True : 成功
                False: 失败
            memo : 处理说明
        """
        self.amount = float(kwargs.get('amount',0.0))
        self.name = kwargs.get('name',None)
        self.type = kwargs.get('type')

        self.qrcode_obj = None
        self.order_obj = None

        self.flag = True
        self.memo = ''
        self.stand_rate = 0.0

        self.qr_class = Choices_to_Dict('qrtype_link_qrClass')[self.type]() if self.type else None
        logger.info("回调开始: 名称{}金额{}类型{}".format(self.name,self.amount,self.type))

    def init_qrcode_obj(self,id=None):
        """
        初始化二维码结构
        :return:
        """
        if id:
            try:
                self.qrcode_obj = Qrcode.objects.select_for_update().get(id=id)
            except Qrcode.DoesNotExist:
                raise PubErrorCustom("无此二维码")
        else:
            self.qrcode_obj = Qrcode.objects.select_for_update().filter(name=self.name,status='0',type=self.type)
            if not self.qrcode_obj.exists():
                logger.error("无对应二维码, name{},type{}".format(self.name,self.type))
                raise PubErrorCustom("无对应二维码")
            self.qrcode_obj = self.qrcode_obj[0]

    def init_order_obj(self,ordercode=None):
        """
        初始化订单结构
        :return:
        """
        if ordercode:
            try:
                self.order_obj = Order.objects.select_for_update().get(ordercode=ordercode)
            except Order.DoesNotExist:
                raise PubErrorCustom("无此订单号")
        else:
            self.order_obj = Order.objects.select_for_update().filter(status=1, qr_id=self.qrcode_obj.id,amount=str(self.amount)).order_by("-createtime")
            if not self.order_obj.exists():
                logger.error("无对应订单, qr_id:{} amount:{}".format(self.qrcode_obj.id,self.amount))
                raise PubErrorCustom("无对应订单")
            self.order_obj = self.order_obj[0]

    def handler_before_check(self):
        """
        业务处理之前校验处理
        :return:
        """
        if not self.qr_class.qrcode_valid(self.order_obj.createtime):
            logger.error("二维码已过期!")
            raise PubErrorCustom("二维码已过期!")

        if float(self.order_obj.amount) - self.amount != 0.0:
            logger.error("金额不符!{},{}".format(float(self.order_obj.amount), self.amount))
            raise PubErrorCustom("金额不符!{},{}".format(float(self.order_obj.amount), self.amount))

    def callback_request_to_server(self):
        """
        进行回调操作
        :return:
        """

        try:
            user = Users.objects.get(userid=self.order_obj.userid)
        except Users.DoesNotExist:
            logger.error("订单用户不存在! 用户:{}".format(self.order_obj.userid))
            raise PubErrorCustom("订单用户不存在!")

        if self.order_obj.lock == '0':

            data_request = {
                "rescode": "10000",
                "msg": "回调成功!",
                "data": {
                    "ordercode": self.order_obj.ordercode,
                    "status": '0',
                    "confirm_amount": float(self.amount),
                    "pay_time": time.mktime(timezone.now().timetuple()),
                    "keep_info": demjson.decode(self.order_obj.keep_info)
                },
                "ordercode":str(self.order_obj.down_ordercode)
            }

            headers={
                "token" : str(self.order_obj.userid),
                "ordercode": str(self.order_obj.down_ordercode)
            }

            #天宝报文不加密
            if user.userid != 4:
                data_request['data'] = encrypt(json.dumps(data_request['data'], cls=DjangoJSONEncoder),
                                               user.google_token).decode('utf-8')

            result = send_request(url=urllib.parse.unquote(self.order_obj.notifyurl), method='POST', data=data_request,headers=headers)
            if not result[0]:
                logger.error("请求对方服务器错误{}".format(str(result)))
                self.order_obj.down_status = '2'
            else:
                self.order_obj.down_status = '0'
        else:

            request_data = {
                "businessid" : str(user.userid),
                "ordercode" : str(self.order_obj.ordercode),
                "down_ordercode" : str(self.order_obj.down_ordercode),
                "amount" : str(self.order_obj.amount),
                "pay_time" : str(UtilTime().timestamp),
                "status" : "00"
            }
            md5params = "{}{}{}{}{}{}{}".format(
                user.google_token,
                request_data['businessid'],
                request_data['ordercode'],
                request_data['down_ordercode'],
                request_data['amount'],
                request_data['pay_time'],
                user.google_token)
            md5params = md5params.encode("utf-8")
            request_data['sign'] = hashlib.md5(md5params).hexdigest()

            logger.info("验签回调参数:{}{}".format(self.order_obj.notifyurl,request_data))
            result = request('POST', url=urllib.parse.unquote(self.order_obj.notifyurl), data=request_data , json=request_data, verify=False)

            logger.info("返回值:{}".format(result.text))
            if result.text != 'SUCCESS':
                logger.error("请求对方服务器错误{}".format(str(result.text)))
                self.order_obj.down_status = '2'
            else:
                self.order_obj.down_status = '0'

    def work_handler_updbal(self,ordercode=None,memo='调账'):
        """
        手工修改余额,传入摘要
        :return:
        """

        if not ordercode :
            raise PubErrorCustom("订单号不能为空")

        self.init_order_obj(ordercode=ordercode)
        self.order_obj.confirm_amount = self.order_obj.amount
        self.amount = self.order_obj.amount

        # 商户技术费
        stand_rate = get_Rate(self.order_obj.userid, paytypeid=self.order_obj.paytype)
        self.order_obj.tech_cost = float(self.order_obj.confirm_amount) * float(stand_rate)
        upd_bal(userid=self.order_obj.userid,
                bal=float(self.order_obj.confirm_amount) - float(self.order_obj.tech_cost), up_bal=self.amount,
                memo=memo, ordercode=self.order_obj.ordercode)

        # 代理费用
        agent_free = 0.0
        for item in UserLink.objects.filter(userid=self.order_obj.userid).order_by('-level'):
            rate = get_Rate(item.userid_to, paytypeid=self.order_obj.paytype)
            amount = float(self.order_obj.confirm_amount) * float(stand_rate - rate) if float(
                stand_rate - rate) > 0.0 else 0.0
            if amount > 0.0:
                upd_bal(userid=item.userid_to, bal=amount, up_bal=self.amount, memo=memo,
                        ordercode=self.order_obj.ordercode)

            stand_rate = rate
            agent_free += amount
        self.order_obj.agentfee = agent_free

        if self.order_obj.paypass in (0, 1):
            self.init_qrcode_obj(self.order_obj.qr_id)
            # 码商费用以及码商流水
            rate = get_Rate(self.qrcode_obj.userid, paytypeid=self.order_obj.paytype, type="2")
            self.order_obj.codefee = float(self.order_obj.confirm_amount) * float(rate)
            upd_bal(userid=self.qrcode_obj.userid, bal=self.order_obj.codefee, up_bal=self.amount, memo=memo,
                    ordercode=self.order_obj.ordercode,flag=True,upd_business_agent_tot=True)
        else:
            # 上游聚到服务费
            paypass = PayPass.objects.get(paypassid=self.order_obj.paypass)
            rate = get_Rate(paypass.paypassid, paytypeid=self.order_obj.paytype, type="0")
            self.order_obj.codefee = float(self.order_obj.confirm_amount) * float(rate)
            paypass.bal = float(paypass.bal) + float(self.order_obj.codefee)


        # 咱们自己的收入
        self.order_obj.myfee = float(self.order_obj.tech_cost) - float(self.order_obj.codefee) - float(agent_free)
        if self.order_obj.userid not in [3,20,5]:
            upd_bal(userid=1, bal=self.order_obj.myfee, up_bal=self.amount, memo=memo, ordercode=self.order_obj.ordercode,upd_business_agent_tot=True)

        self.order_obj.save()

    def get_tech_cost(self):
        """
        获取商户技术费
        :return:
        """
        self.stand_rate = get_Rate(self.order_obj.userid, paytypeid=self.order_obj.paytype)
        self.order_obj.tech_cost = float(self.order_obj.confirm_amount) * float(self.stand_rate)
        upd_bal(userid=self.order_obj.userid,
                bal=float(self.order_obj.confirm_amount) - float(self.order_obj.tech_cost), up_bal=self.amount,
                memo="扫码", ordercode=self.order_obj.ordercode)

    def get_agent_free(self):
        """
        获取代理费用
        :return:
        """
        agent_free = 0.0
        for item in UserLink.objects.filter(userid=self.order_obj.userid).order_by('-level'):
            rate = get_Rate(item.userid_to, paytypeid=self.order_obj.paytype)
            amount = float(self.order_obj.confirm_amount) * float(self.stand_rate - rate) if float(
                self.stand_rate - rate) > 0.0 else 0.0
            if amount > 0.0:
                upd_bal(userid=item.userid_to, bal=amount, up_bal=self.amount, memo="扫码",
                        ordercode=self.order_obj.ordercode)

            self.stand_rate = rate
            agent_free += amount
        self.order_obj.agentfee = agent_free

    def get_codefee(self):
        """
        获取码商/上游费用
        :return:
        """
        if self.order_obj.paypass in (0, 1):
            # 码商费用以及码商流水
            rate = get_Rate(self.qrcode_obj.userid, paytypeid=self.order_obj.paytype, type="2")
            self.order_obj.codefee = float(self.order_obj.confirm_amount) * float(rate)
            upd_bal(userid=self.qrcode_obj.userid, bal=self.order_obj.codefee, up_bal=self.amount, memo="扫码",
                    ordercode=self.order_obj.ordercode, flag=True, upd_business_agent_tot=True)
        else:
            # 上游聚到服务费
            paypass = PayPass.objects.get(paypassid=self.order_obj.paypass)
            rate = get_Rate(paypass.paypassid, paytypeid=self.order_obj.paytype, type="0")
            self.order_obj.codefee = float(self.order_obj.confirm_amount) * float(rate)
            paypass.bal = float(paypass.bal) + float(self.order_obj.codefee)

    def get_myfee(self):
        """
        获取咱们自己的收入
        :return:
        """
        self.order_obj.myfee = float(self.order_obj.tech_cost) - float(self.order_obj.codefee) - float(self.order_obj.agentfee)
        # if self.order_obj.userid not in [3,20,5]:
        #     upd_bal(userid=1, bal=self.order_obj.myfee,up_bal=self.amount, memo="扫码", ordercode=self.order_obj.ordercode,upd_business_agent_tot=True)


    def handlers(self):
        """
        回调后业务数据规整处理
        :return:
        """
        self.order_obj.status = "0"
        self.order_obj.confirm_amount = self.amount
        self.order_obj.pay_time = time.mktime(timezone.now().timetuple())

        self.get_tech_cost()
        self.get_agent_free()
        self.get_codefee()
        self.get_myfee()

        self.order_obj.save()

        self.qrcode_obj.usecount += 1
        self.qrcode_obj.save()

    def handler_after(self):
        """
        回调结束处理
        :return:
        """
        PayCallList.objects.create(**{
            "name": self.name if self.name else '',
            "amount": self.amount,
            "orderid": self.order_obj.ordercode if self.order_obj else 0,
            "status": "0" if self.flag else "1",
            "memo": self.memo,
            "qr_id": self.qrcode_obj.id if self.qrcode_obj else 0
        })

    def run(self):
        try:
            self.init_qrcode_obj()
            self.init_order_obj()
            self.handler_before_check()
            self.callback_request_to_server()
            self.handlers()
        except PubErrorCustom as e:
            self.memo = e.msg
            self.flag = False
        except Exception as e:
            self.memo = str(e)
            self.flag = False
        finally:
            self.handler_after()
            return None

    def handwork_run(self,order=None):
        """
        手工补入
        :param order:
        :return:
        """
        self.order_obj = order
        self.init_qrcode_obj(self.order_obj.qr_id)
        self.amount = float(order.amount)
        self.name = self.qrcode_obj.name
        self.callback_request_to_server()
        self.handlers()

        self.memo = '手工补分'
        self.flag = True
        self.handler_after()
        return None


class PayCallWechat(PayCallBase):

    def __init__(self,**kwargs):
        """
        微信回调
        :param kwargs:
        """
        kwargs.setdefault("type","QR001")
        super().__init__(**kwargs)

class PayCallNxys(PayCallBase):

    def __init__(self,**kwargs):
        """
        农信易扫
        :param kwargs:
        """
        kwargs.setdefault("type","QR010")
        super().__init__(**kwargs)

class PayCallJyys(PayCallBase):

    def __init__(self,**kwargs):
        """
        金燕易商
        :param kwargs:
        """
        kwargs.setdefault("type","QR015")
        super().__init__(**kwargs)

class PayCallZjnx(PayCallBase):

    def __init__(self,**kwargs):
        """
        浙江农信
        :param kwargs:
        """
        kwargs.setdefault("type","QR020")
        super().__init__(**kwargs)

class PayCallYzf(PayCallBase):

    def __init__(self,**kwargs):
        """
        易支付
        :param kwargs:
        """
        kwargs.setdefault("type","QR025")
        super().__init__(**kwargs)

class PayCallFlm(PayCallBase):

    def __init__(self,**kwargs):
        """
        付临门回调
        :param kwargs:
            tranlist : 付临门交易明细
        """
        self.tranlist = kwargs.get('tranlist')

        kwargs.setdefault("type","QR005")
        super().__init__(**kwargs)

    def call_fml_handler(self,isFlag=False):
        """
        :param isFlag: 是否手工补入
        :return:
        """
        if isFlag:
            FlmTranlist = FlmTranList.objects.get(orderid=self.order_obj.ordercode)
            FlmTranlist.umark = "0" if self.flag else "1"
            FlmTranlist.save()
        else:
            FlmTranList.objects.create(**{
                "name": self.name,
                'ordercode': self.tranlist['orderNo'],
                'remark': self.tranlist['remark'],
                'status': self.tranlist['status'],
                'amount': self.amount,
                'paytype': self.tranlist['paytype'],
                'orderid': self.order_obj.ordercode if self.order_obj else 0,
                'umark': "0" if self.flag else "1"
            })

    def run(self):
        super().run()
        self.call_fml_handler()
        return None

    def handwork_run(self,order=None):
        super().handwork_run(order=order)
        self.call_fml_handler(isFlag=True)
        return None

class PayCallLastPass(PayCallBase):

    def __init__(self,**kwargs):
        self.amount = float(kwargs.get('amount',0.0))
        self.name = kwargs.get('name',None)
        self.type = kwargs.get('type',None)

        self.qrcode_obj = None
        self.order_obj = None

        self.flag = True
        self.memo = ''

        logger.info("回调开始: 名称{}金额{}类型{}".format(self.name,self.amount,self.type))


    def handlers(self):
        """
        回调后业务数据规整处理
        :return:
        """
        self.order_obj.status = "0"
        self.order_obj.confirm_amount = self.amount
        self.order_obj.pay_time = time.mktime(timezone.now().timetuple())

        self.get_tech_cost()
        self.get_agent_free()
        self.get_codefee()
        self.get_myfee()

        self.order_obj.save()

    def run(self,order=None):
        """
        :param order:
        :return:
        """
        self.order_obj = order
        self.amount = float(order.amount)
        self.callback_request_to_server()
        self.handlers()

        self.memo = '上游回调成功'
        self.flag = True
        self.handler_after()
        return None


    def handwork_run(self,order=None):
        """
        :param order:
        :return:
        """
        self.order_obj = order
        self.amount = float(order.amount)
        self.callback_request_to_server()
        self.handlers()

        self.memo = '手工补入成功!'
        self.flag = True
        self.handler_after()
        return None

def get_qrcode_path(order):

    qr_class = Choices_to_Dict('qrtype_link_qrClass')[order.qr_type]()

    if order.qr_id:
        qrcode_obj = qr_class.get_qrcode_obj(order.qr_id)
        if qr_class.qrcode_valid(order.createtime):
            return {"data": {
                "amount": round(float(order.amount),2),
                "url": qrcode_obj.url,
                "expire_time": qr_class.get_expire_time(order.createtime),
                "flag": "2",
                "type": qrcode_obj.type
            }}
        else:
            return {"data": {
                "amount": round(float(order.amount),2),
                "url": qrcode_obj.url,
                "expire_time": qr_class.get_expire_time(order.createtime),
                "flag": "1",
                "type": qrcode_obj.type
            }}
    else:
        qrcode_obj = qr_class.get_qrcode(order=order)
        order.qr_id = qrcode_obj.id
        order.save()

        return {"data": {
            "amount": round(float(order.amount),2),
            "url": qrcode_obj.url,
            "expire_time": qr_class.get_expire_time(order.createtime),
            "flag": "1",
            "type": qrcode_obj.type
        }}
