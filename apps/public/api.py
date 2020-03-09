import random
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom
from requests import request as requestAlias
from apps.user.models import Login,Users,Role,UserLink,BalList
import json
from apps.order.models import Order

from apps.user.serializers import UsersSerializer1,WaitbnSerializer,AgentSerializer,BusinessSerializer,UsersSerializer,BankInfoSerializer
from apps.pay.serializers import PayPassModelSerializer
from auth.authentication import Authentication
from apps.public.utils import check_df_ip
from apps.pay.models import PayPass

from libs.utils.mytime import timestamp_toTime,UtilTime
from apps.public.utils import get_fee_rule_forSys
from libs.utils.string_extension import md5pass

from public.serializers import ManageSerializer,QrcodeModelSerializer,WechatHelperModelSerializer
import hashlib
from apps.order.models import CashoutList,UpCashoutList
from apps.paycall.models import PayCallList

from include.data.redislockkey import PAY_SELF_UPD_BAL,PAY_ADMIN_UPD_BAL,LOAD_QRCODE

from apps.public.models import Qrcode,WechatHelper

from apps.utils import url_join
from include.data.choices_list import Choices_to_Dict
from libs.utils.google_auth import create_google_token

from apps.lastpass.utils import LastPass_BAWANGKUAIJIE,LastPass_KUAIJIE,LastPass_GCPAYS

from apps.account import AccountCashout,AccountCashoutCanle,AccountCashoutConfirm,AccountCashoutConfirmFee
import time
import os
import subprocess
from education.settings import BASE_DIR

from requests import request as request_http

from include.data.choices_list import Choices_to_Dict

from libs.utils.google_auth import check_google_token,create_google_token_url
from apps.utils import RedisQQbot

from apps.cache.utils import RedisCaCheHandler
from apps.public.models import WhiteList
from apps.public.serializers import WhiteListModelSerializer
from apps.lastpass.utils import LastPass_GCPAYS
from apps.business.utils import CreateOrder
from libs.utils.db import RedisIdGeneratorForOrder

