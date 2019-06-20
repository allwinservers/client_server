from utils.exceptions import PubErrorCustom
from apps.pay.models import PayType,PayPass
from apps.order.models import Order
from apps.public.models import QrCodeLinkPayType
from libs.utils.mytime import timestamp_toDatetime,datetime_toTimestamp
from apps.utils import url_join
from apps.pay.models import PayType,PayPassLinkType
from apps.lastpass.utils import LastPass_JLF,LastPass_TY,LastPass_DD,LastPass_YZL,LastPass_OSB,LastPass_BAOZHUANKA,LastPass_LIMAFU,LastPass_JUXING,LastPass_MK,LastPass_TONGYU

class CreateOrder(object):

    def __init__(self,**kwargs):

        self.user = kwargs.get('user')
        self.request_param = kwargs.get("request_param")
        self.lock = kwargs.get("lock","0")

        self.paypasslinktype = None
        self.qrcodelinkpaytype = None

        self.order = None

    def get_paypasslinktype(self):
        paypass = PayPassLinkType.objects.raw(
            """
            SELECT t1.*,t2.typename ,t2.name as paytypename,t3.name as paypassname FROM paypasslinktype as t1 
            INNER JOIN paytype as t2 on t1.paytypeid = t2.paytypeid
            INNER JOIN paypass as t3 on t1.passid = t3.paypassid
            WHERE t1.to_id=%s and t1.type='1' 
            """, [self.user.userid]
        )
        paypass = list(paypass)
        return paypass

    def check_request_param(self):

        if not self.request_param.get("down_ordercode"):
            raise PubErrorCustom("订单号不存在!")

        try:
            amount = float(self.request_param.get('amount'))
            if amount <= 0.0:
                raise PubErrorCustom("订单金额不能为0")
        except:
            raise PubErrorCustom("订单金额格式不正确!")

        # try:
        #     timestamp_toDatetime(self.request_param.get('createtime'))
        # except:
        self.request_param['createtime'] = datetime_toTimestamp()

        if not self.request_param.get('client_ip'):
            raise PubErrorCustom("客户端IP不能为空!")

        if not self.request_param.get("notifyurl"):
            raise PubErrorCustom("回调地址不能为空!")

        if not self.request_param.get("ismobile"):
            raise PubErrorCustom("是否手机标志不能为空!")

        if Order.objects.filter(userid=self.user.userid, down_ordercode=self.request_param.get('down_ordercode')).exists():
            raise PubErrorCustom("该订单已生成,请勿重复生成订单!")

        paypass = self.get_paypasslinktype()

        if not self.request_param.get('paytypeid'):
            if not len(paypass):
                raise PubErrorCustom("通道暂未开放!")
            if len(paypass) > 1:
                raise PubErrorCustom("通道暂未开放!")
            self.request_param['paytypeid'] = paypass[0].paytypeid
            self.paypasslinktype = paypass[0]
        else:
            for item in paypass:
                if str(item.paytypeid) == str(self.request_param.get('paytypeid')):
                    self.paypasslinktype = item
            if not self.paypasslinktype:
                raise PubErrorCustom("通道传入有误!")

        if (amount < 100.0 or amount > 5000.0 or amount % 100.0 > 0) and str(self.paypasslinktype.paytypeid)=='13':
            raise PubErrorCustom("金额范围[100,5000],并且金额是100的倍数!")

        if str(self.paypasslinktype.paytypeid)=='19' and amount not in [10,20,30,50,100,200,300,500]:
            raise PubErrorCustom("金额固定为10,20,30,50,100,200,300,500")

        if self.paypasslinktype.passid in (0, 1):
            try:
                self.qrcodelinkpaytype = QrCodeLinkPayType.objects.get(paytypeid=self.paypasslinktype.paytypeid)
            except QrCodeLinkPayType.DoesNotExist:
                raise PubErrorCustom("支付方式与二维码类型未关联!")

    def create_order_handler(self):

        self.order  = Order.objects.create(**{
            "userid": self.user.userid,
            "down_ordercode": self.request_param.get("down_ordercode"),
            "paypass": self.paypasslinktype.passid,
            "paypassname": self.paypasslinktype.paypassname,
            "paytype": self.paypasslinktype.paytypeid,
            "paytypename": self.paypasslinktype.typename + self.paypasslinktype.paytypename,
            "amount": self.request_param.get("amount"),
            "status": "1",
            "ismobile": self.request_param.get("ismobile"),
            "client_ip": self.request_param.get("client_ip"),
            "notifyurl": self.request_param.get("notifyurl"),
            "createtime": self.request_param.get("createtime"),
            'qr_type': self.qrcodelinkpaytype.type if self.qrcodelinkpaytype and len(self.qrcodelinkpaytype.type) else "",
            "keep_info": self.request_param,
            "lock":self.lock
        })

    def select_pass(self):
        # 傲银支付
        if self.paypasslinktype.passid in (0, 1):
            if not self.request_param.get('allwin_test'):
                if float(self.request_param.get("amount")) < 300 or float(self.request_param.get("amount")) > 5000:
                    raise PubErrorCustom("限额300至5000")
            return QrTypePage(self.qrcodelinkpaytype.type, self.order).run()
        # 吉米支付宝原生渠道
        elif str(self.paypasslinktype.passid) == '2':
            raise PubErrorCustom("通道量满单，尽快配量")
        #聚力支付
        elif str(self.paypasslinktype.passid) == '4':
            request_data = {
                "uid": str(self.order.userid),
                "amount": self.order.amount,
                "outTradeNo": str(self.order.ordercode),
                "ip": self.order.client_ip,
                "notifyUrl": url_join('/callback_api/lastpass/juli_callback')
            }
            res = LastPass_JLF(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]}
        #天亿支付
        elif str(self.paypasslinktype.passid) == '5':
            if str(self.paypasslinktype.paytypeid) == "3":
                pay_bankcode="904"
            elif str(self.paypasslinktype.paytypeid) == "13":
                pay_bankcode = "904"
            elif str(self.paypasslinktype.paytypeid) == "14":
                pay_bankcode="901"
            else:
                raise PubErrorCustom("支付通道有误，请联系客服!")

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/tianyi_callback'),
                "pay_bankcode" : pay_bankcode
            }
            res = LastPass_TY(data=request_data).run()

            return {"res": res,"userid":self.order.userid,"ordercode":self.order.ordercode,"htmlfile":"pay.html"}
        #哒哒支付
        elif str(self.paypasslinktype.passid) == '6':
            if str(self.paypasslinktype.paytypeid) == "16":
                pay_bankcode="923"
            elif str(self.paypasslinktype.paytypeid) == "6":
                pay_bankcode="924"
            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/api/lastpass/dada_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_DD(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom("生成订单失败,请稍后再试!")

            with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
        #一直联
        elif str(self.paypasslinktype.passid) == '7':
            request_data = {
                "out_order_no": str(self.order.ordercode),
                "total_fee": self.order.amount,
                "notify_url": url_join('/api/lastpass/yzl_callback')
            }
            res = LastPass_YZL(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom("生成订单失败,请稍后再试!")

            with open('/var/html/yzl/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/yzl/{}.html').format(self.order.ordercode)}
        #OSB
        elif str(self.paypasslinktype.passid) == '8':
            if str(self.paypasslinktype.paytypeid) == "13":
                type="alipay"
            elif str(self.paypasslinktype.paytypeid) == "3":
                type = "alipay"
            elif str(self.paypasslinktype.paytypeid) == "14":
                type="wechat"
            request_data = {
                "type": type,
                "total": self.order.amount,
                "api_order_sn": str(self.order.ordercode),
                "notify_url": url_join('/api/lastpass/osb_callback')
            }
            res = LastPass_OSB(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]['h5_url']}
        #BAOZHUANKA
        elif str(self.paypasslinktype.passid) == '9':

            request_data = {
                "total_amount": self.order.amount,
                "order_no": str(self.order.ordercode),
                "callbackurl": url_join('/api/lastpass/baozhanka_callback')
            }
            res = LastPass_BAOZHUANKA(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            with open('/var/html/yunduan/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/yunduan/{}.html').format(self.order.ordercode)}
        # LIMAFU
        elif str(self.paypasslinktype.passid) == '10':

            request_data = {
                "money": str(self.order.amount),
                "orderid": str(self.order.ordercode),
                "notifyurl": url_join('/api/lastpass/limafu_callback'),
                "userip": self.order.client_ip
            }
            res = LastPass_LIMAFU(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]['url']}
        # JUXING
        elif str(self.paypasslinktype.passid) == '11':

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "mchOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/juxing_callback')
            }
            res = LastPass_JUXING(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # MK
        elif str(self.paypasslinktype.passid) == '12':
            pay_bankcode = "904"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/mk_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_MK(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        # TONGYU
        elif str(self.paypasslinktype.passid) == '13':

            request_data = {
                "out_order_no": str(self.order.ordercode),
                "payment_fee": int(float(self.order.amount) * float(100.0)),
                "notify_url": url_join('/callback_api/lastpass/tongyu_callback'),
                "bill_create_ip": self.order.client_ip
            }
            res = LastPass_TONGYU(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}

    def run(self):
        self.check_request_param()
        self.create_order_handler()
        return self.select_pass()


# def get_type(request):
#
#
#     paypass = PayPassLinkType.objects.raw(
#         """
#         SELECT t1.*,t2.typename ,t2.name as paytypename FROM paypasslinktype as t1
#         INNER JOIN paytype as t2 on t1.paytypeid = t2.paytypeid
#         WHERE t1.to_id=%s and t1.type='1'
#         """, [request.user.userid]
#     )
#     paypass = list(paypass)
#     if not len(paypass):
#         raise PubErrorCustom("请联系客服设置支付方式!")
#     if len(paypass)>1:
#         raise PubErrorCustom("多种方式请通过支付方式接口获取,根据需要选择!")
#     paypass=paypass[0]
#     return paypass.paytypeid
#
# def check_type(request,data):
#     paypass = PayPassLinkType.objects.raw(
#         """
#         SELECT t1.*,t2.typename ,t2.name as paytypename FROM paypasslinktype as t1
#         INNER JOIN paytype as t2 on t1.paytypeid = t2.paytypeid
#         WHERE t1.to_id=%s and t1.type='1'
#         """, [request.user.userid]
#     )
#     for item in paypass:
#         if str(item.paytypeid) == str(data.get('paytypeid')):
# #             return True
# #
# #     return False
#
# def check_data(request):
#
#     data = request.data_format
#
#     if not data.get('paytypeid'):
#         data['paytypeid'] = get_type(request)
#     else:
#         if not check_type(request,data):
#             raise PubErrorCustom("支付方式不正确!")
#
#     try:
#         paytype = PayType.objects.get(paytypeid=data['paytypeid'])
#     except PayType.DoesNotExist:
#         raise PubErrorCustom("支付方式不存在,请通过接口获取!")
#
#     qrcodelinkpaytype=""
#     if request.user.paypassid in (0, 1):
#         try:
#             qrcodelinkpaytype = QrCodeLinkPayType.objects.get(paytypeid=data['paytypeid'])
#         except QrCodeLinkPayType.DoesNotExist:
#             raise PubErrorCustom("支付方式与二维码类型未关联!")
#
#     if not data.get("down_ordercode"):
#         raise PubErrorCustom("订单号不存在!")
#
#     if Order.objects.filter(userid=request.user.userid, down_ordercode=data.get('down_ordercode')).exists():
#         raise PubErrorCustom("该订单已生成,请勿重复生成订单!")
#
#     try:
#         amount = float(data.get('amount'))
#         if amount <= 0.0:
#             raise PubErrorCustom("订单金额不能为0")
#     except:
#         raise PubErrorCustom("订单金额格式不正确!")
#
#     try:
#         timestamp_toDatetime(data.get('createtime'))
#     except:
#         data['createtime'] = datetime_toTimestamp()
#         # raise PubErrorCustom("创建订单时间不正确!")
#
#     if not data.get('client_ip'):
#         raise PubErrorCustom("客户端IP不能为空!")
#
#     if not data.get("notifyurl"):
#         raise PubErrorCustom("回调地址不能为空!")
#
#     if not data.get("ismobile"):
#         raise PubErrorCustom("是否手机标志不能为空!")
#
#     return paytype,qrcodelinkpaytype
#
#
# def check_passtype(request):
#     try:
#         paypass = PayPass.objects.get( paypassid= request.user.paypassid)
#     except PayPass.DoesNotExist:
#         raise PubErrorCustom("支付渠道不存在!")
#
#     return paypass
#
# def create_order_handler(data,request,paytype,paypass,qrcodelinkpaytype):
#
#     order = Order.objects.create(**{
#         "userid": request.user.userid,
#         "down_ordercode": data.get("down_ordercode"),
#         "paypass" : paypass.paypassid,
#         "paypassname" : paypass.name,
#         "paytype": paytype.paytypeid,
#         "paytypename": paytype.typename + paytype.name,
#         "amount": data.get("amount"),
#         "status": "1",
#         "ismobile": data.get("ismobile"),
#         "client_ip": data.get("client_ip"),
#         "notifyurl": data.get("notifyurl"),
#         "createtime": data.get("createtime"),
#         'qr_type' : qrcodelinkpaytype.type if qrcodelinkpaytype and len(qrcodelinkpaytype) else "",
#         "keep_info": data
#     })
#
#     #傲银渠道
#     if request.user.paypassid in (0,1):
#         if not data.get('allwin_test'):
#             if float(data.get("amount")) < 300 or float(data.get("amount")) > 5000:
#                 raise PubErrorCustom("限额300至5000")
#         return QrTypePage(qrcodelinkpaytype.type,order).run()
#     #吉米支付宝原生渠道
#     elif str(request.user.paypassid) == '2':
#         raise PubErrorCustom("通道量满单，尽快配量")
#     elif str(request.user.paypassid) == '4':
#         request_data = {
#             "uid": str(order.userid),
#             "amount": order.amount,
#             "outTradeNo": str(order.ordercode),
#             "ip": order.client_ip,
#             "notifyUrl": url_join('/api/lastpass/juli_callback')
#         }
#         res = LastPass_JLF(data=request_data).run()
#         if not res[0]:
#             raise PubErrorCustom(res[1])
#         return {"path": res[1]}
#     elif str(request.user.paypassid) == '5':
#         request_data = {
#             "pay_orderid": str(order.ordercode),
#             "pay_amount": order.amount,
#             "pay_notifyurl": url_join('/api/lastpass/tianyi_callback')
#         }
#         res = LastPass_TY(data=request_data).run()
#         print(res)
#         if not res[0]:
#             raise PubErrorCustom("生成订单失败,请稍后再试!")
#
#         with open('/var/html/tianyi/{}.html'.format(order.ordercode), 'w') as f1:
#             f1.write(res[1])
#         return {"path": url_join('/tianyi/{}.html').format(order.ordercode) }


class QrTypePage(object):

    def __init__(self,type=None,order=None):
        self.type = type
        self.order = order

        self.custom_select = [
            {
                "userid":11,
                "type":'QR005',
                "paytype" : 'alipay'
            },
            {
                "userid": 4,
                "type": 'QR005',
                "paytype": 'wechat'
            }
        ]

    def run(self):

        for item in self.custom_select:
            if item['userid'] == self.order.userid and item['type'] == self.type :
                return {"path": url_join("/pay/#/{}/{}".format(item['paytype'],self.order.ordercode))}

        if self.type == 'QR001':
            return {"path": url_join("/pay/#/wechat/{}".format(self.order.ordercode))}
        elif self.type == 'QR005':
            return {"path": url_join("/pay/#/wechat/{}".format(self.order.ordercode))}
        elif self.type == 'QR010':
            return {"path": url_join("/pay/#/wechat/{}".format(self.order.ordercode))}
        elif self.type == 'QR015':
            return {"path": url_join("/pay/#/wechat/{}".format(self.order.ordercode))}
        elif self.type == 'QR020':
            return {"path": url_join("/pay/#/wechat/{}".format(self.order.ordercode))}

