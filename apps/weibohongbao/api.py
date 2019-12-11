import json
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector

from auth.authentication import Authentication

from libs.utils.exceptions import PubErrorCustom
from libs.utils.mytime import send_toTimestamp
from apps.weibohongbao.models import WeiboUser,WeiboParams,WeiboGroup,WeiboGroupMember,WeiboTask,WeiboSendList

from apps.weibohongbao.serializers import WeiboUserModelSerializer,WeiboGroupModelSerializer,WeiboGroupMemberModelSerializer,WeiboTaskModelSerializer,WeiboSendListModelSerializer
from requests import request as requestR

from apps.utils import createorder_url

class WeiBoAPIView(viewsets.ViewSet):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def addWeiboUser(self, request, *args, **kwargs):

        WeiboUser.objects.create(**dict(
            userid=request.user.userid,
            username=request.data_format['username'],
            password=request.data_format.get("password", ""),
            type=request.data_format['type'],
            status=request.data_format['status'],
            uid = request.data_format['username']
        ))
        return None

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def getWeiboUser(self, request, *args, **kwargs):

        query = WeiboUser.objects.filter(userid=request.user.userid)

        if request.query_params_format.get("username", None):
            query = query.filter(username=request.query_params_format['username'])

        if request.query_params_format.get("uid", None):
            query = query.filter(uid=request.query_params_format['uid'])

        if request.query_params_format.get("session_status", None):
            query = query.filter(session_status=request.query_params_format['session_status'])

        if request.query_params_format.get("type", None):
            query = query.filter(type=request.query_params_format['type'])

        if request.query_params_format.get("status", None):
            query = query.filter(status=request.query_params_format['status'])

        if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
            query = query.filter(
                createtime__lte=send_toTimestamp(request.query_params_format.get("enddate")),
                createtime__gte=send_toTimestamp(request.query_params_format.get("startdate")))

        return {"data": WeiboUserModelSerializer(query, many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def getSendList(self, request, *args, **kwargs):

        query = WeiboSendList.objects.filter(userid=request.user.userid)

        if request.query_params_format.get("userid", None):
            query = query.filter(userid=request.query_params_format['userid'])

        if request.query_params_format.get("uid", None):
            query = query.filter(uid=request.query_params_format['uid'])


        if request.query_params_format.get("groupid", None):
            query = query.filter(groupid=request.query_params_format['groupid'])

        if request.query_params_format.get("setid", None):
            query = query.filter(setid=request.query_params_format['setid'])

        if request.query_params_format.get("status", None):
            query = query.filter(status=request.query_params_format['status'])

        if request.query_params_format.get("startdate") and request.query_params_format.get("enddate"):
            query = query.filter(
                createtime__lte=send_toTimestamp(request.query_params_format.get("enddate")),
                createtime__gte=send_toTimestamp(request.query_params_format.get("startdate")))

        return {"data": WeiboSendListModelSerializer(query, many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def updWeiboUser(self, request, *args, **kwargs):
        try:
            wbUobj = WeiboUser.objects.get(id=request.data_format['id'])
        except WeiboUser.DoesNotExist:
            raise PubErrorCustom("无此账号信息!")

        wbUobj.password = request.data_format['password']

        wbUobj.status = request.data_format['status']
        wbUobj.session = request.data_format['session']
        wbUobj.save()

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def delWeiboUser(self, request, *args, **kwargs):
        WeiboUser.objects.filter(id=request.data_format['id']).delete()

        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def getVerCodeForWeibo(self, request, *args, **kwargs):

        url="{}/wb/getVerCodeForWeibo".format(createorder_url())
        res = json.loads(requestR(url=url,method="POST",data={"id":request.data_format['id']}).content.decode('utf-8'))
        print(res)
        if res['rescode'] != '10000':
            raise PubErrorCustom(res['msg'])

        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def vercodeLoginForWeibo(self, request, *args, **kwargs):
        if not request.data_format.get("vercode",None):
            raise PubErrorCustom("验证码不能为空!")

        url="{}/wb/vercodeLoginForWeibo".format(createorder_url())
        res = json.loads(requestR(url=url,method="POST",
                    data={"id":request.data_format['id'],"vercode":request.data_format['vercode']})\
                         .content.decode('utf-8'))
        print(res)
        if res['rescode'] != '10000':
            raise PubErrorCustom(res['msg'])

        return None

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def loginForPc(self, request, *args, **kwargs):

        url="{}/wb/loginForPc".format(createorder_url())
        print(request.data_format['datas'])
        res = json.loads(requestR(
                url=url,
                method="POST",
                headers={
                    "Content-Type":"application/json"
                },
                json={"datas":request.data_format['datas']}
        ).content.decode('utf-8'))

        print(res)
        if res['rescode'] != '10000':
            raise PubErrorCustom(res['msg'])

        return {"data":res['data']}

    # @list_route(methods=['POST'])
    # @Core_connector(transaction=True)
    # def initOtherDataForWeibo(self, request, *args, **kwargs):
    #
    #     try:
    #         paypass = WeiboPayUsername.objects.get(id=request.data_format['id'])
    #     except WeiboPayUsername.DoesNotExist:
    #         raise PubErrorCustom("无此账号信息!")
    #     if paypass.type!='0':
    #         raise PubErrorCustom("只有发送红包的账号可以验证码登录!")
    #
    #     s  = WeiboLogin(sessionRes=json.loads(paypass.session))
    #     s.datainitHandler()
    #     # print(session)
    #     paypass.session = json.dumps(s.sessionRes)
    #     paypass.save()
    #     return None
    #
    # @list_route(methods=['POST'])
    # @Core_connector(transaction=True)
    # def getSessionSSS(self, request, *args, **kwargs):
    #
    #     try:
    #         paypass = WeiboPayUsername.objects.get(id=request.data_format['id'])
    #     except WeiboPayUsername.DoesNotExist:
    #         raise PubErrorCustom("无此账号信息!")
    #     session = json.dumps({
    #         "st": "769696",
    #         "uid": "6424853549",
    #         "gsid": "_2A25w49PpDeRxGeBK6VYZ9S3JzzWIHXVRuWAhrDV6PUJbkdAKLVTRkWpNR848UCh0aEfqVWJJUXU-K8hCJACsw_Od",
    #         "cookie": {
    #             "SUB": "_2A25w49PqDeRhGeBK6VYZ9S3JzzWIHXVQfoeirDV8PUJbitANLVLFkWtNR848UBzF-WUfgZC7eFd_O_J3fBaGLzE9",
    #             "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5NHD95QcShzX1h-0SKB4Ws4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSoBEShnfe0-X1Btt",
    #             "SCF": "AjOaGw1K_o2AsNr4Ql_tYHnWtwXMs_0EzBjlhVrMRn9__3dFIc0a2lum8eMmDo5p-w..",
    #             "SUHB": "0jBIffZWGBgbfV"
    #         }
    #     })
    #     paypass.session = session
    #
    #     paypass.save()
    #
    #     return None
    #

    #
    # @list_route(methods=['POST'])
    # @Core_connector(transaction=True)
    # def delPayPassLinkData(self, request, *args, **kwargs):
    #     WeiboPayUsername.objects.filter(id=request.data_format['id']).delete()
    #
    #     return None
    #

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def addGroup(self, request, *args, **kwargs):

        if not request.data_format.get("uid",None):
            raise PubErrorCustom("群组长uid不能为空！")

        data={
            "uid":request.data_format.get("uid",None),
            "userid":request.user.userid
        }

        url="{}/wb/addGroup".format(createorder_url())
        res = json.loads(requestR(url=url,method="POST",
                    data=data).content.decode('utf-8'))
        print(res)
        if res['rescode'] != '10000':
            raise PubErrorCustom(res['msg'])

        return None


    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def getGroup(self, request, *args, **kwargs):
        print(request.user.userid)
        query = WeiboGroup.objects.filter(userid=request.user.userid)

        return {"data": WeiboGroupModelSerializer(query, many=True).data}

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def getGroupMember(self, request, *args, **kwargs):
        query = WeiboGroupMember.objects.filter(userid=request.user.userid)

        if request.query_params_format.get("uid", None):
            query = query.filter(uid=request.query_params_format['uid'])

        if request.query_params_format.get("name", None):
            query = query.filter(name=request.query_params_format['name'])

        if request.query_params_format.get("group_id", None):
            query = query.filter(group_id=request.query_params_format['group_id'])

        return {"data": WeiboGroupMemberModelSerializer(query, many=True).data}



    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def addTask(self, request, *args, **kwargs):

        try:
            wbGObj = WeiboGroup.objects.get(group_id=request.data_format['group'])
        except WeiboGroup.DoesNotExist:
            raise PubErrorCustom("群不存在!")

        robnumber = WeiboGroupMember.objects.filter(group_id=wbGObj.group_id).count()
        if robnumber<=0:
            raise PubErrorCustom("群里无人员！")
        if 100%robnumber>0:
            raise PubErrorCustom("群抢红包人数必须被100整除!")

        WeiboTask.objects.create(**dict(
            userid = request.user.userid,
            taskname = request.data_format['name'],
            minamount = request.data_format['minamount'],
            maxamount = request.data_format['maxamount'],
            groupid = wbGObj.group_id,
            amountwhat = request.data_format['amountwhat'],
            uid = wbGObj.uid,
            sort = request.data_format['sort'],
            date = request.data_format['date'],
            robnumber = robnumber
        ))
        return None


    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def updUmark(self, request, *args, **kwargs):
        try:
            wbTObj = WeiboTask.objects.select_for_update().get(taskid=request.data_format['taskid'])
        except wbTObj.DoesNotExist:
            raise PubErrorCustom("任务不存在!")

        wbTObj.umark = '0' if wbTObj.umark!='0' else '1'
        wbTObj.save()
        return None




    @list_route(methods=['GET'])
    @Core_connector()
    def getTask(self, request, *args, **kwargs):

        query = WeiboTask.objects.filter(userid = request.user.userid)

        if request.query_params_format.get("date", None):
            query = query.filter(date=request.query_params_format['date'])

        return {"data": WeiboTaskModelSerializer(query.order_by('sort'), many=True).data}