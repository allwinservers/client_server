
import os
from apps.public.models import Sysparam,SysNumber
from django_redis import get_redis_connection
from libs.utils.http_request import send_request
from utils.exceptions import PubErrorCustom

def get_sysparam():
    return Sysparam.objects.get()


def get_sysnumber(type=None):
    if not type:
        raise PubErrorCustom("类型不能为空!")
    try:
        return SysNumber.objects.select_for_update().get(type=type)
    except SysNumber.DoesNotExist:
        raise PubErrorCustom("轮询表无记录,类型{}".format(type))

class HelperBase(object):

    def __init__(self,**kwargs):
        """
        所有登录助手基类
        :param kwargs:
            md5name : 执行脚本文件路径,
            type : 二维码类型
        """
        self.md5name = kwargs.get("md5name")
        self.type = kwargs.get("type")
        self.redis_cil = get_redis_connection("helper")

        if self.type == 'QR001':
            self.basepath = "/project/tools/call_help/run/wechat"
        elif self.type == 'QR005':
            self.basepath = "/project/tools/call_help/run/flm"


class HelperWechat(HelperBase):

    def __init__(self,**kwargs):
        kwargs.setdefault("type",'QR001')
        super().__init__(**kwargs)

        self.path = "{}/{}".format(self.basepath,self.md5name)
        self.runname = 'wechat_main.py'

    def helper_add(self):
        if os.path.exists(self.path):
            os.system('cd {} && rm -rf {}'.format(self.basepath,self.md5name))
        os.system('mkdir -p {} && cp {}/{} {}/{}'.format(self.path,self.basepath,self.runname,self.path,self.runname))

    def helper_del(self):
        os.system('cd {} && rm -rf {}'.format(self.basepath,self.md5name))

    def helper_login(self):
        res=send_request(url="http://localhost:5000/helper_wechat_login",method='POST',data={
            "runname":self.runname,
            "basepath":self.basepath,
            "path":self.path,
            "md5name":self.md5name
        })
        if not res[0]:
            raise PubErrorCustom("连接登录服务器有误,请联系客服!")

    def helper_stop(self):
        res=send_request(url="http://localhost:5000/helper_wechat_stop",method='POST',data={
            "runname":self.runname,
            "basepath":self.basepath,
            "path":self.path,
            "md5name":self.md5name
        })
        if not res[0]:
            raise PubErrorCustom("连接登录服务器有误,请联系客服!")


class HelperFlm(HelperBase):

    def __init__(self,**kwargs):
        kwargs.setdefault("type",'QR005')
        super().__init__(**kwargs)

        self.path = "{}/{}".format(self.basepath,self.md5name)
        self.runname = 'flm_main.py'

    def helper_add(self):
        if os.path.exists(self.path):
            os.system('cd {} && rm -rf {}'.format(self.basepath,self.md5name))
        os.system('mkdir -p {} && cp {}/{} {}/{}'.format(self.path,self.basepath,self.runname,self.path,self.runname))

    def helper_del(self):
        os.system('cd {} && rm -rf {}'.format(self.basepath,self.md5name))




