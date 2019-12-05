
import requests
import base64
import re
import rsa
import random
import urllib3
import json
import time
from urllib.parse import unquote,quote
from binascii import b2a_hex

urllib3.disable_warnings() # 取消警告

def get_timestamp():
    return int(time.time()*1000)

class WeiboBase(object):

    def __init__(self,**kwargs):
        self.amount = kwargs.get("amount")
        self.num = kwargs.get("num")
        self.sessionRes = kwargs.get("sessionRes",None)
        print("红包金额: {}分 ----- 红包数量: {} \n 会话:{}".format(self.amount,self.num,self.sessionRes))

        self.session = requests.session()
        self.session.verify = False

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
        }
        if kwargs.get("isSession",None):
            self.get_session()

    def datainitHandler(self):
        html = self.session.get('https://hongbao.weibo.com/h5/pay?groupid=1000303&ouid={}'.format(self.sessionRes['uid'])).text
        print(html)
        self.sessionRes['st'] = html.split("st:")[1].split(",")[0].replace("'","").strip()

    def get_session(self):
        try:
            if not self.sessionRes:
                self.sessionRes={}

            for key,value in self.sessionRes['cookie']['.weibo.com'].items():
                self.session.cookies.set(key, value)
        except Exception as e:
            raise Exception("无可用session!")

