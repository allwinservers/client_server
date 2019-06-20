#!/usr/bin/python3
# -*- coding:utf8 -*-
import web
import commFunction
render=web.template.render('templates')
urls = ('/index', 'index',
        )
#pay.input   pay.ctx.env
class hello(object):
    def GET(self):
        return render.hello2() #hello2.html
class index(object):
    def GET(self):
        pay_amount='0.01'
        pay_applydate=commFun.obtaindate()
        pay_bankcode='902'#微信扫码支付 银行编码见附件
        pay_callbackurl="https://pay.xxx.com/demo/page.php" #同步地址
        pay_memberid='10007'
        pay_notifyurl="https://pay.xxx.com/demo/server.php" #异步地址
        pay_orderid=commFun.order()
        keyValue='t4ig5acnpx4fet4zapshjacjd9o4bhbi' #商户APIKEY
        SignTemp = "pay_amount=" + pay_amount + "&pay_applydate=" + pay_applydate + "&pay_bankcode=" + pay_bankcode + "&pay_callbackurl=" + pay_callbackurl + "&pay_memberid=" + pay_memberid + "&pay_notifyurl=" + pay_notifyurl + "&pay_orderid=" + pay_orderid + "&key=" + keyValue + "";
        print(SignTemp)
        pay_md5sign=md5Util.Md5str(SignTemp)
        pay_productname="VIP基础服务"
        return render.pay(pay_amount,pay_applydate,
                          pay_bankcode,pay_callbackurl,pay_memberid,pay_notifyurl,pay_orderid,pay_md5sign,pay_productname)
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()