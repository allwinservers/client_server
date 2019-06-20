

import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

from django.db import transaction
from apps.order.models import Order
from apps.user.models import Users
from apps.datacount.models import OrderCount
from libs.utils.mytime import UtilTime

def order_valid_task():
    """
    订单过期处理,每天凌晨3点处理昨天的过期情况
    :return:
    """
    with transaction.atomic():
        ut = UtilTime()
        # last_day_time = ut.string_to_timestamp(ut.arrow_to_string(ut.today.replace(days=-1), format_v="YYYY-MM-DD") + ' 00:00:01')
        today_time = ut.string_to_timestamp(ut.arrow_to_string(ut.today,format_v="YYYY-MM-DD")+' 00:00:01')
        Order.objects.filter(createtime__lte=today_time,status="1").update(status="3",down_status='3')


def order_count():
    """
    订单统计
    :return:
    """
    ut = UtilTime()

    lastday = ut.today.replace(days=-1)
    startdate = ut.string_to_timestamp(ut.arrow_to_string(lastday,format_v="YYYY-MM-DD")+' 00:00:00')
    enddate = ut.string_to_timestamp(ut.arrow_to_string(lastday,format_v="YYYY-MM-DD")+' 23:59:59')

    with transaction.atomic():
        print("订单统计，日期：{}...".format(ut.arrow_to_string(lastday,format_v="YYYY-MM-DD")))
        for user in Users.objects.filter(rolecode='2001',status='0',createtime__lt=enddate):
            orders = Order.objects.filter(userid=user.userid,createtime__gte=startdate,createtime__lte=enddate)

            ordercount_insert=dict()
            ordercount_insert["tot_order_count"] = orders.count()
            ordercount_insert["today_success_order_count"] = 0
            ordercount_insert["today_amount"] = 0.0
            ordercount_insert["userid"] = user.userid

            for order in orders:
                if order.status=='0':
                    ordercount_insert["today_success_order_count"] += 1
                    ordercount_insert["today_amount"] += float(order.amount)

            ordercount_insert["today_rate"] = ordercount_insert["today_success_order_count"] * 1.0 / ordercount_insert["tot_order_count"] \
                if ordercount_insert["tot_order_count"] else 0.0
            ordercount_insert["today"] = ut.arrow_to_string(lastday,format_v="YYYY-MM-DD")
            OrderCount.objects.create(**ordercount_insert)







