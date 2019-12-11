from rest_framework import (viewsets)

from education.settings import ServerUrl,CreateOrderUrl
from apps.user.models import Users,BalList
from utils.exceptions import PubErrorCustom
from   django_redis  import   get_redis_connection
import json

class GenericViewSetCustom(viewsets.ViewSet):
    pass

def url_join(path=None):
    return "{}{}".format(ServerUrl,path) if path else ServerUrl

def createorder_url(path=None):
    return "{}{}".format(CreateOrderUrl,path) if path else CreateOrderUrl

def upd_bal(**kwargs):

    user = kwargs.get('user',None)

    userid = kwargs.get('userid',None)
    bal = kwargs.get('bal',None)
    cashout_bal = kwargs.get('cashout_bal',None)
    up_bal = kwargs.get('up_bal',None)

    if bal:
        bal=float(bal)
    if cashout_bal:
        cashout_bal=float(cashout_bal)
    if up_bal:
        up_bal = float(up_bal)

    memo = kwargs.get("memo","修改余额")

    if not user:
        try:
            user = Users.objects.select_for_update().get(userid=userid)
        except Users.DoesNotExist:
            raise PubErrorCustom("无对应用户信息({})".format(userid))

    if bal :
        BalList.objects.create(**{
            "userid" : user.userid,
            "amount" : bal,
            "bal" : user.bal,
            "confirm_bal" : float(user.bal) + float(bal),
            "memo" : memo,
            "ordercode":  kwargs.get("ordercode",0)
        })
        user.bal = float(user.bal) + float(bal)

    if cashout_bal:
        user.cashout_bal = float(user.cashout_bal) + float(cashout_bal)

    if up_bal:
        user.up_bal = float(user.up_bal) + float(up_bal)

    user.save()

    return user

class RedisHandler(object):
    def __init__(self,**kwargs):
        self.redis_client = get_redis_connection(kwargs.get("db"))
        self.key = kwargs.get("key")

    def redis_dict_insert(self,value):
        self.redis_client.set(self.key,json.dumps(value))

    def redis_dict_get(self):
        res = self.redis_client.get(self.key)
        return json.loads(res) if res else res

class RedisOrderCount(RedisHandler):

    def __init__(self,**kwargs):
        kwargs.setdefault('key',"ordercount")
        kwargs.setdefault('db','orders')
        super().__init__(**kwargs)

    def redis_dict_insert(self,userid,value):
        self.redis_client.hset(self.key,userid,json.dumps(value))

    def redis_dict_get(self,userid):
        res = self.redis_client.hget(self.key,userid)
        return json.loads(res) if res else res


class RedisQQbot(RedisHandler):

    def __init__(self,**kwargs):
        kwargs.setdefault('key',"allwin_qqbot_start")
        kwargs.setdefault('db','default')
        super().__init__(**kwargs)

        self.qqacc = kwargs.get("qqacc",None)

    def redis_dict_insert(self,value):
        self.redis_client.hset(self.key,self.qqacc,json.dumps(value))

    def redis_dict_get(self):
        res = self.redis_client.hget(self.key,self.qqacc)
        return json.loads(res) if res else res

    def redis_get_dict_keys(self):
        res = self.redis_client.hkeys(self.key)
        return res