class PublicAPIView(viewsets.ViewSet):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    #对账
    @list_route(methods=['POST'])
    @Core_connector()
    def accCheckok(self,request,*args, **kwargs):
        obj = Users.objects.raw("""
            SELECT * FROM user  as t8
            INNER JOIN paypasslinktype as t1 
            INNER JOIN paytype as t2 on t1.paytypeid = t2.paytypeid
            INNER JOIN paypass as t3 on t1.passid = t3.paypassid
            WHERE t1.to_id=t8.userid and t1.type='1' and t3.paypassid = '69'
        """)

        userids = [ item.userid for item in obj ]

        #余额
        totbal = 0.0
        for item in obj:
            totbal += float(item.bal)

        #流水
        totamount = 0.0
        orderObj = Order.objects.filter(userid__in=userids,status='0')
        for item in orderObj:
            totamount += float(item.amount)

        #上游余额
        res = LastPass_GCPAYS(data={}).df_bal_query()
        lasttotbal = float(res.get("customerAmt"))

        #手续费
        feetot = CashoutList.objects.filter(paypassid='69',textstatus='支付成功').count() * 2

        return {
            "data":{
                "totbal" : totbal,
                "totamount" : totamount,
                "lasttotbal" : lasttotbal,
                "feetot" : feetot
            }
        }

    #充值
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def neichong(self,request,*args, **kwargs):

        bankCardNo = self.request.data_format['bank']['bank_card_number']
        custName = self.request.data_format['bank']['open_name']

        data={
            "businessid" : self.request.user.userid,
            "paytypeid" : "23",
            "down_ordercode" : RedisIdGeneratorForOrder().run(),
            "amount" : request.data_format.get("amount"),
            "client_ip" : "localhost",
            "notifyurl" : "http://allwin6666.com/api/paycall/wechat_test",
            "ismobile" : "1",
            "bankno":bankCardNo,
            "open_name":custName
        }
        obj = CreateOrder(user=request.user, request_param=data, lock="0")

        obj.check_request_param()
        obj.create_order_handler()

        return LastPass_GCPAYS(data={
            "bankCardNo": bankCardNo,
            "custName" : custName,
            "ordercode" : obj.order.ordercode,
            "amount" : obj.order.amount
        }).run()


    #刷新所有支付方式缓存数据
    @list_route(methods=['POST'])
    @Core_connector()
    def refeshWhiteList(self,request, *args, **kwargs):

        RedisCaCheHandler(
            method="insertAll",
            serialiers="WhiteListModelSerializerToRedis",
            table="whitelist",
            filter_value=WhiteList.objects.filter(),
            must_key="userid",
        ).run()

        return None

    #添加用户
    @list_route(methods=['POST'])
    @Core_connector(transaction=True, serializer_class=WhiteListModelSerializer, model_class=WhiteList)
    def addWhiteList(self,request,*args, **kwargs):

        serializer = kwargs.pop('serializer')
        isinstance = serializer.save()

        RedisCaCheHandler(
            method="save",
            serialiers="WhiteListModelSerializerToRedis",
            table="whitelist",
            filter_value=isinstance,
            must_key="userid",
        ).run()

        return None

    #修改用户
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def updWhiteList(self,request,*args, **kwargs):


        serializer=WhiteListModelSerializer(WhiteList.objects.get(userid=request.data_format.get("userid")),data=request.data_format)
        serializer.is_valid(raise_exception=True)
        userObj = serializer.save()

        RedisCaCheHandler(
            method="save",
            serialiers="WhiteListModelSerializerToRedis",
            table="whitelist",
            filter_value=userObj,
            must_key="userid",
        ).run()

        return None

    #删除用户
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def delWhiteList(self,request,*args, **kwargs):

        userid = request.data_format.get('userid')


        WhiteList.objects.filter(userid=userid).delete()


        RedisCaCheHandler(
            method="delete",
            table="whitelist",
            must_key_value=userid).run()


        return None

    #查询用户
    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def getWhiteList(self,request,*args, **kwargs):

        data =RedisCaCheHandler(
            method="filter",
            serialiers="WhiteListModelSerializerToRedis",
            table="whitelist",
            filter_value=request.query_params_format
        ).run()

        return {"data":data}

    @list_route(methods=['POST'])
    @Core_connector()
    def check_google_token(self, request):

        check_google_token(request.user.google_token,request.data_format.get('vercode'))
        return None

    @list_route(methods=['POST'])
    @Core_connector()
    def qqbot_send_msg(self, request):

        if not request.data_format.get("msg"):
            raise PubErrorCustom("请输入群发的消息!")

        if not request.data_format.get("self_id"):
            raise PubErrorCustom("请选择QQ号!")

        if not request.data_format.get("data"):
            raise PubErrorCustom("请勾选群号!")

        redis_handler = RedisQQbot(qqacc=request.data_format.get("self_id"))
        res = redis_handler.redis_dict_get()

        if res and 'data' in res:
            for item in request.data_format.get("data"):
                for item1 in res['data']:
                    if str(item.get("id")) == str(item1.get("id")):
                        if item1.get('message_type') == 'group':
                            data = {"group_id": item.get("id"), "message": request.data_format.get("msg")}
                            request_http('POST', url='http://47.244.129.198:5700/send_group_msg', data=data,
                                                  json=data, verify=False, headers={
                                    "Authorization": "Bearer allwin_niubi"
                                })
                        elif item1.get('message_type') == 'discuss':
                            data = {"discuss_id": item.get("id"), "message": request.data_format.get("msg")}
                            request_http('POST', url='http://47.244.129.198:5700/send_discuss_msg', data=data,
                                                  json=data, verify=False, headers={
                                    "Authorization": "Bearer allwin_niubi"
                                })

        return None


    @list_route(methods=['GET'])
    @Core_connector()
    def get_qq_accs(self, request):
        res = RedisQQbot().redis_get_dict_keys()
        if res:
            res  = [ item.decode()  for item in RedisQQbot().redis_get_dict_keys() ]
        return {"data" : res} if res else {"data":[]}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def get_qq_list(self, request):

        redis_handler = RedisQQbot(qqacc=request.query_params_format.get("self_id"))
        res = redis_handler.redis_dict_get()

        if request.query_params_format.get("name"):
            if res and 'data' in res:
                for item in res['data']:
                    if str(request.query_params_format.get("name")) in str(item.get('name')):
                        return {"data":[item]}
        else:
            return {"data":res['data'] if res and 'data' in res else []}

        return {"data":[]}

    @list_route(methods=['POST'])
    @Core_connector()
    def upd_qq(self, request):
        redis_handler = RedisQQbot(qqacc=request.data_format.get("self_id"))
        res = redis_handler.redis_dict_get()
        if res and 'data' in res:
            for item in res['data']:
                if str(item.get('id')) == str(request.data_format.get('data').get('id')):
                    item['name'] = request.data_format.get('data').get('name')

        redis_handler.redis_dict_insert(res)
        return None

    @list_route(methods=['POST'])
    @Core_connector()
    def del_qq(self, request):
        redis_handler = RedisQQbot(qqacc=request.data_format.get("self_id"))
        res = redis_handler.redis_dict_get()
        data=[]
        if res and 'data' in res:
            for item in res['data']:
                if str(item.get('id')) != str(request.data_format.get('id')):
                    data.append(item)
        res['data'] = data
        redis_handler.redis_dict_insert(res)
        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def get_qrtype(self, request):

        data=[]
        for key,value in Choices_to_Dict('qrcode_type').items():
            data.append({"name":key,"value":value})

        return {"data" : data }


    @list_route(methods=['POST'])
    @Core_connector(transaction=True, serializer_class=WechatHelperModelSerializer, model_class=WechatHelper)
    def wechathelper_add(self, request, *args, **kwargs):
        serializer = kwargs.pop('serializer')
        res=serializer.save()

        if not res.name or not len(res.name):
            raise PubErrorCustom("店员名称不能为空!")

        helper_class = Choices_to_Dict('helper_link_helperClass')[res.type](md5name="%s_%08d"%(res.md5name,res.id))
        helper_class.helper_add()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechathelper_del(self,request, *args, **kwargs):
        try:
            wechat= WechatHelper.objects.get(id=request.data_format.get('id'))
        except WechatHelper.DoesNotExist:
            raise PubErrorCustom("该店员不存在")
        if wechat.login == '0':
            raise PubErrorCustom("登录状态不允许删除!")

        helper_class = Choices_to_Dict('helper_link_helperClass')[wechat.type](md5name="%s_%08d"%(wechat.md5name,wechat.id))
        helper_class.helper_del()

        wechat.delete()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechathelper_login(self, request, *args, **kwargs):
        try:
            wechat = WechatHelper.objects.select_for_update().get(id=request.data_format.get('id'))
        except WechatHelper.DoesNotExist:
            raise PubErrorCustom("该店员不存在")

        md5name = "%s_%08d" % (wechat.md5name, wechat.id)

        wechat.qrcode = "/nginx_upload/wechatlogin/{}.png".format(md5name)
        wechat.save()

        if wechat.login == '0':
            raise PubErrorCustom("登录状态不允许再登录!")

        helper_class = Choices_to_Dict('helper_link_helperClass')[wechat.type](md5name=md5name)
        helper_class.helper_login()

        return {"data":{
            "path": wechat.qrcode
        }}


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechathelper_stop(self, request, *args, **kwargs):
        try:
            wechat = WechatHelper.objects.get(id=request.data_format.get('id'))
        except WechatHelper.DoesNotExist:
            raise PubErrorCustom("该店员不存在")


        Qrcode.objects.select_for_update().filter(wechathelper_id=wechat.id,status='0').update(status='5')

        if wechat.login == '1':
            raise PubErrorCustom("未登录状态不允许再退出!")

        helper_class = Choices_to_Dict('helper_link_helperClass')[wechat.type](md5name="%s_%08d" % (wechat.md5name, wechat.id))
        helper_class.helper_stop()

        wechat.login = "1"
        wechat.save()


        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def wechathelper_upd(self,request, *args, **kwargs):
        serializer=WechatHelperModelSerializer(WechatHelper.objects.get(id=request.data_format.get("id")),data=request.data_format)
        serializer=WechatHelperModelSerializer(WechatHelper.objects.get(id=request.data_format.get("id")),data=request.data_format)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def wechathelper_query(self,request, *args, **kwargs):
        QureSet=WechatHelper.objects.all()

        if self.request.query_params_format.get("name"):
            QureSet=QureSet.filter(name=self.request.query_params_format.get("name"))

        if self.request.query_params_format.get("id"):
            QureSet=QureSet.filter(id=self.request.query_params_format.get("id"))

        return {"data":WechatHelperModelSerializer(QureSet.filter().order_by('-createtime'),many=True).data}

    @list_route(methods=['GET'])
    @Core_connector()
    def getroletype(self,request, *args, **kwargs):
        role=Role.objects.filter()
        data=[]
        if role.exists():
            for item in role:
                if item.rolecode != '1000':
                    data.append({"rolecode":item.rolecode,"name":item.name})
        return {"data" : data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def loginquery(self,request, *args, **kwargs):
        login=Login.objects.filter().order_by('-createtime')
        data=[]
        if login.exists():
            for item in login:
                try:
                    user=Users.objects.get(userid=item.userid)
                except Users.DoesNotExist:
                    continue

                data.append({
                    "ip" : item.ip,
                    "chrom" : item.user_agent.split(' ')[0],
                    "windows" : item.user_agent.split('(')[1].split(';')[0],
                    "userid" : item.userid,
                    "loginname" : user.loginname,
                    "name" : user.name,
                    "createtime" : timestamp_toTime(item.createtime),
                    "rolename" : Role.objects.get(rolecode=user.rolecode).name
                })

        return { "data" : data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def manageadd_query(self,request, *args, **kwargs):
        user = Users.objects.raw("""
            SELECT t1.*,t2.name as rolename FROM user as t1
              INNER JOIN `role` t2 on t1.rolecode = t2.rolecode
              WHERE t2.type = 0 and t1.status=0 and t1.rolecode!='1000' 
        """)

        return  {"data":  ManageSerializer(user,many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def manageadd_del(self,request, *args, **kwargs):
        userid = request.data_format.get('userid')

        try:
            user=Users.objects.get(userid=userid)
            user.status = 1
            user.save()
        except Users.DoesNotExist:
            raise PubErrorCustom("此账号不存在!")

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True, serializer_class=UsersSerializer1, model_class=Users)
    def manageadd_add(self,request, *args, **kwargs):

        serializer = kwargs.pop('serializer')
        isinstance = serializer.save()
        isinstance.createman = request.user.userid
        isinstance.createman_name = request.user.name
        isinstance.status = 0
        token = create_google_token()
        while Users.objects.filter(google_token=token).exists():
            token = create_google_token()
        isinstance.google_token = token
        isinstance.save()

        return {"msg": "添加成功！"}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def manageadd_upd(self,request, *args, **kwargs):

        serializer=UsersSerializer1(Users.objects.get(userid=request.data_format.get("userid")),data=request.data_format)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return None


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def waitbn_query(self, request, *args, **kwargs):

        user = Users.objects.raw("""
            SELECT t1.*,t2.name FROM user as t1 
              INNER  JOIN  `role` as t2 on t1.rolecode=t2.rolecode
              WHERE t1.status = '0' and t2.type=1 
        """)

        return {"data" : WaitbnSerializer(user,many=True).data}


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def waitbn_query(self, request, *args, **kwargs):

        user = Users.objects.raw("""
            SELECT t1.*,t2.name FROM user as t1 
              INNER  JOIN  `role` as t2 on t1.rolecode=t2.rolecode
              WHERE t1.status = '0' and t2.type=1 
        """)

        return {"data" : WaitbnSerializer(user,many=True).data}


    @list_route(methods=['POST'])
    @Core_connector(transaction=True, serializer_class=UsersSerializer1, model_class=Users)
    def user_add(self,request, *args, **kwargs):

        serializer = kwargs.pop('serializer')
        isinstance = serializer.save()
        isinstance.createman = request.user.userid
        isinstance.createman_name = request.user.name
        token = create_google_token()
        while Users.objects.filter(google_token=token).exists():
            token = create_google_token()
        isinstance.google_token = token
        isinstance.save()

        if request.data_format.get("agents"):
            agents = [ item['value'] for item in request.data_format.get("agents")]
            if len(agents) != len(set(agents)):
                raise PubErrorCustom("代理人不能是同一人")
            for index,item in enumerate(agents):
                userid_to = item.split("(")[0]
                try:
                    Users.objects.get(userid=userid_to,status="0")
                except Users.DoesNotExist:
                    PubErrorCustom("%s不存在!"%(item))
                UserLink.objects.create(**{
                    "userid" : isinstance.userid,
                    "userid_to" : userid_to,
                    "level" : index+1
                })
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def user_upd(self,request, *args, **kwargs):

        serializer=UsersSerializer1(Users.objects.get(userid=request.data_format.get("userid")),data=request.data_format)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def user_del(self,request, *args, **kwargs):

        try:
            user=Users.objects.get(userid=request.data_format.get("userid"))
            user.status=2
            user.save()
        except Users.DoesNotExist:
            raise PubErrorCustom("该用户不存在!")
        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def user_verify(self,request, *args, **kwargs):

        userids=[]
        if isinstance(request.data_format.get("userid"),list) :
            userids = request.data_format.get("userid")
        else:
            userids.append(request.data_format.get("userid"))

        for item in Users.objects.filter(userid__in=userids):
            item.status = 0
            item.save()

        return None

    #批量切换通道
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def user_updpass(self,request, *args, **kwargs):

        for item in request.data_format.get("pass"):
            for user_item in Users.objects.filter(userid=item['userid']):
                user_item.paypassid = item['paypassid']
                user_item.save()

        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def agent_query(self,request, *args, **kwargs):
        query_format=str()
        query_params=list()
        if self.request.query_params_format.get("name"):
            query_format = query_format + " and t1.name=%s"
            query_params.append(self.request.query_params_format.get("name"))
        if self.request.query_params_format.get("loginname"):
            query_format = query_format + " and t1.loginname=%s"
            query_params.append(self.request.query_params_format.get("loginname"))
        if self.request.query_params_format.get("status"):
            query_format = query_format + " and t1.status=%s"
            query_params.append(self.request.query_params_format.get("status"))
        if self.request.query_params_format.get("type"):
            query_format = query_format + " and t2.type=%s"
            query_params.append(self.request.query_params_format.get("type"))

        user=Users.objects.raw("""
            SELECT t1.* FROM user as t1
              INNER JOIN `role` as t2 on t1.rolecode=t2.rolecode
              WHERE 1=1 %s
        """%(query_format),query_params)

        return {"data":AgentSerializer(user,many=True).data}

    @list_route(methods=['GET'])
    @Core_connector()
    def agent_query1(self, request, *args, **kwargs):
        query_format = str()
        query_params = list()
        if self.request.query_params_format.get("status"):
            query_format = query_format + " and t1.status=%s"
            query_params.append(self.request.query_params_format.get("status"))
        if self.request.query_params_format.get("type"):
            query_format = query_format + " and t2.type=%s"
            query_params.append(self.request.query_params_format.get("type"))

        user = Users.objects.raw("""
                SELECT t1.* FROM user as t1
                  INNER JOIN `role` as t2 on t1.rolecode=t2.rolecode
                  WHERE 1=1 %s
            """ % (query_format), query_params)

        return { "data" : [ {
                                "value": str(item.userid)+'('+item.name+')' ,
                                "name": item.name
                            } for item in user ] }



    #查出相关商户对应的代理
    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def business_query(self,request, *args, **kwargs):
        query_format=str()
        query_params=list()

        if self.request.query_params_format.get("userid"):
            query_format = query_format + " and ("
            count = 0
            for item in str(self.request.query_params_format.get("userid")).split(","):
                count +=1
                if count == 1:
                    query_format = query_format + " t1.userid=%s"
                else:
                    query_format = query_format + " or t1.userid=%s"
                query_params.append(str(item))
            query_format = query_format + " ) "

        if self.request.query_params_format.get("status"):
            query_format = query_format + " and t1.status=%s"
            query_params.append(str(self.request.query_params_format.get("status")))

        if request.user.rolecode == "3001":
            userlink = UserLink.objects.filter(userid_to=self.request.user.userid)
            if not userlink.exists():
                query_format += "and t1.userid='%s'"
                query_params.append("0")
            else:
                query_format += "and t1.userid in %s"
                query_params.append([item.userid for item in userlink])

        user=Users.objects.raw("""
            SELECT t1.* FROM user as t1
              INNER JOIN `role` as t2 on t1.rolecode=t2.rolecode and t2.type='1'
              WHERE 1=1 %s
        """%(query_format),query_params)

        # for item in user:
        #     print(item.userid)

        return {"data":BusinessSerializer(user,many=True).data}


    #删除代理关系
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def agent_delete(self,request, *args, **kwargs):
        UserLink.objects.get(id=self.request.data_format.get('id')).delete()

        return None


    #用户查询
    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def user_query(self,request, *args, **kwargs):

        return {"data":UsersSerializer(self.request.user,many=False).data}

    #代理编辑

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def agent_modi(self,request, *args, **kwargs):

        UserLink.objects.filter(userid=request.data_format.get("userid")).delete()

        if request.data_format.get("agents"):

            agents = [item['value'] for item in request.data_format.get("agents")]
            if len(agents) != len(set(agents)):
                raise PubErrorCustom("代理人不能是同一人")
            for index, item in enumerate(agents):
                userid_to = item.split("(")[0]
                try:
                    Users.objects.get(userid=userid_to, status="0")
                except Users.DoesNotExist:
                    PubErrorCustom("%s不存在!" % (item))
                UserLink.objects.create(**{
                    "userid": request.data_format.get("userid"),
                    "userid_to": userid_to,
                    "level": index + 1
                })
        return None



    #银行信息查询
    @list_route(methods=['GET'])
    @Core_connector()
    def get_bankinfo(self,request, *args, **kwargs):

        return {"data" : BankInfoSerializer(self.request.user,many=False).data}

    #余额查询
    @list_route(methods=['GET'])
    @Core_connector()
    def get_bal(self,request, *args, **kwargs):

        if self.request.user.fee_rule <= 0.0:
            fee = get_fee_rule_forSys()
        else:
            fee = float(self.request.user.fee_rule)

        return {"data" : {"bal":round(self.request.user.bal,2),"cashout_bal":round(self.request.user.cashout_bal,2),"fee_rule":round(fee,2)}}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def google_token_url_get(self,request, *args, **kwargs):

        try:
            user = Users.objects.get(userid=request.data_format.get("userid"))
        except Users.DoesNotExist:
            raise PubErrorCustom("用户不存在!")

        return {"data":create_google_token_url(user.google_token,user.name)}


    #提现申请
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def cashout(self,request, *args, **kwargs):

        # if not check_google_token(request.user.google_token, request.data_format.get('vercode')):
        #     raise PubErrorCustom("谷歌验证码不正确！")

        if not self.request.data_format.get("bank"):
            raise PubErrorCustom("请选择银行卡信息!")

        if not self.request.data_format.get("pay_passwd"):
            raise PubErrorCustom("请输入支付密码!")
        if self.request.data_format.get("pay_passwd") != self.request.user.pay_passwd:
            raise PubErrorCustom("支付密码错误!")

        if self.request.user.fee_rule <= 0.0:
            fee = get_fee_rule_forSys()
        else:
            fee = float(self.request.user.fee_rule)

        if float(self.request.user.bal) - abs(float(self.request.user.cashout_bal)) - fee < self.request.data_format.get("amount"):
            raise  PubErrorCustom("可提余额不足!")

        if self.request.data_format.get("amount")<=0 :
            raise PubErrorCustom("请输入正确的提现金额!")

        # user = upd_bal(userid=self.request.user.userid,cashout_bal = self.request.data_format.get("amount"))

        cashlist = CashoutList.objects.create(**{
            "userid" : self.request.user.userid ,
            "name" : self.request.user.name,
            "amount" : self.request.data_format.get("amount") ,
            "bank_name" : self.request.data_format.get("bank")['bank_name'],
            "open_name" : self.request.data_format.get("bank")['open_name'],
            "open_bank" : self.request.data_format.get("bank")['open_bank'],
            "bank_card_number" : self.request.data_format.get("bank")['bank_card_number'],
            "status" : "0"
        })

        cashlist.downordercode = "%08d" % cashlist.id
        cashlist.save()

        user = AccountCashout(userid=self.request.user.userid,amount=self.request.data_format.get("amount"),ordercode=cashlist.downordercode).run()

        return {"data": {"bal": round(user.bal, 2), "cashout_bal": round(user.cashout_bal, 2)}}

    #手工代付提现
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def cashout_daifusb(self,request, *args, **kwargs):

        if not check_google_token(request.user.google_token, request.data_format.get('vercode')):
            raise PubErrorCustom("谷歌验证码不正确！")

        if not self.request.data_format.get("bank"):
            raise PubErrorCustom("请选择银行卡信息!")

        if not self.request.data_format.get("pay_passwd"):
            raise PubErrorCustom("请输入支付密码!")
        if self.request.data_format.get("pay_passwd") != self.request.user.pay_passwd:
            raise PubErrorCustom("支付密码错误!")

        if self.request.user.fee_rule <= 0.0:
            fee = get_fee_rule_forSys()
        else:
            fee = float(self.request.user.fee_rule)
        if float(self.request.user.bal) - abs(float(self.request.user.cashout_bal)) - fee < self.request.data_format.get("amount"):
            raise  PubErrorCustom("可提余额不足!")

        if self.request.data_format.get("amount")<=0 :
            raise PubErrorCustom("请输入正确的提现金额!")

        data={}
        data.setdefault('down_ordercode', RedisIdGeneratorForOrder().run())
        data.setdefault('amount', float(self.request.data_format.get("amount")))
        data.setdefault('businessid', str(request.user.userid))
        data.setdefault("nonceStr", str(UtilTime().timestamp))
        data.setdefault('accountNo', self.request.data_format.get("bank")['bank_card_number'])
        data.setdefault('bankName', self.request.data_format.get("bank")['bank_name'].encode('utf-8').hex())
        data.setdefault('accountName', self.request.data_format.get("bank")['open_name'].encode('utf-8').hex())
        data.setdefault('memo',self.request.data_format.get("memo"))

        md5params = "{}{}{}{}{}{}{}{}{}{}".format(
            request.user.google_token,
            str(data.get("down_ordercode")),
            str(data.get("businessid")),
            request.user.google_token,
            str(data.get("nonceStr")),
            str(data.get("amount")),
            str(data.get("accountNo")),
            str(data.get("bankName")),
            str(data.get("accountName")),
            request.user.google_token)
        md5params = md5params.encode("utf-8")
        data.setdefault("sign", hashlib.md5(md5params).hexdigest())

        print(data)

        result = requestAlias('POST', url="http://allwin6666.com/api_new/business/df",
                         json=data, verify=False)

        # result = requestAlias('POST', url="http://localhost:9001/api_new/business/df",
        #                  json=data, verify=False)

        res = json.loads(result.content.decode('utf-8'))

        print(res)

        if res['rescode'] != '10000':
            raise PubErrorCustom( res['msg'])

        return None
    #冲正
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def correct(self,request, *args, **kwargs):

        try:
            user = Users.objects.select_for_update().get(userid=request.data_format.get('userid'))
        except Users.DoesNotExist:
            raise PubErrorCustom("该用户不存在!")

        if not request.data_format.get("amount") :
            raise PubErrorCustom("请输入金额!")

        if not request.data_format.get("memo1") :
            raise PubErrorCustom("说明情况不能为空!")

        BalList.objects.create(**{
            "userid": user.userid,
            "amount": request.data_format.get("amount"),
            "bal": user.bal,
            "confirm_bal": float(user.bal) + request.data_format.get("amount"),
            "memo": "冲正",
            "memo1" : request.data_format.get("memo1"),
            "ordercode": 0
        })

        user.bal = float(user.bal) + request.data_format.get("amount")
        user.save()

        return None

    #代付列表
    @list_route(methods=['GET'])
    @Core_connector()
    def daifuPassList(self,request, *args, **kwargs):

        check_df_ip(request.user.userid, request.META.get("HTTP_X_REAL_IP"))

        QueryObj=PayPass.objects.filter(status__in=[0, 1],isdayfu='0')

        if request.query_params_format.get("id"):
            QueryObj=QueryObj.filter(paypassid=request.query_params_format.get("id"))
        return {"data" : PayPassModelSerializer(QueryObj,many=True).data}


    #代付订单查询
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def daifuOrderQuery(self,request, *args, **kwargs):


        check_df_ip(request.user.userid, request.META.get("HTTP_X_REAL_IP"))
        if not request.data_format.get("dfordercode"):
            raise PubErrorCustom("订单号不能为空!")

        try:
            obj = CashoutList.objects.get(id= request.data_format.get("id"))
        except CashoutList.DoesNotExist:
            raise PubErrorCustom("此订单不存在!")

        print(request.data_format)

        if str(request.data_format.get('paypassid')) == '54':
            res = LastPass_BAWANGKUAIJIE(data={
                "orderId" : request.data_format.get("dfordercode")
            }).df_query()
            obj.textstatus = res
            obj.save()
            return {"data":res}

        elif str(request.data_format.get('paypassid')) == '51':
            res=LastPass_KUAIJIE(data={
                "tradeCustorder" : request.data_format.get("dfordercode")
            }).df_order_query()
            obj.textstatus = res
            obj.save()
            return {"data":res}
        elif str(request.data_format.get('paypassid')) == '69':
            res=LastPass_GCPAYS().df_order_query(data={
                "orderNo" : request.data_format.get("dfordercode")
            })
            # obj.textstatus = res
            # obj.save()
            return {"data":res}

    #代付提现
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def daifuBalTixian(self,request, *args, **kwargs):

        check_df_ip(request.user.userid, request.META.get("HTTP_X_REAL_IP"))


        if str(request.data_format.get('paypassid')) == '54':
            if not self.request.data_format.get("bank"):
                raise PubErrorCustom("请选择银行卡信息!")

            if not self.request.data_format.get("pay_passwd"):
                raise PubErrorCustom("请输入支付密码!")
            if self.request.data_format.get("pay_passwd") != self.request.user.pay_passwd:
                raise PubErrorCustom("支付密码错误!")

            if self.request.data_format.get("amount") <= 0:
                raise PubErrorCustom("请输入正确的提现金额!")

            cashlist = CashoutList.objects.create(**{
                "userid": self.request.user.userid,
                "name": self.request.user.name,
                "amount": self.request.data_format.get("amount"),
                "bank_name": self.request.data_format.get("bank")['bank_name'],
                "open_name": self.request.data_format.get("bank")['open_name'],
                "open_bank": self.request.data_format.get("bank")['open_bank'],
                "bank_card_number": self.request.data_format.get("bank")['bank_card_number'],
                "status": "0"
            })

            cashlist.downordercode = "%08d"%cashlist.id

            res = LastPass_BAWANGKUAIJIE(data={
                "orderId": "DF%08d%s" % (cashlist.userid, cashlist.downordercode),
                "txnAmt" : str(int(float(cashlist.amount)*100.0)),
                "accountNo" : cashlist.bank_card_number,
                "bankName" :cashlist.bank_name,
                "accountName" : cashlist.open_name
            }).df_bal_handler()

            cashlist.status='1'
            cashlist.paypassid = '54'
            cashlist.tranid = res['REP_BODY']['tranId']
            cashlist.save()

            return None
        elif str(request.data_format.get('paypassid')) == '51':
            if not self.request.data_format.get("bank"):
                raise PubErrorCustom("请选择银行卡信息!")

            if not self.request.data_format.get("pay_passwd"):
                raise PubErrorCustom("请输入支付密码!")
            if self.request.data_format.get("pay_passwd") != self.request.user.pay_passwd:
                raise PubErrorCustom("支付密码错误!")

            if self.request.data_format.get("amount") <= 0:
                raise PubErrorCustom("请输入正确的提现金额!")

            cashlist = CashoutList.objects.create(**{
                "userid": self.request.user.userid,
                "name": self.request.user.name,
                "amount": self.request.data_format.get("amount"),
                "bank_name": self.request.data_format.get("bank")['bank_name'],
                "open_name": self.request.data_format.get("bank")['open_name'],
                "open_bank": self.request.data_format.get("bank")['open_bank'],
                "bank_card_number": self.request.data_format.get("bank")['bank_card_number'],
                "status": "0"
            })
            cashlist.downordercode = "%08d" % cashlist.id

            res = LastPass_KUAIJIE().df_api(data={
                "orderId": "DF%08d%s" % (cashlist.userid, cashlist.downordercode),
                "txnAmt": "%.2lf"%float(cashlist.amount),
                "accountNo": cashlist.bank_card_number,
                "bankName": cashlist.bank_name,
                "accountName": cashlist.open_name
            })

            cashlist.status = '1'
            cashlist.paypassid = '51'
            cashlist.tranid = cashlist.downordercode
            cashlist.save()

            return None
        elif str(request.data_format.get('paypassid')) == '69':
            if not self.request.data_format.get("bank"):
                raise PubErrorCustom("请选择银行卡信息!")

            if not self.request.data_format.get("pay_passwd"):
                raise PubErrorCustom("请输入支付密码!")
            if self.request.data_format.get("pay_passwd") != self.request.user.pay_passwd:
                raise PubErrorCustom("支付密码错误!")

            if self.request.data_format.get("amount") <= 0:
                raise PubErrorCustom("请输入正确的提现金额!")

            cashlist = CashoutList.objects.create(**{
                "userid": self.request.user.userid,
                "name": self.request.user.name,
                "amount": self.request.data_format.get("amount"),
                "bank_name": self.request.data_format.get("bank")['bank_name'],
                "open_name": self.request.data_format.get("bank")['open_name'],
                "open_bank": self.request.data_format.get("bank")['open_bank'],
                "bank_card_number": self.request.data_format.get("bank")['bank_card_number'],
                "status": "0"
            })
            cashlist.downordercode = "%08d" % cashlist.id

            res = LastPass_GCPAYS().df_api(data={
                "orderNo": "DF%08d%s" % (cashlist.userid, cashlist.downordercode),
                "bankNo": cashlist.bank_card_number,
                "timestap" : str(cashlist.createtime),
                "realName": cashlist.open_name,
                "branchBankName" : cashlist.open_bank,
                "money": int(float(cashlist.amount)*100.0),
                "bankName": cashlist.bank_name
            })

            cashlist.status = '1'
            cashlist.paypassid = '69'
            cashlist.tranid = cashlist.downordercode
            cashlist.save()

            return None
        else:
            raise PubErrorCustom("代付渠道有误!")


    #代付余额查询
    @list_route(methods=['GET'])
    @Core_connector()
    def daifuBalQuery(self,request, *args, **kwargs):

        check_df_ip(request.user.userid,request.META.get("HTTP_X_REAL_IP"))



        if str(request.query_params_format.get("paypassid")) == '54':

            res = LastPass_BAWANGKUAIJIE(data={}).df_bal_query()

            return {"data":{
                "freezeOrderAmt" : round(float(res['REP_BODY']['freezeOrderAmt']) / 100.0,2) if res['REP_BODY']['freezeOrderAmt'] else 0.0,
                "acT0": round(float(res['REP_BODY']['acT0']) / 100.0, 2) if res['REP_BODY'][
                    'acT0'] else 0.0,
                "freezeAmt": round(float(res['REP_BODY']['freezeAmt']) / 100.0, 2) if res['REP_BODY'][
                    'freezeAmt'] else 0.0,
                "acBal": round(float(res['REP_BODY']['acBal']) / 100.0, 2) if res['REP_BODY'][
                    'acBal'] else 0.0,
            } }
        elif str(request.query_params_format.get("paypassid")) == '51':
            res = LastPass_KUAIJIE(data={}).df_bal_query()
            return {"data":{
                "freezeOrderAmt" : 0.0,
                "acT0": float(res)/100.0,
                "freezeAmt": 0.0,
                "acBal": float(res)/100.0,
            } }
        elif str(request.query_params_format.get("paypassid")) == '69':
            res = LastPass_GCPAYS(data={}).df_bal_query()
            return {"data":{
                "freezeOrderAmt" : 0.0,
                "acT0": float(res.get("customerAmt")),
                "freezeAmt": float(res.get("freezeAmt")),
                "acBal": float(res.get("customerAmt"))
            } }
        else:
            return None

    #提现通过
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def cashout_confirm(self,request, *args, **kwargs):

        try:
            cashlist = CashoutList.objects.select_for_update().get(id=self.request.data_format.get('id'),status='0')
        except CashoutList.DoesNotExist:
            raise PubErrorCustom("此纪录不存在!")

        cashlist.status = '1'
        cashlist.updtime = time.mktime(timezone.now().timetuple())
        cashlist.save()

        # upd_bal(userid=self.request.data_format.get("userid"),cashout_bal = cashlist.amount*-1,bal=cashlist.amount*-1,memo="提现")

        try:
            user = Users.objects.select_for_update().get(userid=self.request.data_format.get("userid"))
        except Users.DoesNotExist:
            raise PubErrorCustom("无对应用户信息({})".format(self.request.data_format.get("userid")))
        AccountCashoutConfirmFee(user=user).run()
        AccountCashoutConfirm(user=user, amount=cashlist.amount).run()

        return None

    # 提现拒绝
    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def cashout_cancel(self, request, *args, **kwargs):

        try:
            cashlist = CashoutList.objects.select_for_update().get(id=self.request.data_format.get('id'))
        except CashoutList.DoesNotExist:
            raise PubErrorCustom("此纪录不存在!")

        cashlist.status = '2'
        cashlist.updtime = time.mktime(timezone.now().timetuple())
        cashlist.save()

        # upd_bal(userid=self.request.data_format.get("userid"),cashout_bal = cashlist.amount*-1)
        AccountCashoutCanle(userid=self.request.data_format.get("userid"), amount=cashlist.amount).run()

        return None

        # 提现申请

    # @list_route(methods=['POST'])
    # @Core_connector(transaction=True)
    # def up_cashout(self, request, *args, **kwargs):
    #     if not self.request.data_format.get("bank"):
    #         raise PubErrorCustom("请选择银行卡信息!")
    #
    #     if not self.request.data_format.get("userid"):
    #         raise PubErrorCustom("码商ID不能为空!")
    #
    #     if not self.request.data_format.get("pay_passwd"):
    #         raise PubErrorCustom("请输入支付密码!")
    #     if self.request.data_format.get("pay_passwd") != self.request.user.pay_passwd:
    #         raise PubErrorCustom("支付密码错误!")
    #
    #     try:
    #         user = Users.objects.get(userid=self.request.data_format.get("userid"))
    #     except Users.DoesNotExist:
    #         raise PubErrorCustom("码商ID不存在!")
    #
    #     if float(user.up_bal) - float(user.bal) - float(user.cashout_bal) < self.request.data_format.get("amount"):
    #         raise PubErrorCustom("可提余额不足!")
    #
    #     if self.request.data_format.get("amount") <= 0:
    #         raise PubErrorCustom("请输入正确的提现金额!")
    #
    #     user = upd_bal(userid=user.userid, cashout_bal=self.request.data_format.get("amount"))
    #
    #     UpCashoutList.objects.create(**{
    #         "userid": self.request.user.userid,
    #         "name": self.request.user.name,
    #         "userid_to" : user.userid,
    #         "name_to" : user.name,
    #         "amount": self.request.data_format.get("amount"),
    #         "bank_name": self.request.data_format.get("bank")['bank_name'],
    #         "open_name": self.request.data_format.get("bank")['open_name'],
    #         "open_bank": self.request.data_format.get("bank")['open_bank'],
    #         "bank_card_number": self.request.data_format.get("bank")['bank_card_number'],
    #         "status": "0"
    #     })
    #     return {"data":{
    #         "bal":user.bal,
    #         "up_bal" : user.up_bal,
    #         "cashout_bal" : user.cashout_bal
    #     }}
    #
    # #提现通过
    # @list_route(methods=['POST'])
    # @Core_connector(transaction=True)
    # def up_cashout_confirm(self,request, *args, **kwargs):
    #
    #     try:
    #         cashlist = UpCashoutList.objects.select_for_update().get(id=self.request.data_format.get('id'),status=0)
    #     except CashoutList.DoesNotExist:
    #         raise PubErrorCustom("此纪录不存在!")
    #
    #     cashlist.status = '1'
    #     cashlist.updtime = time.mktime(timezone.now().timetuple())
    #     cashlist.save()
    #
    #     upd_bal(userid=cashlist.userid_to,cashout_bal = cashlist.amount*-1,up_bal=cashlist.amount*-1,memo="提现")
    #
    #     return None
    #
    # # 提现拒绝
    # @list_route(methods=['POST'])
    # @Core_connector(transaction=True)
    # def up_cashout_cancel(self, request, *args, **kwargs):
    #
    #     try:
    #         cashlist = UpCashoutList.objects.get(id=self.request.data_format.get('id'))
    #     except CashoutList.DoesNotExist:
    #         raise PubErrorCustom("此纪录不存在!")
    #
    #     cashlist.status = '2'
    #     cashlist.updtime = time.mktime(timezone.now().timetuple())
    #     cashlist.save()
    #
    #     upd_bal(userid=cashlist.userid_to,cashout_bal = cashlist.amount*-1)
    #
    #     return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def upd_passwd(self,request):

        if self.request.user.passwd != self.request.data_format.get('oldpasswd'):
            raise PubErrorCustom("密码错误!")

        self.request.user.passwd = self.request.data_format.get('passwd')
        self.request.user.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def upd_paypasswd(self, request):

        if self.request.user.pay_passwd != self.request.data_format.get('oldpasswd'):
            raise PubErrorCustom("密码错误!")

        self.request.user.pay_passwd = self.request.data_format.get('passwd')
        self.request.user.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector()
    def check_paypasswd(self, request):

        if self.request.user.pay_passwd != self.request.data_format.get('pay_passwd'):
            raise PubErrorCustom("支付密码错误!")

        return None


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def get_qrcode(self, request):

        QureSet=Qrcode.objects.all()

        if self.request.query_params_format.get("name"):
            QureSet=QureSet.filter(name=self.request.query_params_format.get("name"))

        if self.request.query_params_format.get("status"):
            QureSet=QureSet.filter(status=self.request.query_params_format.get("status"))

        return {"data":QrcodeModelSerializer(QureSet.filter(status=self.request.query_params_format.get("status")).order_by('-createtime'),many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def get_help(self, request):

        print("123123213123213123123213")

        print(self.request.query_params_format.get("userid"))

        ut = UtilTime()
        today = ut.arrow_to_string(ut.today, format_v="YYYY-MM-DD")


        query_format=str()
        query_params=list()

        if self.request.query_params_format.get("userid"):
            query_format = query_format + " and t1.userid=%s"
            query_params.append(self.request.query_params_format.get("userid"))
        if self.request.query_params_format.get("name"):
            query_format = query_format + " and t1.name=%s"
            query_params.append(self.request.query_params_format.get("name"))
        if self.request.query_params_format.get("loginname"):
            query_format = query_format + " and t1.loginname=%s"
            query_params.append(self.request.query_params_format.get("loginname"))
        if self.request.query_params_format.get("status"):
            query_format = query_format + " and t1.status=%s"
            query_params.append(self.request.query_params_format.get("status"))
        if self.request.query_params_format.get("type"):
            query_format = query_format + " and t2.type=%s"
            query_params.append(self.request.query_params_format.get("type"))

        user=Users.objects.raw("""
            SELECT t1.* FROM user as t1
              INNER JOIN `role` as t2 on t1.rolecode=t2.rolecode
              WHERE 1=1 %s
        """%(query_format),query_params)

        data=[]
        for item in user:

            data.append({
                "createtime": timestamp_toTime(item.createtime),
                "up_bal": round(item.up_bal, 2),
                "bal1": round(item.up_bal - item.cashout_bal - item.bal,2),
                "bal" : round(item.bal,2),
                "cashout_bal" : round(item.cashout_bal,2),
                "name": item.name,
                "userid": item.userid,
                "loginname":item.loginname
            })
        return {"data":data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def get_ok_qrcode(self, request):

        ut = UtilTime()
        today = ut.arrow_to_string(ut.today, format_v="YYYY-MM-DD")

        start_time = ut.string_to_timestamp(today + ' 00:00:01')
        end_time = ut.string_to_timestamp(today + ' 23:59:59')

        QureSet=Qrcode.objects.all()


        if request.user.rolecode in ["4001"]:
            QureSet = QureSet.filter(userid=request.user.userid)
        else:
            if self.request.query_params_format.get("userid"):
                QureSet = QureSet.filter(userid=self.request.query_params_format.get("userid"))

        if self.request.query_params_format.get("name"):
            QureSet=QureSet.filter(name=self.request.query_params_format.get("name"))

        if self.request.query_params_format.get("status"):
            QureSet=QureSet.filter(status=self.request.query_params_format.get("status"))

        if self.request.query_params_format.get("wechathelper_id"):
            QureSet = QureSet.filter(wechathelper_id=self.request.query_params_format.get("wechathelper_id"))

        data=[]

        for item in QureSet.filter(status__in=["0", "2", "3","5"]).order_by('-createtime'):
            confirm_tot = 0.0
            today_confirm_tot = 0.0
            statusname = Choices_to_Dict('qrcode_status')[item.status]

            all_tot = 0.0
            today_all_tot = 0.0
            for inner_item in PayCallList.objects.filter(name=item.name):
                if inner_item.status == '0':
                    confirm_tot = float(confirm_tot) + float(inner_item.amount)

                    if start_time <= inner_item.createtime <= end_time:
                        today_confirm_tot = float(today_confirm_tot) + float(inner_item.amount)


                all_tot = float(all_tot) + float(inner_item.amount)

                if start_time <= inner_item.createtime <= end_time:
                    today_all_tot = float(today_all_tot) + float(inner_item.amount)

            data.append({
                "statusname" : statusname,
                "createtime" : timestamp_toTime(item.createtime),
                "confirm_tot" : round(confirm_tot,2),
                "today_confirm_tot" : round(today_confirm_tot,2),
                "all_tot" : round(all_tot,2),
                "today_all_tot" : round(today_all_tot,2),
                "name" : item.name,
                "id" : item.id,
                "usecount":item.usecount
            })

        return {"data":data}


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def upd_status_qrcode(self, request):

        Qrcode.objects.filter(id=request.data_format.get("id")).update(status=request.data_format.get("status"))

        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True,lock={"resource":LOAD_QRCODE})
    def upd_qrcode(self, request):

        if not request.data_format.get("name"):
            raise PubErrorCustom("微信昵称不能为空!")
        try:
            obj=Qrcode.objects.get(id=request.data_format.get("id"))
            for item in Qrcode.objects.filter(name=request.data_format.get("name")):
                if item.id != obj.id:
                    raise PubErrorCustom("一个微信昵称只能存一张二维码!")
            obj.name = request.data_format.get("name")
            obj.save()
        except Qrcode.DoesNotExist :
            raise  PubErrorCustom("该二维码不存在,请刷新页面")

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True,lock={"resource":LOAD_QRCODE})
    def del_qrcode(self, request):

        Qrcode.objects.filter(id=request.data_format.get("id")).delete()

        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True,lock={"resource":LOAD_QRCODE})
    def open_qrcode(self, request):

        for item in Qrcode.objects.filter(id=request.data_format.get("id")):
            item.status = '3'
            item.save()

        return None



    #代理编辑
    @list_route(methods=['GET'])
    @Core_connector()
    def get_menu(self,request, *args, **kwargs):

        if request.user.rolecode in ["1000"]:
            return { "data" : {"router" : [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                        {"path": '/logquery', "component": "logquery", "name": '登录日志'}
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'}
                    ]
                },
                {
                    "path": '/manage',
                    "component": "Home",
                    "name": '管理员管理',
                    "iconCls": 'el-icon-s-platform',
                    "children": [
                        {"path": '/adminadd', "component": "adminadd", "name": '添加管理员'},
                    ]
                },
                {
                    "path": '/business',
                    "component": "Home",
                    "name": '商户管理',
                    "iconCls": 'el-icon-s-shop',
                    "children": [
                        {"path": '/waitbn', "component": "waitbn", "name": '待审核商户'},
                        {"path": '/bnlist', "component": "bnlist", "name": '商户列表'}
                    ]
                },
                {
                    "path": '/agent',
                    "component": "Home",
                    "name": '代理人管理',
                    "iconCls": 'el-icon-s-custom',
                    "children": [
                        {"path": '/agentadd', "component": "agentadd", "name": '待审核代理人'},
                        {"path": '/agentlist', "component": "agentlist", "name": '代理人列表'}
                    ]
                },
                {
                    "path": '/finance',
                    "component": "Home",
                    "name": '财务数据',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passcount', "component": "passcount", "name": '渠道数据'},
                        {"path": '/ordercount', "component": "ordercount", "name": '每日报表'},
                        {"path": '/ballist_admin', "component": "ballist_admin", "name": '资金明细'},
                        {"path": '/ubaladmin', "component": "ubaladmin", "name": '调账'},
                    ]
                },
                {
                    "path": '/pay',
                    "component": "Home",
                    "name": '支付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/paypassNew', "component": "paypassNew", "name": '支付渠道'},
                        {"path": '/paytype', "component": "paytype", "name": '支付方式'},
                        {"path": '/cashoutlist1', "component": "cashoutlist1", "name": '打款记录'},
                    ]
                },
                {
                    "path": '/order',
                    "component": "Home",
                    "name": '订单管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/orderlist', "component": "orderlist", "name": '订单列表'},
                        {"path": '/cashoutlist_admin_df', "component": "cashoutlist_admin_df", "name": '代付订单列表'}
                    ]
                },
                {
                    "path": '/sys',
                    "component": "Home",
                    "name": '系统管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/whitelist', "component": "whitelist", "name": '白名单管理'},
                        {"path": '/cache', "component": "cache", "name": '缓存管理'}
                    ]
                },
                {
                    "path": '/cqmanage',
                    "component": "Home",
                    "name": '码商管理',
                    "iconCls": 'el-icon-user-solid',
                    "children": [
                        {"path": '/codequotient', "component": "codequotient", "name": '码商维护'},
                    ]
                },
                # {
                #     "path": '/wechathelpermanage',
                #     "component": "Home",
                #     "name": '店员助手管理',
                #     "iconCls": 'el-icon-coffee',
                #     "children": [
                #         {"path": '/wechathelper', "component": "wechathelper", "name": '店员助手维护'}
                #     ]
                # },
                # {
                #     "path": '/qrcode',
                #     "component": "Home",
                #     "name": '二维码管理',
                #     "iconCls": 'el-icon-picture',
                #     "children": [
                #         {"path": '/qr_code_pool', "component": "qr_code_pool", "name": '二维码新增'},
                #         {"path": '/qrcode_pools', "component": "qrcode_pools", "name": '二维码列表',
                #          "query": {"id": "id","wechathelper_id":"wechathelper_id"}}
                #     ]
                # },
            ]}}
        elif request.user.rolecode in ["1001"]:
            return {"data": {"router": [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                        {"path": '/logquery', "component": "logquery", "name": '登录日志'},
                        {"path": '/qqbot', "component": "qqbot", "name": 'QQ消息群发'}
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'}
                    ]
                },
                {
                    "path": '/business',
                    "component": "Home",
                    "name": '商户管理',
                    "iconCls": 'el-icon-s-shop',
                    "children": [
                        {"path": '/waitbn', "component": "waitbn", "name": '待审核商户'},
                        {"path": '/bnlist', "component": "bnlist", "name": '商户列表'}
                    ]
                },
                {
                    "path": '/agent',
                    "component": "Home",
                    "name": '代理人管理',
                    "iconCls": 'el-icon-s-custom',
                    "children": [
                        {"path": '/agentadd', "component": "agentadd", "name": '待审核代理人'},
                        {"path": '/agentlist', "component": "agentlist", "name": '代理人列表'}
                    ]
                },
                {
                    "path": '/finance',
                    "component": "Home",
                    "name": '财务数据',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/busicount', "component": "busicount", "name": '通道数据'},
                        {"path": '/passcount', "component": "passcount", "name": '渠道数据'},
                        {"path": '/ordercount', "component": "ordercount", "name": '每日报表'},
                        {"path": '/ballist_admin', "component": "ballist_admin", "name": '资金明细'},
                        {"path": '/ubaladmin', "component": "ubaladmin", "name": '调账'},
                        {"path": '/accCheckok', "component": "accCheckok", "name": '对账'},
                    ]
                },
                {
                    "path": '/pay',
                    "component": "Home",
                    "name": '支付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/paypassNew', "component": "paypassNew", "name": '支付渠道'},
                        {"path": '/paytype', "component": "paytype", "name": '支付方式'},
                        # {"path": '/up_cashout', "component": "up_cashout", "name": '提现申请(码商)'},
                        # {"path": '/upcashoutlist_ss', "component": "upcashoutlist_ss", "name": '提现申请记录(码商)'},
                        # {"path": '/upcashoutlist', "component": "upcashoutlist", "name": '打款记录(码商)'},
                        {"path": '/cashoutlist_admin', "component": "cashoutlist_admin", "name": '提现申请审核(下游)'},
                        {"path": '/cashoutlist1', "component": "cashoutlist1", "name": '打款记录(下游)'},
                    ]
                },
                {
                    "path": '/order',
                    "component": "Home",
                    "name": '订单管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/orderlist', "component": "orderlist", "name": '订单列表'},
                        {"path": '/cashoutlist_admin_df', "component": "cashoutlist_admin_df", "name": '代付订单列表'}
                    ]
                },
                {
                    "path": '/sys',
                    "component": "Home",
                    "name": '系统管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/whitelist', "component": "whitelist", "name": '白名单管理'},
                        {"path": '/cache', "component": "cache", "name": '缓存管理'}
                    ]
                },
                {
                    "path": '/cqmanage',
                    "component": "Home",
                    "name": '码商管理',
                    "iconCls": 'el-icon-user-solid',
                    "children": [
                        {"path": '/codequotient', "component": "codequotient", "name": '码商维护'},
                    ]
                },
                # {
                #     "path": '/cqmanage',
                #     "component": "Home",
                #     "name": '码商管理',
                #     "iconCls": 'el-icon-user-solid',
                #     "children": [
                #         {"path": '/codequotient', "component": "codequotient", "name": '码商维护'}
                #     ]
                # },
                # {
                #     "path": '/wechathelpermanage',
                #     "component": "Home",
                #     "name": '店员助手管理',
                #     "iconCls": 'el-icon-coffee',
                #     "children": [
                #         {"path": '/wechathelper', "component": "wechathelper", "name": '店员助手维护'}
                #     ]
                # },
                # {
                #     "path": '/qrcode',
                #     "component": "Home",
                #     "name": '二维码管理',
                #     "iconCls": 'el-icon-picture',
                #     "children": [
                #         {"path": '/qr_code_pool', "component": "qr_code_pool", "name": '二维码新增'},
                #         {"path": '/qrcode_pools', "component": "qrcode_pools", "name": '二维码列表',
                #          "query": {"id": "id","wechathelper_id":"wechathelper_id"}}
                #     ]
                # },
            ]}}
        elif request.user.rolecode in ["1005"]:
            return {"data": {"router": [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'}
                    ]
                },
                {
                    "path": '/pay',
                    "component": "Home",
                    "name": '支付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/cashout_daifu', "component": "cashout_daifu", "name": '申请提现(代付)'},
                        {"path": '/cashoutlist_admin_df', "component": "cashoutlist_admin_df", "name": '提现记录(代付)'}
                    ]
                },
                # {
                #     "path": '/cqmanage',
                #     "component": "Home",
                #     "name": '码商管理',
                #     "iconCls": 'el-icon-user-solid',
                #     "children": [
                #         {"path": '/codequotient', "component": "codequotient", "name": '码商维护'}
                #     ]
                # },
                # {
                #     "path": '/wechathelpermanage',
                #     "component": "Home",
                #     "name": '店员助手管理',
                #     "iconCls": 'el-icon-coffee',
                #     "children": [
                #         {"path": '/wechathelper', "component": "wechathelper", "name": '店员助手维护'}
                #     ]
                # },
                # {
                #     "path": '/qrcode',
                #     "component": "Home",
                #     "name": '二维码管理',
                #     "iconCls": 'el-icon-picture',
                #     "children": [
                #         {"path": '/qr_code_pool', "component": "qr_code_pool", "name": '二维码新增'},
                #         {"path": '/qrcode_pools', "component": "qrcode_pools", "name": '二维码列表',
                #          "query": {"id": "id","wechathelper_id":"wechathelper_id"}}
                #     ]
                # },
            ]}}
        elif request.user.rolecode in ["1006"]:
            return {"data": {"router": [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'}
                    ]
                },
                # {
                #     "path": '/business',
                #     "component": "Home",
                #     "name": '商户管理',
                #     "iconCls": 'el-icon-s-shop',
                #     "children": [
                #         {"path": '/waitbn', "component": "waitbn", "name": '待审核商户'},
                #         {"path": '/bnlist', "component": "bnlist", "name": '商户列表'}
                #     ]
                # },
                # {
                #     "path": '/agent',
                #     "component": "Home",
                #     "name": '代理人管理',
                #     "iconCls": 'el-icon-s-custom',
                #     "children": [
                #         {"path": '/agentadd', "component": "agentadd", "name": '待审核代理人'},
                #         {"path": '/agentlist', "component": "agentlist", "name": '代理人列表'}
                #     ]
                # },
                # {
                #     "path": '/finance',
                #     "component": "Home",
                #     "name": '财务数据',
                #     "iconCls": 'el-icon-s-finance',
                #     "children": [
                #         {"path": '/busicount', "component": "busicount", "name": '通道数据'},
                #         {"path": '/passcount', "component": "passcount", "name": '渠道数据'},
                #         {"path": '/ordercount', "component": "ordercount", "name": '每日报表'},
                #         {"path": '/ballist_admin', "component": "ballist_admin", "name": '资金明细'},
                #         {"path": '/ubaladmin', "component": "ubaladmin", "name": '调账'},
                #         {"path": '/accCheckok', "component": "accCheckok", "name": '对账'},
                #     ]
                # },
                {
                    "path": '/pay',
                    "component": "Home",
                    "name": '支付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/paypassNew', "component": "paypassNew", "name": '支付渠道'},
                        {"path": '/paytype', "component": "paytype", "name": '支付方式'},
                        # {"path": '/up_cashout', "component": "up_cashout", "name": '提现申请(码商)'},
                        # {"path": '/upcashoutlist_ss', "component": "upcashoutlist_ss", "name": '提现申请记录(码商)'},
                        # {"path": '/upcashoutlist', "component": "upcashoutlist", "name": '打款记录(码商)'},
                        {"path": '/cashoutlist_admin', "component": "cashoutlist_admin", "name": '提现申请审核(下游)'},
                        {"path": '/cashoutlist1', "component": "cashoutlist1", "name": '打款记录(下游)'},
                    ]
                },
                {
                    "path": '/order',
                    "component": "Home",
                    "name": '订单管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/orderlist', "component": "orderlist", "name": '订单列表'},
                        {"path": '/cashoutlist_admin_df', "component": "cashoutlist_admin_df", "name": '代付订单列表'}
                    ]
                },
                {
                    "path": '/sys',
                    "component": "Home",
                    "name": '系统管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/whitelist', "component": "whitelist", "name": '白名单管理'},
                        {"path": '/cache', "component": "cache", "name": '缓存管理'}
                    ]
                },
                # {
                #     "path": '/cqmanage',
                #     "component": "Home",
                #     "name": '码商管理',
                #     "iconCls": 'el-icon-user-solid',
                #     "children": [
                #         {"path": '/codequotient', "component": "codequotient", "name": '码商维护'},
                #     ]
                # },
                # {
                #     "path": '/cqmanage',
                #     "component": "Home",
                #     "name": '码商管理',
                #     "iconCls": 'el-icon-user-solid',
                #     "children": [
                #         {"path": '/codequotient', "component": "codequotient", "name": '码商维护'}
                #     ]
                # },
                # {
                #     "path": '/wechathelpermanage',
                #     "component": "Home",
                #     "name": '店员助手管理',
                #     "iconCls": 'el-icon-coffee',
                #     "children": [
                #         {"path": '/wechathelper', "component": "wechathelper", "name": '店员助手维护'}
                #     ]
                # },
                # {
                #     "path": '/qrcode',
                #     "component": "Home",
                #     "name": '二维码管理',
                #     "iconCls": 'el-icon-picture',
                #     "children": [
                #         {"path": '/qr_code_pool', "component": "qr_code_pool", "name": '二维码新增'},
                #         {"path": '/qrcode_pools', "component": "qrcode_pools", "name": '二维码列表',
                #          "query": {"id": "id","wechathelper_id":"wechathelper_id"}}
                #     ]
                # },
            ]}}
        elif request.user.rolecode in ["2001"]:
            return { "data" : {"router" : [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                        {"path": '/business_tost', "component": "business_tost", "name": '技术接入'}
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'},
                        {"path": '/paypasswd', "component": "paypasswd", "name": '支付密码修改'}
                    ]
                },
                {
                    "path": '/chongzhi',
                    "component": "Home",
                    "name": '充值管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/neichong', "component": "neichong", "name": '充值'}
                    ]
                },
                {
                    "path": '/daifu',
                    "component": "Home",
                    "name": '代付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/cashoutlist_tixiandaifu', "component": "cashoutlist_tixiandaifu", "name": '提现'},
                        {"path": '/cashoutlist_df', "component": "cashoutlist_df", "name": '提现列表'}
                    ]
                } if str(request.user.isapidaifu)=='0' else {
                    "path": '/daifu',
                    "component": "Home",
                    "name": '代付管理',
                    "iconCls": 'el-icon-s-finance',
                },
                {
                    "path": '/order',
                    "component": "Home",
                    "name": '订单管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/orderlist_other', "component": "orderlist_other", "name": '订单列表'},
                    ]
                },
                {
                    "path": '/finance',
                    "component": "Home",
                    "name": '财务数据',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/ordercount_business', "component": "ordercount_business", "name": '每日报表'},
                        {"path": '/ballist', "component": "ballist", "name": '资金明细'},
                    ]
                },
                {
                    "path": '/pay',
                    "component": "Home",
                    "name": '支付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/rate', "component": "rate", "name": '费率'},
                        # {"path": '/bankinfo', "component": "bankinfo", "name": '银行卡设置'},
                        {"path": '/cashoutlist_sb', "component": "cashoutlist_sb", "name": '提现申请'} if self.request.user.istixianpage != '0' else {"path": '/cashout', "component": "cashout", "name": '提现申请'},
                        {"path": '/cashoutlist', "component": "cashoutlist", "name": '提现申请记录'},
                        {"path": '/cashoutlist1', "component": "cashoutlist1", "name": '打款记录'},
                    ]
                },
            ]}}
        elif request.user.rolecode in ["3001"]:
            return { "data" : {"router" : [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                        {"path": '/business_tost', "component": "business_tost", "name": '技术接入'}
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'},
                        {"path": '/paypasswd', "component": "paypasswd", "name": '支付密码修改'}
                    ]
                },
                {
                    "path": '/business',
                    "component": "Home",
                    "name": '商户管理',
                    "iconCls": 'el-icon-s-shop',
                    "children": [
                        {"path": '/bnlist_agent', "component": "bnlist_agent", "name": '商户列表'}
                    ]
                },
                {
                    "path": '/finance',
                    "component": "Home",
                    "name": '财务数据',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/ordercount_agent', "component": "ordercount_agent", "name": '每日报表'},
                        {"path": '/ballist', "component": "ballist", "name": '资金明细'},
                    ]
                },
                {
                    "path": '/order',
                    "component": "Home",
                    "name": '订单管理',
                    "iconCls": 'el-icon-s-order',
                    "children": [
                        {"path": '/orderlist_agent', "component": "orderlist_agent", "name": '订单列表'}
                    ]
                },
                {
                    "path": '/pay',
                    "component": "Home",
                    "name": '支付管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        # {"path": '/rate', "component": "rate", "name": '费率'},
                        # {"path": '/bankinfo', "component": "bankinfo", "name": '银行卡设置'},
                        {"path": '/cashout', "component": "cashout", "name": '提现申请'},
                        {"path": '/cashoutlist', "component": "cashoutlist", "name": '提现申请记录'},
                        {"path": '/cashoutlist1', "component": "cashoutlist1", "name": '打款记录'},
                    ]
                },
            ]}}
        elif request.user.rolecode in ["4001"] :
            return {"data": {"router": [
                {
                    "path": '/',
                    "component": "Home",
                    "name": '首页',
                    "iconCls": 'el-icon-s-home',
                    "children": [
                        {"path": '/dashboard', "component": "dashboard", "name": '桌面'},
                        {"path": '/msQuerytoken', "component": "msQuerytoken", "name": 'Token获取'}
                    ]
                },
                {
                    "path": '/anquan',
                    "component": "Home",
                    "name": '安全管理',
                    "iconCls": 'el-icon-s-finance',
                    "children": [
                        {"path": '/passwd', "component": "passwd", "name": '密码修改'}
                    ]
                },
                {
                    "path": '/cqmanage',
                    "component": "Home",
                    "name": '微博红包管理',
                    "iconCls": 'el-icon-user-solid',
                    "children": [
                        {"path": '/wbTask', "component": "wbTask", "name": '计划任务'},
                        {"path": '/wbsendlist', "component": "wbsendlist", "name": '红包明细'},
                        {"path": '/sendhbmanange', "component": "sendhbmanange", "name": '发送红包账号管理'},
                        {"path": '/robhbmanange', "component": "robhbmanange", "name": '抢红包账号管理'},
                        {"path": '/group', "component": "group", "name": '群管理'},
                        {"path": '/groupmember', "component": "groupmember", "name": '群成员管理'},
                    ]
                },

            ]}}

