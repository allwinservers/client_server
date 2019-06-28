from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom
from libs.utils.apistool import SaveSerializer

from apps.pay.serializers import PayTypeModelSerializer,PayTypeModelSerializer1,PayPassModelSerializer,PayPassLinkTypeModelSerializer,RateSerializer,BankInfoModelSerializer

from apps.pay.models import PayType,PayPass,PayPassLinkType,BankInfo

from apps.user.serializers import BallistSerializer
from apps.user.models import BalList,UserLink

from auth.authentication import Authentication
from apps.order.models import Order
from apps.paycall.utils import PayCallBase


from apps.public.utils import get_sysparam
from include.data.choices_list import Choices_to_List

class PayAPIView(viewsets.ViewSet):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def callback_business(self,request, *args, **kwargs):

        try:
            order = Order.objects.select_for_update().get(ordercode=request.data_format.get("ordercode"),down_status='2')
        except Order.DoesNotExist:
            raise PubErrorCustom("状态不正确不能补发通知!")

        paycall = PayCallBase(amount=order.amount)
        paycall.order_obj = order
        paycall.callback_request_to_server()
        paycall.order_obj.save()
        return None

    @list_route(methods=['GET'])
    @Core_connector()
    def paytype_get(self,request, *args, **kwargs):

        return {"data":Choices_to_List('paytype')}


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paytype_add(self,request, *args, **kwargs):

        PayType.objects.create(**request.data_format)
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paytype_upd(self,request, *args, **kwargs):
        serializer=PayTypeModelSerializer1(PayType.objects.get(paytypeid=request.data_format.get("paytypeid")),data=request.data_format)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paytype_del(self,request, *args, **kwargs):
        PayType.objects.filter(paytypeid=request.data_format.get("paytypeid")).delete()
        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def paytype_query(self,request, *args, **kwargs):
        return {"data":PayTypeModelSerializer(PayType.objects.filter().order_by('createtime'),many=True).data}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def ballist_query(self,request, *args, **kwargs):

        query_format = str()
        query_params = list()

        if request.user.rolecode in ["1000","1001"]:
            if self.request.query_params_format.get("userid"):
                query_format = query_format + " and t1.userid=%s"
                query_params.append(self.request.query_params_format.get("userid"))

            if self.request.query_params_format.get("memo"):
                query_format = query_format + " and t1.memo=%s"
                query_params.append(self.request.query_params_format.get("memo"))

        elif request.user.rolecode == "2001" :
            query_format = query_format + " and t1.userid=%s"
            query_params.append(request.user.userid)
        elif request.user.rolecode == "3001":
            userlink = UserLink.objects.filter(userid_to=self.request.user.userid)
            if not userlink.exists():
                query_format = query_format + " and t1.userid=%s"
                query_params.append("0")
            else:
                query_format = query_format + " and t1.userid in %s"
                query_params.append([ item.userid for item in userlink ])
        else:
            raise PubErrorCustom("用户类型有误!")

        ballist = BalList.objects.raw("""
            SELECT t1.*,t2.name FROM ballist as t1 
            INNER JOIN user as t2 ON t1.userid=t2.userid
            WHERE 1=1 %s order by t1.createtime desc
        """%(query_format),query_params)

        headers = {
            'Total': len(ballist),
        }

        page=int(request.query_params_format.get('page'))
        page_size=int(request.query_params_format.get('page_size'))
        page_start = page_size * page - page_size
        page_end = page_size * page


        return {"data":BallistSerializer(ballist[page_start:page_end],many=True).data,"header":headers}

    # @list_route(methods=['GET'])
    # @Core_connector(pagination=True)
    # def paytype_name_query(self,request, *args, **kwargs):
    #     return {"data" : [ item.typename+item.name for item in PayType.objects.filter() ] }

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paypass_add(self,request, *args, **kwargs):

        PayPass.objects.create(**{
            "paycode" : request.data_format.get("paycode"),
            "name" : request.data_format.get("name"),
            "passcode": request.data_format.get("passcode"),
            "concat": request.data_format.get("concat"),
            "contype": request.data_format.get("contype")
        })
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paypass_del(self,request, *args, **kwargs):

        try:
            pay=PayPass.objects.get(paypassid = request.data_format.get("paypassid"))
            pay.status = 2
            pay.save()
        except PayPass.DoesNotExist:
            raise PubErrorCustom("该支付渠道不存在!")

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paypass_upd(self, request, *args, **kwargs):

        serializer=PayPassModelSerializer(PayPass.objects.get(paypassid=request.data_format.get("paypassid")),data=request.data_format)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def paypass_query(self, request, *args, **kwargs):

        QueryObj=PayPass.objects.filter(status__in=[0, 1])

        if request.query_params_format.get("id"):
            QueryObj=QueryObj.filter(paypassid=request.query_params_format.get("id"))
        return {"data" : PayPassModelSerializer(QueryObj,many=True).data}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def paypass_query1(self, request, *args, **kwargs):

        QueryObj=PayPass.objects.filter(status='0')

        if request.query_params_format.get("id"):
            QueryObj=QueryObj.filter(paypassid=request.query_params_format.get("id"))
        return {"data" : PayPassModelSerializer(QueryObj,many=True).data}



    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def paypasslinktype_add(self,request, *args, **kwargs):

        if "delete" in request.data_format and len(request.data_format.get('delete')):
            PayPassLinkType.objects.filter(to_id=request.data_format.get("delete").get("id"),type=request.data_format.get("delete").get("type")).delete()
        else:
            for (index, item) in enumerate(request.data_format.get("insert")):
                if index == 0:
                    PayPassLinkType.objects.filter(to_id=item['to_id'],type=item['type']).delete()
                SaveSerializer(serializers_class=PayPassLinkTypeModelSerializer, data=item)

        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def paypasslinktype_query(self, request, *args, **kwargs):

        query_format=str()
        query_params=list()
        if self.request.query_params_format.get("id"):
            query_format = query_format + " and t2.to_id=%s"
            query_params.append(self.request.query_params_format.get("id"))
        if self.request.query_params_format.get("type"):
            query_format = query_format + " and t2.type=%s"
            query_params.append(self.request.query_params_format.get("type"))

        paytype = PayType.objects.raw("""
            SELECT t1.*,t2.rate,t2.passid FROM paytype as t1 
            INNER JOIN paypasslinktype as t2 on t1.paytypeid = t2.paytypeid
            WHERE 1=1 %s order by t1.createtime
        """%(query_format),query_params)

        return {"data":PayTypeModelSerializer(paytype, many=True).data}



    #商户费率查询
    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def rate_query(self, request):

        sysparam = get_sysparam()

        data=[]

        for item in PayType.objects.filter():
            try:
                rate=PayPassLinkType.objects.get(paytypeid=item.paytypeid,to_id=self.request.user.userid,type='1').rate
                data.append({
                    "name" :  item.typename + item.name,
                    "rate" : "{}%".format(float(rate) * 100.0)
                })
            except PayPassLinkType.DoesNotExist:
                pass

        return {"data":data}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def bankinfo_query(self,request):
        return {"data":BankInfoModelSerializer(BankInfo.objects.filter(userid=request.user.userid).order_by('-createtime'),many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def bankinfo_upd(self,request):
        serializer=BankInfoModelSerializer(BankInfo.objects.get(id=request.data_format.get("id")),data=request.data_format)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def bankinfo_del(self,request):
        BankInfo.objects.get(id=request.data_format.get("id")).delete()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def bankinfo_add(self,request, *args, **kwargs):

        request.data_format['userid'] = request.user.userid
        BankInfo.objects.create(**request.data_format)
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def upd_userbal(self,request, *args, **kwargs):

        userid = request.data_format['userid']

        return None




    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def upd_paypass_batch(self,request, *args, **kwargs):

        paypass = request.data_format.get("paypass")
        userids = request.data_format.get("userids")
        if not len(paypass):
            raise PubErrorCustom("请选择支付方式对应的渠道!")
        if not len(userids):
            raise PubErrorCustom("请勾选用户记录!")

        error_list=""

        for userid in userids:
            for pay in paypass:
                try:
                    paypasslinktype = PayPassLinkType.objects.get(type='1',to_id=userid,paytypeid=pay['paytypeid'])
                    paypasslinktype.passid  = pay['passid']
                    if not paypasslinktype.rate:
                        error_list += "用户{}渠道{}支付方式{}未设置费率,切换未生效!\n".format(userid, pay['passid'], pay['paytypeid'])
                    else:
                        paypasslinktype.save()
                except PayPassLinkType.DoesNotExist:
                    error_list += "用户{}渠道{}支付方式{}未设置费率,切换未生效!\n".format(userid, pay['passid'], pay['paytypeid'])

        return {"data":{"error_list":error_list}}






