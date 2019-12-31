
from requests import request as requestEx

from apps.utils import GenericViewSetCustom

from apps.order.models import Order,CashoutList,UpCashoutList
from apps.order.serializers import OrderModelSerializer,CashoutListModelSerializer,UpCashoutListModelSerializer
from libs.utils.log import logger

from auth.authentication import Authentication
from rest_framework.decorators import list_route

from core.decorator.response import Core_connector

from libs.utils.mytime import send_toTimestamp
from utils.exceptions import PubErrorCustom

from apps.user.models import UserLink
from apps.utils import RedisOrderCount

from apps.account import AccountStop,AccountStopCanle
from apps.utils import url_join
import json
from apps.order.utils import get_today_start_end_time

from apps.paycall.utils import PayCallFlm,PayCallWechat,PayCallLastPass,PayCallBase,PayCallNxys,PayCallJyys,PayCallZjnx,PayCallYzf

import time


class OrderAPIView(GenericViewSetCustom):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    @list_route(methods=['GET'])
    @Core_connector()
    def order_query(self, request, *args, **kwargs):

        QuerySet = Order.objects.all()

        if request.query_params_format.get("ordercode"):
            QuerySet = QuerySet.filter(ordercode=request.query_params_format.get("ordercode"))

        if request.query_params_format.get("no"):
            QuerySet = QuerySet.filter(down_ordercode=request.query_params_format.get("no"))

        if request.query_params_format.get("passid"):
            QuerySet = QuerySet.filter(paypass=request.query_params_format.get("passid"))

        if request.query_params_format.get("userid"):
            QuerySet = QuerySet.filter(userid=request.query_params_format.get("userid"))

        if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
            QuerySet = QuerySet.filter(
                createtime__lte = send_toTimestamp(request.query_params_format.get("enddate")),
                createtime__gte = send_toTimestamp(request.query_params_format.get("startdate")))

        if request.query_params_format.get("status"):
            QuerySet = QuerySet.filter(status=request.query_params_format.get("status"))

        if request.query_params_format.get("down_status"):
            QuerySet = QuerySet.filter(down_status=request.query_params_format.get("down_status"))

        if request.user.rolecode in ["1000","1001"]:
            pass
        elif request.user.rolecode == "2001" :
            QuerySet=QuerySet.filter(userid=self.request.user.userid)
        elif request.user.rolecode == "3001":
            userlink = UserLink.objects.filter(userid_to=self.request.user.userid)
            if not userlink.exists():
                QuerySet=Order.objects.filter(userid=0)
            else:
                QuerySet=QuerySet.filter(userid__in=[ item.userid for item in userlink ])
        else:
            raise PubErrorCustom("用户类型有误!")

        res = QuerySet.order_by('-createtime')
        headers = {
            'Total': res.count(),
        }

        page=int(request.query_params_format.get('page'))
        page_size=int(request.query_params_format.get('page_size'))
        page_start = page_size * page - page_size
        page_end = page_size * page
        data = OrderModelSerializer(res[page_start:page_end],many=True).data

        # if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
        #     start = request.query_params_format.get("startdate")
        #     end = request.query_params_format.get("enddate")
        # else:
        #     start, end = get_today_start_end_time()
        # today_amount = 0.0
        # tot_amount = 0.0
        # today_order_tot_count = 0
        # today_order_ok_count = 0
        # tot_order_tot_count = 0
        # tot_order_ok_count = 0
        #
        # for item in data:
        #
        #     tot_order_tot_count += 1
        #
        #     if item['status'] == '0':
        #         tot_amount += float(item['confirm_amount'])
        #         tot_order_ok_count += 1
        #         if start <= item['createtime'] <=end:
        #             today_amount += float(item['confirm_amount'])
        #             today_order_ok_count += 1
        #
        #     if start <= item['createtime'] <= end:
        #         today_order_tot_count += 1
        #

        # res = RedisOrderCount().redis_dict_get(request.user.userid)
        # print("res:",res)
        res=None
        r_data = {
            "data" : data,
            "today_amount" : round(res['today_amount'],2) if res and 'today_amount' in res else 0.0,
            "tot_amount" : round(res['tot_amount'],2) if res and 'tot_amount' in res else 0.0,
            "today_order_tot_count" : round(res['today_order_tot_count'],2) if res and 'today_order_tot_count' in res else 0,
            "today_order_ok_count" : round(res['today_order_ok_count'],2) if res and 'today_order_ok_count' in res else 0 ,
            "tot_order_tot_count" : round(res['tot_order_tot_count'],2) if res and 'tot_order_tot_count' in res else 0 ,
            "tot_order_ok_count" : round(res['tot_order_ok_count'],2) if res and 'tot_order_ok_count' in res else 0
        }
        return {"data": r_data,"header":headers}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def stop_handler(self, request, *args, **kwargs):
        try:
            order = Order.objects.select_for_update().get(ordercode=self.request.data_format.get("ordercode"))
            if not str(order.status)=='0':
                raise PubErrorCustom("只可冻结成功的订单!")
            if str(order.isstop) == '0':
                raise PubErrorCustom("该订单已被冻结")
        except Order.DoesNotExist:
            raise PubErrorCustom("此订单号不存在!")

        AccountStop(userid=order.userid,amount=order.amount).run()
        order.isstop = '0'
        order.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def stop_canle_handler(self, request, *args, **kwargs):
        try:
            order = Order.objects.select_for_update().get(ordercode=self.request.data_format.get("ordercode"))

        except Order.DoesNotExist:
            raise PubErrorCustom("此订单号不存在!")

        AccountStopCanle(userid=order.userid,amount=order.amount).run()
        order.isstop = '1'
        order.save()
        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def order_status_upd(self, request, *args, **kwargs):

        if self.request.data_format.get("orders") and len(self.request.data_format.get("orders"))>1:
            raise PubErrorCustom("手工上分只允许单笔操作!")

        if not self.request.data_format.get("orders") :
            raise PubErrorCustom("请选择订单！")

        request_data = {
            "orderid": self.request.data_format.get("orders")[0]
        }

        result = requestEx('POST',
                         url=url_join('/callback_api/lastpass/shougonghandler_callback'),
                         data=request_data,
                         json=request_data, verify=False)

        res = json.loads(result.content.decode('utf-8'))

        print(res)

        if str(res['rescode']) != '10000':
            raise PubErrorCustom(res['msg'])

        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def order_status_upd1(self, request, *args, **kwargs):

        if not len(self.request.data_format.get("orders")):
            raise PubErrorCustom("订单号不能为空!")

        for ordercode in self.request.data_format.get("orders"):
            PayCallBase().work_handler_updbal(ordercode=ordercode)

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def cashoutlist_query(self, request, *args, **kwargs):

        QuerySet = CashoutList.objects.all()

        if self.request.user.rolecode in ["1000","1001","1005"]:
            pass
        elif self.request.user.rolecode == '2001':
            QuerySet = QuerySet.filter(userid=self.request.user.userid)
        elif request.user.rolecode == "3001":
            QuerySet = QuerySet.filter(userid=self.request.user.userid)
        else:
            raise PubErrorCustom("用户类型有误!")

        return {"data": CashoutListModelSerializer(QuerySet.filter(status="0",paypassid=0).order_by('-createtime'),many=True).data}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def cashoutlist_df_query(self, request, *args, **kwargs):

        QuerySet = CashoutList.objects.filter(paypassid__gt=0)


        if self.request.query_params_format.get("bank_card_number") :
            QuerySet = QuerySet.filter(bank_card_number__contains=self.request.query_params_format.get("bank_card_number"))

        if self.request.query_params_format.get("bank_name") :
            QuerySet = QuerySet.filter(bank_name__contains=self.request.query_params_format.get("bank_name"))

        if self.request.query_params_format.get("open_name") :
            QuerySet = QuerySet.filter(open_name__contains=self.request.query_params_format.get("open_name"))

        if self.request.query_params_format.get("amount") :
            QuerySet = QuerySet.filter(amount=self.request.query_params_format.get("amount"))

        if self.request.query_params_format.get("userid") :
            QuerySet = QuerySet.filter(userid=self.request.query_params_format.get("userid"))

        if self.request.query_params_format.get("memo") :
            QuerySet = QuerySet.filter(memo__contains=self.request.query_params_format.get("memo"))

        if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
            QuerySet = QuerySet.filter(
                createtime__lte = send_toTimestamp(request.query_params_format.get("enddate")),
                createtime__gte = send_toTimestamp(request.query_params_format.get("startdate")))

        if self.request.query_params_format.get("ordercode"):
            userid = int(self.request.query_params_format.get("ordercode")[2:10])
            ordercode = self.request.query_params_format.get("ordercode")[10:]

            QuerySet = QuerySet.filter(downordercode=ordercode,userid=userid)

        if self.request.query_params_format.get("no") :
            QuerySet = QuerySet.filter(downordercode=self.request.query_params_format.get("no"))

        if self.request.query_params_format.get("df_status") :
            QuerySet = QuerySet.filter(df_status=self.request.query_params_format.get("df_status"))

        if self.request.user.rolecode in ["1000", "1001", "1005"]:
            pass
        elif self.request.user.rolecode == '2001':
            QuerySet = QuerySet.filter(userid=self.request.user.userid)
        else:
            raise PubErrorCustom("用户类型有误!")


        if self.request.query_params_format.get("sort") :
            if self.request.query_params_format.get("sort") == '0':
                QuerySet = QuerySet.filter().order_by('-createtime')
            elif self.request.query_params_format.get("sort") == '1':
                QuerySet = QuerySet.filter().order_by('createtime')
        else:
            QuerySet = QuerySet.filter().order_by('-createtime')

        return {"data": CashoutListModelSerializer(QuerySet,many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def cashoutlist_status_query(self, request, *args, **kwargs):

        isFlag = "True" if  CashoutList.objects.filter(status='0').count() else "False"

        return {"data": isFlag}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def cashoutlist1_query(self, request, *args, **kwargs):

        QuerySet = CashoutList.objects.all()

        if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
            QuerySet = QuerySet.filter(
                createtime__lte = send_toTimestamp(request.query_params_format.get("enddate")),
                createtime__gte = send_toTimestamp(request.query_params_format.get("startdate")))

        if self.request.query_params_format.get("ordercode"):
            userid = int(self.request.query_params_format.get("ordercode")[2:10])
            ordercode = self.request.query_params_format.get("ordercode")[10:]

            QuerySet = QuerySet.filter(downordercode=ordercode,userid=userid)

        if self.request.query_params_format.get("no") :
            QuerySet = QuerySet.filter(downordercode=self.request.query_params_format.get("no"))

        if self.request.user.rolecode in ["1000","1001","1005"]:
            pass
        elif self.request.user.rolecode == '2001':
            QuerySet = QuerySet.filter(userid=self.request.user.userid)
        elif request.user.rolecode == "3001":
            QuerySet = QuerySet.filter(userid=self.request.user.userid)
        else:
            raise PubErrorCustom("用户类型有误!")

        return {"data": CashoutListModelSerializer(QuerySet.filter(status__in=["1","2"],paypassid=0).order_by('-updtime'),many=True).data}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def up_cashoutlist1_query(self, request, *args, **kwargs):

        QuerySet = UpCashoutList.objects.all()

        if self.request.user.rolecode in ["1000","1001","1005"]:
            pass
        elif self.request.user.rolecode == '4001':
            QuerySet = QuerySet.filter(userid_to=self.request.user.userid)
        else:
            raise PubErrorCustom("用户类型有误!")

        return {"data": UpCashoutListModelSerializer(QuerySet.filter(status__in=["1","2"]).order_by('-updtime'),many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def up_cashoutlist_query(self, request, *args, **kwargs):

        QuerySet = UpCashoutList.objects.all()

        if self.request.user.rolecode in ["1000", "1001","1005"]:
            pass
        elif self.request.user.rolecode == '4001':
            QuerySet = QuerySet.filter(userid_to=self.request.user.userid)
        else:
            raise PubErrorCustom("用户类型有误!")

        return {"data": UpCashoutListModelSerializer(QuerySet.filter(status="0").order_by('-createtime'), many=True).data}