from libs.core.decorator.response import Core_connector_exec
from libs.utils.qrcode import decode_qr
from apps.utils import url_join

class PublicFileAPIView(viewsets.ViewSet):

    @list_route(methods=['POST'])
    @Core_connector_exec(transaction=True,lock={"resource":LOAD_QRCODE})
    def upload(self,request, *args, **kwargs):

        if not request.data.get("qrtype"):
            raise PubErrorCustom("请选择二维码类型!")

        if not request.data.get("userid") or str(request.data.get("userid"))=='0':
            raise PubErrorCustom("请选择码商!")

        if request.data.get("qrtype") == 'QR001' :
            if not request.data.get("wechathelper_id") or str(request.data.get("wechathelper_id")) == '0':
                raise PubErrorCustom("请选择店员助手!")


        QrcodeObj=Qrcode.objects.filter(status__in=[0,1,2,3,5])


        file_name = request.data.get("file_name").split(".")[0]

        for item in QrcodeObj:
            if item.name == file_name :
                raise PubErrorCustom("一个微信昵称只能存一张二维码!")

        create_order_dict = {
            "name" : file_name,
            "status" : '1',
            "updtime" : 0,
            "userid" : request.data.get("userid"),
            "wechathelper_id" : request.data.get("wechathelper_id"),
            "type" : request.data.get("qrtype")
        }

        QrcodeObj=Qrcode.objects.create(**create_order_dict)

        UPLOAD_FILE_PATH = '/var/nginx_upload/qrcode/'
        isExists = os.path.exists(UPLOAD_FILE_PATH)

        if not isExists:
            os.makedirs(UPLOAD_FILE_PATH)

        new_file_name = request.data.get("file_md5") + '_' + "%08d"%(QrcodeObj.id) + '.jpeg'
        new_file_path = ''.join([UPLOAD_FILE_PATH, new_file_name])


        with open(new_file_path, 'wb') as new_file:
            with open(request.data.get('file_path'), 'rb') as f:
                new_file.write(f.read())
        url = '/nginx_upload/qrcode/%s'%(new_file_name)

        decode_res = decode_qr(url_join(url))

        while not decode_res:
            decode_res=decode_qr(url_join(url))

        QrcodeObj.url = decode_res
        QrcodeObj.path = url
        QrcodeObj.save()
        return {'data': QrcodeModelSerializer(QrcodeObj,many=False).data}



