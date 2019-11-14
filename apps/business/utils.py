import demjson
from utils.exceptions import PubErrorCustom
from apps.pay.models import PayType, PayPass
from apps.order.models import Order
from apps.public.models import QrCodeLinkPayType
from libs.utils.mytime import timestamp_toDatetime, datetime_toTimestamp
from apps.utils import url_join
from apps.pay.models import PayType, PayPassLinkType
from apps.lastpass.utils1 import LastPass_JLF, LastPass_TY, LastPass_DD, \
    LastPass_YZL, LastPass_OSB, LastPass_BAOZHUANKA, LastPass_LIMAFU, LastPass_JUXING, LastPass_MK, \
    LastPass_TONGYU, LastPass_JIAE, LastPass_DONGFANG, LastPass_XIONGMAO, LastPass_KUAILAI, LastPass_SHANGHU, \
    LastPass_HAOYUN, LastPass_FENGNIAO, LastPass_LIANJINHAI, LastPass_JIUFU, LastPass_XINGYUANFU, LastPass_XINGYUN, \
    LastPass_CHUANGYUAN, \
    LastPass_JLFZFB, LastPass_WXHFYS, LastPass_ZFBHFYS, LastPass_SDGY, LastPass_JIABAO, LastPass_QIANWANG, \
    LastPass_CHUANGYUAN_YUANSHENG, \
    LastPass_MIFENG, LastPass_TIGER, LastPass_GUAISHOU, LastPass_DINGSHENG, LastPass_CZKJ, LastPass_SBGM, \
    LastPass_XINGHE, LastPass_YUANLAI, \
    LastPass_JINGSHA, LastPass_ANJIE, LastPass_hahapay, LastPass_SHUIJING, LastPass_KUAIJIE, LastPass_ALLWIN, \
    LastPass_SHUIJING_NEW, LastPass_BAWANGKUAIJIE, \
    LastPass_YANXINGZHIFU, LastPass_JINGDONG, LastPass_JIAHUI, LastPass_ZHONGXING, LastPass_ZHAOXING, \
    LastPass_TIANCHENG, LastPass_IPAYZHIFUBAO, LastPass_YSLH, \
    LastPass_HUIHUANG, LastPass_JUXINGNEW, LastPass_LONGSHI


