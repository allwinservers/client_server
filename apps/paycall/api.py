from apps.utils import GenericViewSetCustom
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from libs.utils.http_request import send_request
from utils.exceptions import PubErrorCustom,InnerErrorCustom
from apps.paycall.utils import PayCallWechat,PayCallFlm,get_qrcode_path,PayCallNxys,PayCallJyys,PayCallZjnx
from apps.paycall.models import FlmTranList
from apps.order.models import Order
from apps.pay.utils import QrCodeWechat,QrCodeFlm

from apps.public.models import WechatHelper,Qrcode
from include.data.redislockkey import sms_call_mobile_CALLBACK,zhejiangnongxin_call_mobile_CALLBACK

from apps.paycall.serializers import FlmTranListModelSerializer

from django.shortcuts import HttpResponse

class PayCallAPIView(GenericViewSetCustom):

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechat_callback(self, request, *args, **kwargs):

        msg = request.data_format.get('msg')
        msg = msg.split("digest")[1].split("digest")[0]
        amount = msg.split('￥')[1].split('汇')[0].replace('\n','')
        name = msg.split('店长')[1].split('(')[0]
        return PayCallWechat(name=name,amount=amount).run()

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def flm_callback(self, request, *args, **kwargs):
        for item in request.data_format.get("tranlist"):
            PayCallFlm(name = item['mobileno'],amount=item['transamt'] ,tranlist = item ).run()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def qrcode_order_get(self,request, *args, **kwargs):

        try:
            order=Order.objects.get(ordercode=request.data_format.get("ordercode"))
        except Order.DoesNotExist:
            raise PubErrorCustom("订单号不存在!")

        return get_qrcode_path(order)


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechat_login(self, request, *args, **kwargs):

        for item in WechatHelper.objects.filter(id=int(request.data_format.get('msg').split('_')[1])):
            Qrcode.objects.select_for_update().filter(wechathelper_id=item.id,status='5').update(status='0')
            item.login='0'
            item.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechat_logout(self, request, *args, **kwargs):
        for item in WechatHelper.objects.filter(id=int(request.data_format.get('msg').split('_')[1])):
            Qrcode.objects.select_for_update().filter(wechathelper_id=item.id,status='0').update(status='5')
            item.login = '1'
            item.save()
        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def flm_tranlist_get(self, request, *args, **kwargs):

        return {"data" : FlmTranListModelSerializer(FlmTranList.objects.filter(name=request.query_params_format.get("name")),many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True,lock=True)
    def wechat_call_mobile(self, request, *args, **kwargs):
        return PayCallNxys(name=request.data_format.get("name"),amount=request.data_format.get('amout')).run()

    @list_route(methods=['POST'])
    @Core_connector(transaction=True,lock={"resource":sms_call_mobile_CALLBACK})
    def sms_call_mobile(self, request, *args, **kwargs):
        return PayCallJyys(name=request.data_format.get("name"),amount=request.data_format.get('amout')).run()

    @list_route(methods=['POST'])
    @Core_connector(transaction=True, lock={"resource":zhejiangnongxin_call_mobile_CALLBACK})
    def zhejiangnongxin_call_mobile(self, request, *args, **kwargs):
        return PayCallJyys(name=request.data_format.get("name"), amount=request.data_format.get('amout')).run()

    #回调测试
    @list_route(methods=['POST'])
    @Core_connector()
    def wechat_test(self,request):

        return None

    #回调测试
    @list_route(methods=['POST'])
    def juli_call_back(self,request):
        print("request : {}".format(request.data))
        return HttpResponse("SUCCESS")