class WeiboHbPay(WeiboBase):

    def __init__(self,**kwargs):

        self.payScWeiboUrl = None
        self.payScWeiboParams = None
        self.wapPayUrl = None
        self.ordercode = None
        kwargs.setdefault("isSession",True)
        super(WeiboHbPay,self).__init__(**kwargs)
        self.session.headers['Referer'] = "https://hongbao.weibo.com/h5/pay?groupid=1000303&ouid={}".format(self.sessionRes['uid'])
        self.session.headers['Content-Type'] = "application/x-www-form-urlencoded"
        self.session.headers['Origin'] = "https://hongbao.weibo.com"
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)'

    def getPayUrl(self):
        url = "https://hongbao.weibo.com/aj_h5/createorder?st={}&current_id={}".format(self.sessionRes['st'],self.sessionRes['uid'])
        data = {
            "uid": self.sessionRes['uid'],
            "groupid": "1000303",
            "eid": 0,
            "amount": self.amount,
            "num": self.num,
            "share": 0,
            "_type": 1,
            "isavg": 0,
            "tab": 1,
            "genter": "f,m",
            "clear": 1
        }
        res = json.loads(self.session.post(url=url, data=data).content.decode("utf-8"))
        print("getPayUrl: {}".format(res))
        if res['ok'] != 1:
            #授权失败
            raise Exception(res['msg'])
        else:
            self.payScWeiboUrl = res['url']

    def getPayParams(self):

        params =  ""
        try:
            self.session.get(url=self.payScWeiboUrl)
        except Exception as a:
            # print(a)
            params = str(a).split("No connection adapters were found for")[1].\
                replace("sinaweibo://wbpay?", "").replace("'",'').split("pay_params=")[1]
            params = unquote(params, 'utf-8')
            print(params)
        self.payScWeiboParams = params

    def orderForWeibo(self):
        data={
            'uid' : self.sessionRes['uid'],
            'gsid' : self.sessionRes['gsid'],
            'request_str' : self.payScWeiboParams,
            'is4g' : 0,
            'apple_pay_allowed' :  0,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/prepare"
        try:
            res = self.session.post(url=url,data=data)
            print(res.text)
        except Exception as e:
            raise  Exception("createOrderForWeibo Error ： {}".format(str(e)))

    def orderForAliPay(self):

        data={
            'uid' : self.sessionRes['uid'],
            'gsid' : self.sessionRes['gsid'],
            "channel" : "ali_wap",
            "coupon_amount" : 0,
            'request_str' : self.payScWeiboParams,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/buildparams"
        self.session.headers['User-Agent'] = 'iOS__iPhone__iOS__12.4.1__828*1792__iPhone11,8__arm64e__0__9.11.2__2.0.0'

        try:
            res = json.loads(self.session.post(url=url, data=data).content.decode('utf-8'))
            if res['code'] != "100000":
                raise Exception("系统异常,请联系管理员!")
            # 成功 code=="100000"
            print(res)
            self.wapPayUrl = res['data']['wap_pay_url']
            self.ordercode = res['data']['pay_id']
        except Exception as e:
            print("orderForAliPay ! ： {}".format(str(e)))
            raise Exception("系统异常,请联系管理员!")

    def createSkipAliPayResponse(self):
        # print(self.headers)
        print(self.wapPayUrl)
        html = self.session.get(url=self.wapPayUrl).text

        return html,self.ordercode

    def run(self):
        self.getPayUrl()
        self.getPayParams()
        self.orderForWeibo()
        self.orderForAliPay()
        return self.createSkipAliPayResponse()


class WeiboLogin(WeiboBase):

    def __init__(self,**kwargs):

        super(WeiboLogin,self).__init__(**kwargs)
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)'

    def get_vercode(self,username):
        url = """
        https://api.weibo.cn/2/account/login_sendcode?wm=3333_2001&sensors_mark=0&uid=1014111034742&sensors_is_first_day=false&from=109B293010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&v_f=1&networktype=wifi&checktoken=1d4
a525091a7e60e4dced9f69b2e488b&did=6c622ce71e3a34c27cbd3b658eb8614e&lang=zh_CN&ua=iPhone11,8__weibo__9.11.2__iphone__os12.4.1&sflag=1&ft=0&aid=01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.&b=0&launchid=icon
        """

        data={
            "moduleID":"account",
            "orifid":"102803%24%240",
            "featurecode":"10000225",
            "uicode":"10000944",
            "luicode":"10000384",
            "phone":username,
            "lfid":"0",
            "oriuicode":"10000225_10000384"
        }

        try:
            res = json.loads(self.session.post(url=url,data=data).content.decode("utf-8"))
            if 'sendsms' in res and res['sendsms']:
                print("发送成功!")
            else:
                raise Exception(res['errmsg'])
        except Exception as e:
            print(str(e))
            raise Exception("发送验证码不成功!,请联系管理员!")

    def login(self,username,smscode):

        url = """
        https://api.weibo.cn/2/account/login?wm=3333_2001&sensors_mark=0&uid=1014111034742&sensors_is_first_day=false&from=109B293010&sensors_device_id=7F2E6523-1726-4FB9-87E5-038B80BC8AC7&c=iphone&v_p=78&skin=default&v_f=1&networktype=wifi&checktoken=1d4a525091a7e60e4dced9f69b2e488b&did=6c622ce71e3a34c27cbd3b658eb8614e&lang=zh_CN&ua=iPhone11,8__weibo__9.11.2__iphone__os12.4.1&sflag=1&ft=0&aid=01A7-rs9h5H2UJarozhxkn1a9juBCBeCxvbr3L_O6brkT10uU.&b=0&launchid=icon
        """
        """

        """
        data=dict(
            guestid="1014111034742",
            getcookie="1",
            uicode="10000062",
            imei="b3103498dc4cc5d7a32ad955b837aeba70766e74",
            device_name="iPhone",
            device_id="6c622ce71e3a34c27cbd3b658eb8614e83ab357b",
            moduleID="account",
            request_ab="1",
            preload_ab="1",
            luicode="10000944",
            phone=username,
            orifid="102803%24%240%24%240",
            featurecode="10000225",
            cfrom="",
            smscode=smscode,
            oriuicode="10000225_10000384_10000944",
            lfid=0
        )

        try:
            return self.filterloginres(json.loads(self.session.post(url=url, data=data).content.decode("utf-8")))
        except Exception as e:
            print(str(e))
            raise Exception("登录错误,请联系管理员!")

    def filterloginres(self,res):

        # res = json.loads(res)

        session=dict(
            gsid = res['gsid'],
            uid = res['uid'],
            cookie=res['cookie']['cookie']
        )
        for key,value in session['cookie'].items():
            session['cookie'][key]=dict()
            for item in value.split('\n'):
                itemtmp = item.split(';')[0]
                key1 = itemtmp.split('=')[0]
                value1 = itemtmp.split('=')[1]
                session['cookie'][key][key1] = value1

        return session,res


if __name__ == '__main__':

    # session={
    #     "st":"769696",
    #     "uid":"6424853549",
    #     "gsid":"_2A25w49PpDeRxGeBK6VYZ9S3JzzWIHXVRuWAhrDV6PUJbkdAKLVTRkWpNR848UCh0aEfqVWJJUXU-K8hCJACsw_Od",
    #     "cookie":{
    #         "SUB":"_2A25w49PqDeRhGeBK6VYZ9S3JzzWIHXVQfoeirDV8PUJbitANLVLFkWtNR848UBzF-WUfgZC7eFd_O_J3fBaGLzE9",
    #         "SUBP":"0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5NHD95QcShzX1h-0SKB4Ws4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSoBEShnfe0-X1Btt",
    #         "SCF":"AjOaGw1K_o2AsNr4Ql_tYHnWtwXMs_0EzBjlhVrMRn9__3dFIc0a2lum8eMmDo5p-w..",
    #         "SUHB":"0jBIffZWGBgbfV"
    #     }
    # }
    #
    # print(WeiboHbPay(amount=100,num=1,sessionRes=session).run())
    username="18580881001"
    s=WeiboLogin()
    # s.get_vercode(username)


    # s.login(username,"093579")
    session,res = s.filterloginres(res)
    a=WeiboHbPay(amount=100, num=1, sessionRes=session)
    a.datainitHandler()

    print(a.run())