class CreateOrder(object):

    def __init__(self, **kwargs):

        self.user = kwargs.get('user')
        self.request_param = kwargs.get("request_param")
        self.lock = kwargs.get("lock", "0")

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

        if Order.objects.filter(userid=self.user.userid,
                                down_ordercode=self.request_param.get('down_ordercode')).exists():
            raise PubErrorCustom("该订单已生成,请勿重复生成订单!")

        paypass = self.get_paypasslinktype()

        print(self.request_param)
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

        if str(self.paypasslinktype.passid) == '47':
            if 300.0 <= float(amount) <= 10000.0:
                pass
            else:
                raise PubErrorCustom("金额范围在[500-10000]")

        # print()
        if str(self.paypasslinktype.passid) == '22':
            if amount % 100 == 0 and int(amount) in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000,
                                                     4000, 5000]:
                pass
            else:
                raise PubErrorCustom("金额范围在[100,200,300,400,500,600,700,800,900,1000,2000,3000,4000,5000]")
        # elif (amount < 100.0 or amount > 5000.0 or amount % 100.0 > 0) and str(self.paypasslinktype.paytypeid)=='13':
        #     raise PubErrorCustom("金额范围[100,5000],并且金额是100的倍数!")

        if str(self.paypasslinktype.passid) == '52':
            if amount % 100 == 0 and int(amount) in [500, 1000, 5000]:
                pass
            else:
                raise PubErrorCustom("金额范围在[ 500,1000,5000 ]")

        if str(self.paypasslinktype.passid) == '58':
            if amount % 1 == 0 and 100 <= int(amount) <= 5000:
                pass
            else:
                raise PubErrorCustom("金额范围在100-5000,并且是整数")

        if str(self.paypasslinktype.passid) == '59':
            if amount % 1 == 0 and 50 <= int(amount) <= 5000:
                pass
            else:
                raise PubErrorCustom("金额范围在50-5000,并且是整数")

        # if str(self.paypasslinktype.passid)=='55':
        #     if amount % 100 == 0 and int(amount) in [ 500,1000,2000,3000,5000 ]:
        #         pass
        #     else:
        #         raise PubErrorCustom("金额范围在[ 500,1000,2000,3000,5000 ]")

        if str(self.paypasslinktype.passid) == '57':
            if 100.0 <= amount <= 5000.0:
                pass
            else:
                raise PubErrorCustom("金额范围是100-5000")

        if str(self.paypasslinktype.passid) == '60':
            if 300.0 <= amount <= 5000.0:
                pass
            else:
                raise PubErrorCustom("金额范围是300-5000")

        if str(self.paypasslinktype.passid) == '56':
            if float(amount) in [40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]:
                pass
            else:
                raise PubErrorCustom("金额范围在[ 40,50,60,70,80,90,100 ]")

        if str(self.paypasslinktype.passid) == '38':
            if int(amount) not in [500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]:
                raise PubErrorCustom("金额范围在[500,600,700,800,900,1000,1500,2000,2500,3000,3500,4000,4500,5000]")

        if str(self.paypasslinktype.passid) == '24':
            if int(amount) not in [198, 297, 396, 499, 785, 998, 1588, 2466, 3480, 3998, 4588]:
                raise PubErrorCustom("金额范围在[198,297,396,499,785,998,1588,2466,3480,3998,4588]")

        if str(self.paypasslinktype.passid) in ['28', '29']:
            if int(amount) not in [50, 100, 200]:
                raise PubErrorCustom("金额范围在[50,100,200]")

        if str(self.paypasslinktype.passid) in ['63', '64']:
            if float(amount) not in [30.0, 50.0, 100.0]:
                raise PubErrorCustom("金额范围在[30,50,100]")

        if str(self.paypasslinktype.passid) in ['44', '65']:
            if float(amount) not in [324.0, 475.0, 569.0, 670.0, 814.0, 916.0, 1366.0, 1978.0, 2308.0, 2793.0, 3438.0,
                                     3058.0, 3891.0, 4577.0]:
                raise PubErrorCustom("金额范围在[324,475,569,670,814,916,1366,1978,2308,2793,3438,3058,3891,4577]")

        if str(self.paypasslinktype.passid) == '48':
            if float(amount) not in [100.0, 200.0, 300.0, 400.0, 500.0]:
                raise PubErrorCustom("金额范围在[100,200,300,400,500]")

        if (amount < 100.0 or amount > 5000.0 or amount % 1.0 > 0) and str(self.paypasslinktype.passid) == '17':
            raise PubErrorCustom("金额范围[100,5000],并且金额是整元!")

        # if str(self.paypasslinktype.paytypeid)=='19' and amount not in [10,20,30,50,100,200,300,500]:
        #     raise PubErrorCustom("金额固定为10,20,30,50,100,200,300,500")

        if self.paypasslinktype.passid in (0, 1):
            try:
                self.qrcodelinkpaytype = QrCodeLinkPayType.objects.get(paytypeid=self.paypasslinktype.paytypeid)
            except QrCodeLinkPayType.DoesNotExist:
                raise PubErrorCustom("支付方式与二维码类型未关联!")

    def create_order_handler(self):

        self.order = Order.objects.create(**{
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
            'qr_type': self.qrcodelinkpaytype.type if self.qrcodelinkpaytype and len(
                self.qrcodelinkpaytype.type) else "",
            "keep_info": self.request_param,
            "lock": self.lock
        })

    def select_pass(self):
        # 傲银支付
        if self.paypasslinktype.passid in (0, 1):

            return None

            #     if not self.request_param.get('allwin_test'):
            #         if float(self.request_param.get("amount")) < 300 or float(self.request_param.get("amount")) > 5000:
            #             raise PubErrorCustom("限额300至5000")
            #     return QrTypePage(self.qrcodelinkpaytype.type, self.order).run()
            # # 吉米支付宝原生渠道
            # elif str(self.paypasslinktype.passid) == '2':
            #     raise PubErrorCustom("通道量满单，尽快配量")

            return {
                "path": "alipays://platformapi/startapp?appId=20000067&url=https://mclient.alipay.com/h5/peerpay.htm?enableWK=YES&biz_no=2019092404200382821044739889_08c0921d39d53c55f89d20f509cf4e2b&app_name=tb&sc=card&__webview_options__=pd%3DNO&sid=12c6fa9a351b3211dc58c92a8e3aeb89&sourceType=other&suid=76eb71e2-6561-4f15-a02a-67b7319a1289&ut_sk=1.WkhBxxFd0TwDAIAsLGK5b40v_21646297_1569336683124.Copy.windvane&un=0d5fb49cb447af33bbeeeafdb2768e28&share_crt_v=1&spm=a2159r.13376460.0.0&sp_tk=77+lQW9kRFlubDNhZFDvv6U=&cpp=1&shareurl=true&short_name=h.eN6BalY&sm=e478a4&app=macos_safari"}
        # 聚力支付
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
        # 天亿支付
        elif str(self.paypasslinktype.passid) == '5':

            if str(self.paypasslinktype.paytypeid) == "1":
                productId = 8002
            elif str(self.paypasslinktype.paytypeid) == "6":
                productId = 8003
            elif str(self.paypasslinktype.paytypeid) == "12":
                productId = 8006
            elif str(self.paypasslinktype.paytypeid) == '11':
                productId = 8007
            else:
                raise PubErrorCustom("支付通道有误，请联系客服!")

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "mchOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/tianyi_callback'),
                "productId": productId
            }
            res = LastPass_JUXING(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # elif str(self.paypasslinktype.passid) == '5':
        #     if str(self.paypasslinktype.paytypeid) == "3":
        #         pay_bankcode="904"
        #     elif str(self.paypasslinktype.paytypeid) == "13":
        #         pay_bankcode = "904"
        #     elif str(self.paypasslinktype.paytypeid) == "14":
        #         pay_bankcode="901"
        #     else:
        #         raise PubErrorCustom("支付通道有误，请联系客服!")
        #
        #     request_data = {
        #         "pay_orderid": str(self.order.ordercode),
        #         "pay_amount": self.order.amount,
        #         "pay_notifyurl": url_join('/callback_api/lastpass/tianyi_callback'),
        #         "pay_bankcode" : pay_bankcode
        #     }
        #     res = LastPass_TY(data=request_data).run()
        #
        #     return {"res": res,"userid":self.order.userid,"ordercode":self.order.ordercode,"htmlfile":"pay.html"}
        # 哒哒支付
        elif str(self.paypasslinktype.passid) == '6':
            if str(self.paypasslinktype.paytypeid) == "16":
                pay_bankcode = "923"
            elif str(self.paypasslinktype.paytypeid) == "6":
                pay_bankcode = "924"
            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/dada_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_DD(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom("生成订单失败,请稍后再试!")

            with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
        # 一直联
        elif str(self.paypasslinktype.passid) == '7':
            request_data = {
                "out_order_no": str(self.order.ordercode),
                "total_fee": self.order.amount,
                "notify_url": url_join('/callback_api/lastpass/yzl_callback')
            }
            res = LastPass_YZL(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom("生成订单失败,请稍后再试!")

            with open('/var/html/yzl/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/yzl/{}.html').format(self.order.ordercode)}
        # OSB
        elif str(self.paypasslinktype.passid) == '8':
            if str(self.paypasslinktype.paytypeid) == "13":
                type = "alipay"
            elif str(self.paypasslinktype.paytypeid) == "3":
                type = "alipay"
            elif str(self.paypasslinktype.paytypeid) == "14":
                type = "wechat"
            request_data = {
                "type": type,
                "total": self.order.amount,
                "api_order_sn": str(self.order.ordercode),
                "notify_url": url_join('/callback_api/lastpass/osb_callback')
            }
            res = LastPass_OSB(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]['h5_url']}
        # BAOZHUANKA
        elif str(self.paypasslinktype.passid) == '9':

            request_data = {
                "total_amount": self.order.amount,
                "order_no": str(self.order.ordercode),
                "callbackurl": url_join('/callback_api/lastpass/baozhanka_callback')
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
                "notifyurl": url_join('/callback_api/lastpass/limafu_callback'),
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
        # jiae
        elif str(self.paypasslinktype.passid) == '14':

            request_data = {
                "fxddh": str(self.order.ordercode),
                "fxfee": str(float(self.order.amount)),
                "fxnotifyurl": url_join('/callback_api/lastpass/jiae_callback'),
                'fxbackurl': url_join("/pay/#/juli"),
                "fxip": self.order.client_ip
            }
            res = LastPass_JIAE(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 东方
        elif str(self.paypasslinktype.passid) == '15':
            request_data = {
                "out_order_no": str(self.order.ordercode),
                "total_fee": self.order.amount,
                "notify_url": url_join('/callback_api/lastpass/dongfang_callback')
            }
            res = LastPass_DONGFANG(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay2.html"}
        # 熊猫
        elif str(self.paypasslinktype.passid) == '16':
            request_data = {
                "order_id": str(self.order.ordercode),
                "price": self.order.amount,
                "notify_url": url_join('/callback_api/lastpass/xiongmao_callback')
            }
            res = LastPass_XIONGMAO(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 快来
        elif str(self.paypasslinktype.passid) == '17':

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "umNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/kuailai_callback'),
                'returnUrl': url_join("/pay/#/juli"),
                'errorUrl': url_join("/pay/#/juli"),
            }
            res = LastPass_KUAILAI(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            with open('/var/html/yunduan/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/yunduan/{}.html').format(self.order.ordercode)}
        # SHANGHU
        elif str(self.paypasslinktype.passid) == '18':
            request_data = {
                "orderid": str(self.order.ordercode),
                "amount": float(self.order.amount)
            }
            res = LastPass_SHANGHU(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay3.html"}
        # HOAYUN
        elif str(self.paypasslinktype.passid) == '19':

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "mchOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/haoyun_callback')
            }
            res = LastPass_HAOYUN(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # FENGNIAO
        elif str(self.paypasslinktype.passid) == '20':

            request_data = {
                "price": int(float(self.order.amount) * float(100.0)),
                "merchantOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/fengniao_callback')
            }
            res = LastPass_FENGNIAO(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # LIANJINHAI
        elif str(self.paypasslinktype.passid) == '21':

            request_data = {
                "total_fee": str(int(float(self.order.amount) * float(100.0))),
                "out_trade_no": 'ALLWIN8888' + str(self.order.ordercode),
                "notify_url": url_join('/callback_api/lastpass/lianjinhai_callback')
            }
            res = LastPass_LIANJINHAI(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # MK
        elif str(self.paypasslinktype.passid) == '22':
            # pay_bankcode = "926"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/jiufu_callback')
            }
            res = LastPass_JIUFU(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        # 星元付(微信、支付宝)
        elif str(self.paypasslinktype.passid) in ['23', '24', '39', '40']:

            if str(self.paypasslinktype.passid) == '23':
                # 微信
                type = '8068'
            elif str(self.paypasslinktype.passid) == '24':
                # 支付宝
                type = '8063'
            elif str(self.paypasslinktype.passid) == '39':
                type = '8080'
            else:
                type = '8060'

            request_data = {
                "value": str(self.order.amount),
                "orderid": str(self.order.ordercode),
                "callbackurl": url_join('/callback_api/lastpass/xingyuanfu_callback'),
                'type': type,
            }
            # res = LastPass_XINGYUANFU(data=request_data).run()
            # if not res[0]:
            #     raise PubErrorCustom(res[1])

            # if type=='8057':
            #     temple_before = '<!DOCTYPE html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head><div style="height:100%;margin-top:10em;text-align:center;"><a href="'
            #     temple_after='" style="border:.1em solid red;font-size:5.2em;">点击打开微信付款</a></div></html>'
            #     print(res[1])
            #     value = temple_before + res[1].split('<a href="')[1].split('" style')[0] + temple_after
            # else:
            #     value = res[1]
            #
            # with open('/var/html/yunduan/{}.html'.format(self.order.ordercode), 'w') as f1:
            #     f1.write(value)
            # return {"path": url_join('/yunduan/{}.html').format(self.order.ordercode)}
            res = LastPass_XINGYUANFU(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay4.html"}

        # XINGYUN
        elif str(self.paypasslinktype.passid) == '25':

            request_data = {
                "amount": self.order.amount,
                "orderid": str(self.order.ordercode),
                "notify_url": url_join('/api/lastpass/xingfu_callback'),
                "client_ip": self.order.client_ip,
                "paytype": 'ALIPAY_TRANS'
            }
            res = LastPass_XINGYUN(data=request_data).run()
            # print(res)
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # XINGYUN
        elif str(self.paypasslinktype.passid) == '26':

            print(self.order.amount)
            request_data = {
                "payMoney": str(self.order.amount),
                "orderSN": str(self.order.ordercode),
                "refreshForResult": url_join('/callback_api/lastpass/chuangyuan_callback')
            }
            res = LastPass_CHUANGYUAN(data=request_data).run()
            # print(res)
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 聚力支付宝
        elif str(self.paypasslinktype.passid) == '27':
            request_data = {
                "uid": str(self.order.userid),
                "amount": self.order.amount,
                "outTradeNo": str(self.order.ordercode),
                "ip": self.order.client_ip,
                "notifyUrl": url_join('/callback_api/lastpass/juli_callback')
            }
            res = LastPass_JLFZFB(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]}
        # 聚力支付宝
        elif str(self.paypasslinktype.passid) == '28':
            request_data = {
                "totalAmount": self.order.amount,
                "outTradeNo": str(self.order.ordercode),
                "orgCreateIp": self.order.client_ip,
                "notifyUrl": url_join('/callback_api/lastpass/wxhf_callback')
            }
            res = LastPass_WXHFYS(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]}
        # 聚力支付宝
        elif str(self.paypasslinktype.passid) == '29':
            request_data = {
                "totalAmount": self.order.amount,
                "outTradeNo": str(self.order.ordercode),
                "orgCreateIp": self.order.client_ip,
                "notifyUrl": url_join('/callback_api/lastpass/wxhf_callback')
            }
            res = LastPass_ZFBHFYS(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]}
        # 聚力支付宝
        elif str(self.paypasslinktype.passid) == '30':
            # if str(self.paypasslinktype.paytypeid) == "16":
            #     pay_bankcode="923"
            # elif str(self.paypasslinktype.paytypeid) == "6":
            #     pay_bankcode="924"

            pay_bankcode = "904"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/sdgy_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_SDGY(data=request_data).run()

            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]}
        # 加宝
        elif str(self.paypasslinktype.passid) == '31':
            pay_bankcode = "935"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/jiabao_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_JIABAO(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        # 千旺
        elif str(self.paypasslinktype.passid) == '32':

            request_data = {
                "merch_order_id": str(self.order.ordercode),
                "fee": int(float(self.order.amount) * float(100.0)),
                "notify_url": url_join('/callback_api/lastpass/qianwang_callback')
            }
            res = LastPass_QIANWANG(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 创源支付宝原生
        elif str(self.paypasslinktype.passid) == '33':

            request_data = {
                "orderNo": str(self.order.ordercode),
                "money": float(self.order.amount),
                "notifyUrl": url_join('/callback_api/lastpass/chuangyuan_yuansheng_callback')
            }
            res = LastPass_CHUANGYUAN_YUANSHENG(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 蜜蜂支付宝
        elif str(self.paypasslinktype.passid) in ['34', '35']:

            if str(self.paypasslinktype.passid) == '34':
                paytype = 'AlipayH5'
            else:
                paytype = 'wechatpayH5'

            request_data = {
                "order_id": str(self.order.ordercode),
                "price": float(self.order.amount),
                "notify_url": url_join('/api/lastpass/mifeng_callback'),
                'paytype': paytype
            }
            res = LastPass_MIFENG(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # MK
        elif str(self.paypasslinktype.passid) in ['36', '37', '50']:
            if str(self.paypasslinktype.passid) == '36':
                pay_bankcode = "923"
            elif str(self.paypasslinktype.passid) == '37':
                pay_bankcode = "924"
            else:
                pay_bankcode = "903"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/tiger_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_TIGER(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        # 怪兽
        elif str(self.paypasslinktype.passid) == '38':

            request_data = {
                "sdorderno": str(self.order.ordercode),
                "total_fee": float(self.order.amount),
                "notifyurl": url_join('/callback_api/lastpass/guaishou_callback')
            }
            res = LastPass_GUAISHOU(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay5.html"}
        # DINGSHENG
        elif str(self.paypasslinktype.passid) == '41':
            pay_bankcode = "903"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/api/lastpass/dingsheng_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_DINGSHENG(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        # 创意支付
        elif str(self.paypasslinktype.passid) == '42':

            request_data = {
                "order_id": str(self.order.ordercode),
                "cash": "%.2f" % (float(self.order.amount)),
                "server_url": url_join('/callback_api/lastpass/czkj_callback')
            }
            res = LastPass_CZKJ(data=request_data).run()

            with open('/var/html/yunduan/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res)
            return {"path": url_join('/yunduan/{}.html').format(self.order.ordercode)}
        # 蜜蜂支付宝
        elif str(self.paypasslinktype.passid) == '43':

            request_data = {
                "out_order_no": str(self.order.ordercode),
                "amount": "%.2f" % (float(self.order.amount)),
                "callbackUrl": url_join('/api/lastpass/sbgm_callback')
            }
            res = LastPass_SBGM(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 星河
        elif str(self.paypasslinktype.passid) in ['44', '65']:

            if str(self.paypasslinktype.passid) == '44':
                terminal = "WEIXIN_PAY_WAP"
            else:
                terminal = "ALI_PAY_WAP"
            request_data = {
                "businessnumber": str(self.order.ordercode),
                "amount": int(float(self.order.amount) * float(100.0)),
                "ServerUrl": url_join('/callback_api/lastpass/xinghe_callback'),
                "terminal": terminal
            }
            res = LastPass_XINGHE(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 原来
        elif str(self.paypasslinktype.passid) == '45':

            request_data = {
                "orderId": str(self.order.ordercode),
                "price": str(self.order.amount)
            }
            res = LastPass_YUANLAI(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay6.html"}
        # 金沙
        elif str(self.paypasslinktype.passid) == '46':

            request_data = {
                "sdorderno": str(self.order.ordercode),
                "total_fee": float(self.order.amount),
                "notifyurl": url_join('/callback_api/lastpass/jingsha_callback')
            }
            res = LastPass_JINGSHA(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay5.html"}
        # 安杰个码
        elif str(self.paypasslinktype.passid) == '47':

            request_data = {
                "out_order_no": str(self.order.ordercode),
                "amount": "%.2f" % (float(self.order.amount)),
                "callbackUrl": url_join('/callback_api/lastpass/anjie_callback')
            }
            res = LastPass_ANJIE(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
            # 哒哒支付
        elif str(self.paypasslinktype.passid) == '48':

            pay_bankcode = "904"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/hahapay_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_hahapay(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom("生成订单失败,请稍后再试!")

            with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
        # 水晶
        elif str(self.paypasslinktype.passid) == '49':

            request_data = {
                "businessnumber": str(self.order.ordercode),
                "amount": int(float(self.order.amount) * float(100.0)),
                "ServerUrl": url_join('/callback_api/lastpass/shuijing_callback')
            }
            res = LastPass_SHUIJING(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # 快捷
        elif str(self.paypasslinktype.passid) == '51':

            request_data = {
                "order_no": str(self.order.ordercode),
                "total_fee": float(self.order.amount),
                "notify_url": url_join('/api/lastpass/kuaijie_callback')
            }
            res = LastPass_KUAIJIE(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay7.html"}
        # 招财宝
        elif str(self.paypasslinktype.passid) == '52':
            request_data = {
                "down_ordercode": str(self.order.ordercode),
                "amount": self.order.amount,
                "client_ip": self.order.client_ip,
                "notifyurl": url_join('/callback_api/lastpass/allwin_callback')
            }

            res = LastPass_ALLWIN(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])
            return {"path": res[1]}
        # 水晶新
        elif str(self.paypasslinktype.passid) == '53':
            request_data = {
                "tradeNo": str(self.order.ordercode),
                "orderPrice": float(self.order.amount),
                "notifyUrl": url_join('/callback_api/lastpass/shuijing_new_callback')
            }

            res = LastPass_SHUIJING_NEW(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode,
                    "htmlfile": "pay10.html"}
        # 霸王快捷
        elif str(self.paypasslinktype.passid) == '54':
            request_data = {
                "orderId": str(self.order.ordercode),
                "orderAmt": int(float(self.order.amount) * float(100.0)),
                "notifyUrl": url_join('/callback_api/lastpass/bawangkuaijie_callback'),
                "memberId": str(self.order.userid)
            }

            res = LastPass_BAWANGKUAIJIE(data=request_data).run()

            with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res)
            return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
        # 衍鑫
        elif str(self.paypasslinktype.passid) == '55':
            pay_bankcode = "930"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/yangxingzhifu_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_YANXINGZHIFU(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        # 京东
        elif str(self.paypasslinktype.passid) == '56':

            request_data = {
                "price": str(self.order.amount)
            }
            obj = LastPass_JINGDONG(data=request_data).run()

            self.order.jd_ordercode = obj.get('ordercode')
            self.order.jd_data = demjson.encode(obj)
            self.order.isjd = '0'
            self.order.save()

            return {"path": obj.get('url')}
        elif str(self.paypasslinktype.passid) == '57':

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "mchOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/jiahui_callback'),
                "productId": "8007"
            }
            res = LastPass_JIAHUI(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        elif str(self.paypasslinktype.passid) == '58':

            print(self.order.amount)
            request_data = {
                "amount": str(int(float(self.order.amount))),
                "orderNumber": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/zhongxing_callback')
            }
            res = LastPass_ZHONGXING(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        elif str(self.paypasslinktype.passid) == '59':

            print(self.order.amount)
            request_data = {
                "money": str(int(float(self.order.amount))),
                "innerorderid": str(self.order.ordercode),
                "notifyurl": url_join('/callback_api/lastpass/zhaoxing_callback')
            }
            res = LastPass_ZHAOXING(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
        elif str(self.paypasslinktype.passid) == '60':

            print(self.order.amount)
            request_data = {
                "money": float(self.order.amount),
                "customno": str(self.order.ordercode),
                "notifyurl": url_join('/callback_api/lastpass/tiancheng_callback')
            }
            res = LastPass_TIANCHENG(data=request_data).run()

            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode,
                    "htmlfile": "pay11.html"}
        elif str(self.paypasslinktype.passid) == '61':

            print(self.order.amount)
            request_data = {
                "amount": "%.2f" % float(self.order.amount),
                "out_trade_no": str(self.order.ordercode),
                "callback_url": url_join('/callback_api/lastpass/ipayzhifubao_callback')
            }
            res = LastPass_IPAYZHIFUBAO(data=request_data).run()
            print(res)
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        elif str(self.paypasslinktype.passid) == '62':

            pay_bankcode = "903"
            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/yslh_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_YSLH(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom("生成订单失败,请稍后再试!")

            with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
                f1.write(res[1])
            return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}

        elif str(self.paypasslinktype.passid) in ['63', '64']:

            if str(self.paypasslinktype.passid) == '63':
                id = "8007"
            else:
                id = "8003"

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "mchOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/jiahui_callback'),
                "productId": id,
                "clientIp": self.order.client_ip
            }
            res = LastPass_HUIHUANG(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}
        # elif str(self.paypasslinktype.passid) == '66':
        #
        #     pay_bankcode = "903"
        #     request_data = {
        #         "pay_orderid": str(self.order.ordercode),
        #         "pay_amount": self.order.amount,
        #         "pay_notifyurl": url_join('/callback_api/lastpass/juxingnew_callback'),
        #         "pay_bankcode": pay_bankcode
        #     }
        #     res = LastPass_JUXINGNEW(data=request_data).run()
        #     if not res[0]:
        #         raise PubErrorCustom("生成订单失败,请稍后再试!")
        #
        #     with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
        #         f1.write(res[1])
        #     return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
        elif str(self.paypasslinktype.passid) in ['66', '67']:

            if str(self.paypasslinktype.passid) == '66':
                pay_bankcode = "8007"
            else:
                pay_bankcode = "8003"

            request_data = {
                "amount": int(float(self.order.amount) * float(100.0)),
                "mchOrderNo": str(self.order.ordercode),
                "notifyUrl": url_join('/callback_api/lastpass/jiahui_callback'),
                "productId": pay_bankcode
            }

            res = LastPass_JUXINGNEW(data=request_data).run()
            if not res[0]:
                raise PubErrorCustom(res[1])

            return {"path": res[1]}

        elif str(self.paypasslinktype.passid) == '68':

            pay_bankcode = "930"

            request_data = {
                "pay_orderid": str(self.order.ordercode),
                "pay_amount": self.order.amount,
                "pay_notifyurl": url_join('/callback_api/lastpass/juxingnew_callback'),
                "pay_bankcode": pay_bankcode
            }
            res = LastPass_LONGSHI(data=request_data).run()
            # if not res[0]:
            #     raise PubErrorCustom("生成订单失败,请稍后再试!")

            # with open('/var/html/dada/{}.html'.format(self.order.ordercode), 'w') as f1:
            #     f1.write(res[1])
            # return {"path": url_join('/dada/{}.html').format(self.order.ordercode)}
            #
            return {"res": res, "userid": self.order.userid, "ordercode": self.order.ordercode, "htmlfile": "pay.html"}
        elif str(self.paypasslinktype.passid) == '69':

            data = {
                "amount": float(self.order.amount),
                "ordercode": self.order.ordercode,
                "url": url_join('/api_new/business/CardPays')
            }
            return {"res": data, "userid": self.order.userid, "ordercode": self.order.ordercode,
                    "htmlfile": "neichong.html"}

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

    def __init__(self, type=None, order=None):
        self.type = type
        self.order = order

        self.custom_select = [
            {
                "userid": 11,
                "type": 'QR005',
                "paytype": 'alipay'
            },
            {
                "userid": 4,
                "type": 'QR005',
                "paytype": 'wechat'
            }
        ]

    def run(self):

        for item in self.custom_select:
            if item['userid'] == self.order.userid and item['type'] == self.type:
                return {"path": url_join("/pay/#/{}/{}".format(item['paytype'], self.order.ordercode))}

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
        else:
            return {"path": url_join("/pay/#/wechat/{}".format(self.order.ordercode))}

