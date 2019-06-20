from apps.utils import GenericViewSetCustom

from apps.order.models import Order
from apps.user.models import UserLink
from apps.order.serializers import OrderModelSerializer
from libs.utils.log import logger

from apps.datacount.models import OrderCount
import datetime

from auth.authentication import Authentication
from rest_framework.decorators import list_route

from core.decorator.response import Core_connector

from libs.utils.mytime import send_toTimestamp,UtilTime
from utils.exceptions import PubErrorCustom

from apps.datacount.serializers import OrderCountModelSerializer

from apps.datacount.models import OrderCount
from apps.pay.models import PayPass

class DataCountAPIView(GenericViewSetCustom):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def ordercount(self, request, *args, **kwargs):

        data = {
            "amount_tot" : 0.0,
            "amount" : 0.0 ,
            "order_tot" : 0,
            "order" : 0 ,
            "rate_tot" : 0.0,
            "rate" : 0.0
        }

        start_datetime  = send_toTimestamp(datetime.datetime.now().strftime('%Y-%m-%d')+' 00:00:01')
        end_datetime = send_toTimestamp(datetime.datetime.now().strftime('%Y-%m-%d') + ' 23:59:59')

        #流水统计,订单比数统计,成功率
        QuerySet = Order.objects.all()

        if self.request.user.rolecode in ["1000","1001"]:
            pass
        elif self.request.user.rolecode == '2001':
            QuerySet = QuerySet.filter(userid=self.request.user.userid)
        elif request.user.rolecode == "3001":
            userlink = UserLink.objects.filter(userid_to=self.request.user.userid)
            if not userlink.exists():
                QuerySet=Order.objects.filter(userid=0)
            else:
                QuerySet=QuerySet.filter(userid__in=[item.userid for item in userlink])
        else:
            raise PubErrorCustom("用户类型有误!")

        is_all = 0.0
        is_ok = 0.0

        is_all_today = 0.0
        is_ok_today = 0.0


        for item in QuerySet:

            is_all += 1

            if start_datetime <= item.createtime <= end_datetime:
                is_all_today += 1

            if item.status == '0' :
                is_ok+=1
                data['amount_tot'] += float(item.confirm_amount)
                data['order_tot'] += 1

                if start_datetime <= item.createtime  <= end_datetime:
                    data['amount'] += float(item.confirm_amount)
                    data['order'] +=1
                    is_ok_today += 1

        data['rate_tot'] = round(is_ok / is_all  * 100.0,3) if is_all else 0
        data['rate'] = round(is_ok_today / is_all_today * 100.0,3) if is_all_today else 0


        data1=[
            {
                "title": '当天商户流水',
                "subtitle": '实时',
                "count": '¥{}'.format(round(data["amount"],2)),
                "allcount": '¥{}'.format(round(data["amount_tot"],2)),
                "text": '总流水',
                "color": 'rgb(27, 201, 142)',
                "key": '商'
            },
            {
                "title": '当天订单数',
                "subtitle": '实时',
                "count": '{}'.format(data["order"]),
                "allcount": '{}'.format(data["order_tot"]),
                "text": '总订单比数',
                "color": 'rgb(230, 71, 88)',
                "key": '订'
            },
            {
                "title": '当天订单成功率',
                "subtitle": '实时',
                "count": '{}%'.format(data["rate"]),
                "allcount": '{}%'.format(data["rate_tot"]),
                "text": '总成功率',
                "color": 'rgb(178, 159, 255)',
                "key": '成'
            },
        ]

        ut=UtilTime()

        item_count = 7
        data2=[]
        data3=[]

        day = ut.today.replace(days=-7)
        while item_count:
            day=ut.replace(arrow_v=day , days=1)

            day_string = ut.arrow_to_string(arrow_s=day,format_v="YYYY-MM-DD")[0:10]

            amount = 0.0
            for item in QuerySet.filter(createtime__lte=ut.string_to_arrow(day_string+' 23:59:59').timestamp ,
                                createtime__gte=ut.string_to_arrow(day_string+' 00:00:01').timestamp,status='0'):
                amount += float(item.confirm_amount)

            data2.append(day_string.replace('-','')[4:])
            data3.append(amount)
            item_count-=1


        data4={
            'value': data3,
            'key' : data2,
            'top' : ['订单金额']
        }

        return {"data":{"data1":data1,"data4":data4}}


    @list_route(methods=['GET'])
    @Core_connector()
    def finance_order_count(self, request, *args, **kwargs):

        query = OrderCount.objects.filter()

        if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
            query = query.filter(
                today__lte = request.query_params_format.get("enddate")[:10],
                today__gte = request.query_params_format.get("startdate")[:10])

        if self.request.user.rolecode in ["1000", "1001"]:
            if request.query_params_format.get("userid"):
                query = query.filter(userid=request.query_params_format.get("userid"))
        elif self.request.user.rolecode == '2001':
            query = query.filter(userid=self.request.user.userid)
        elif request.user.rolecode == "3001":
            userlink = UserLink.objects.filter(userid_to=self.request.user.userid)
            if not userlink.exists():
                query = query.filter(userid=0)
            else:
                query = query.filter(userid__in=[item.userid for item in userlink])
            if request.query_params_format.get("userid"):
                query = query.filter(userid=request.query_params_format.get("userid"))
        else:
            raise PubErrorCustom("用户类型有误!")

        page=int(request.query_params_format.get('page'))
        page_size=int(request.query_params_format.get('page_size'))
        page_start = page_size * page - page_size
        page_end = page_size * page

        res = query.filter().order_by('-today')
        headers = {
            'Total': res.count(),
        }
        return {"data":OrderCountModelSerializer(res[page_start:page_end], many=True).data,"header":headers}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def pass_count(self,request):

        query_format = str()
        query_params = list()

        ut = UtilTime()
        if request.query_params_format.get("today"):
            today = request.query_params_format.get("today")
            startdate = ut.string_to_timestamp(today+' 00:00:01')
            enddate =  ut.string_to_timestamp(today+' 23:59:59')
        else:
            today = ut.arrow_to_string(format_v="YYYY-MM-DD")
            startdate = ut.string_to_timestamp(today+' 00:00:01')
            enddate = ut.string_to_timestamp(today+' 23:59:59')

        query_format = query_format + " and t1.createtime>=%s and t1.createtime<=%s"
        query_params.append(startdate)
        query_params.append(enddate)

        if request.query_params_format.get("paypassid"):
            query_format = query_format + " and t2.paypassid =%s"
            query_params.append(request.query_params_format.get("paypassid"))

        orders = Order.objects.raw("""
                SELECT t1.* FROM `order` as t1
                INNER JOIN `paypass` as t2 ON t1.paypass = t2.paypassid and t2.status='0'
                WHERE 1=1 %s
        """% (query_format), query_params)


        pass_order_dict={}
        for order in orders :
            if order.paypass not in pass_order_dict:
                pass_order_dict[order.paypass]={
                    "id": order.paypass,
                    "name" : order.paypassname,
                    "amount" : 0.0,
                    "order_count":0,
                    "order_success_count":0,
                    "rate" : 0.0,
                    "today" : today[:10]
                }

            pass_order_dict[order.paypass]['order_count'] += 1
            if order.status == '0':
                pass_order_dict[order.paypass]['amount'] += float(order.amount)
                pass_order_dict[order.paypass]['order_success_count'] += 1

        data = []
        for key in pass_order_dict:
            pass_order_dict[key]['rate'] = "{}%".format(round(pass_order_dict[key]['order_success_count'] * 100.0 / pass_order_dict[key]['order_count'] \
                                                                  if pass_order_dict[key]['order_count']  else 0.0 ,2))
            data.append(pass_order_dict[key])

        return {"data": data}
