

from apps.pay.models import PayPassLinkType
from apps.public.models import Qrcode,QrcodeUseList
from libs.utils.mytime import UtilTime
from apps.public.utils import get_sysparam,get_sysnumber
from apps.order.models import Order
from libs.utils.log import logger

from utils.exceptions import PubErrorCustom,InnerErrorCustom

import random


def get_Rate(userid,paytypeid,type="1"):
    sysparam = get_sysparam()

    try:
        rate = PayPassLinkType.objects.get(paytypeid=paytypeid, to_id=userid, type=type).rate
    except PayPassLinkType.DoesNotExist:
        rate = sysparam.baserate

    return rate

# from libs.utils.redlock import ReadLock
# from include.data.redislockkey import LOAD_QRCODE


class QrcodeBase(object) :

    def __init__(self,type=None):
        self.ut = UtilTime()

        #当前时间
        self.today = self.ut.today

        #有效时间
        self.order_failure_time = int(get_sysparam().order_failure_time)

        #二维码类型
        self.type = type

    def get_qrcode_obj(self,id):
        try:
            qrcode_obj = Qrcode.objects.get(id=id,status='0')
        except Qrcode.DoesNotExist:
            raise PubErrorCustom("无此二维码!")
        return qrcode_obj


    def get_expire_time(self,updtime=None,timetype=None):
        """
        获取过期时间(时间戳)
        :param timetype: 为None时默认为时间戳,为True代表时间
        :return:
        """

        return  self.ut.timestamp_to_arrow(updtime).replace(seconds=self.order_failure_time ).timestamp if not timetype else \
                     self.ut.timestamp_to_arrow(updtime).replace(seconds=self.order_failure_time )

    def get_valid_time(self,timetype=None):
        """
        获取对应码的有效时间(时间戳)
        :param timetype: 为None时默认为时间戳,为True代表时间
        :return:
        """

        return self.today.replace(seconds=self.order_failure_time * -1).timestamp if not timetype else \
                     self.today.replace(seconds=self.order_failure_time * -1)

    def qrcode_valid(self,updtime=None):
        """
        判断二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """

        return True if self.get_valid_time() < updtime else False

    def get_qrcode(self,order=None):
        """
        #获取有效二维码
        :param
        :return:
        """
        #二维码轮询
        self.last_qr = get_sysnumber(self.type)
        qrcodes = Qrcode.objects.filter(status='0',type=self.type).order_by('id')
        if not qrcodes.exists():
            raise InnerErrorCustom("10010", "码池正在加紧制作二维码,请稍等刷新!")
        qrids = [ item.id for item in qrcodes ]
        qrids.sort()

        qrids_exists = [ item.qr_id for item in Order.objects.select_for_update().filter(qr_id__in=qrids,status=1,createtime__gte=self.get_valid_time()) \
                                if item.amount == order.amount ]

        logger.info("\n 二维码列表：{} \n 已存在相同金额的二维码列表：{}".format(qrids,qrids_exists))

        def check_valid_index_qrcode(index):
            max_qrids = len(qrids)-1
            index +=1
            index = 0 if index > max_qrids else index

            while index <= max_qrids:
                if qrids[index] not in qrids_exists:
                    return qrids[index]
                else:
                    index += 1

            return False

        #开始轮询检查
        res = check_valid_index_qrcode(qrids.index(int(self.last_qr.last_qrcode)) if int(self.last_qr.last_qrcode) in qrids else -1 )
        if not res:
            res = check_valid_index_qrcode(-1)
        if not res:
            raise InnerErrorCustom("10010", "码池正在加紧制作二维码,请稍等刷新!")
        else:
            self.last_qr.last_qrcode = res

        useing_qrcode_obj = [ item for item in qrcodes if item.id == self.last_qr.last_qrcode ][0]

        useing_qrcode_obj.updtime = self.ut.timestamp
        useing_qrcode_obj.save()
        self.last_qr.save()

        return useing_qrcode_obj


class QrCodeWechat(QrcodeBase):

    """
    微信二维码个码
    """

    def __init__(self):
        super().__init__(type='QR001')

    def qrcode_valid(self,updtime=None):

        """
        判断微信二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """
        return super().qrcode_valid(updtime=updtime)

    # def get_qrcode(self,order=None):
    #     """
    #     #获取一个有效二维码
    #     :param
    #     :return:
    #     """
    #
    #
    #     qrcode_list = Qrcode.objects.filter(status='0',type=self.type).order_by('id')
    #     if not qrcode_list.exists():
    #         return None
    #
    #     #获取二维码有效的obj
    #     qrcode_valid_list=[]
    #     qrid_valid_list=[]
    #     for item in qrcode_list:
    #         #如果过期那么加入有效二维码obj
    #         if not self.qrcode_valid(updtime=item.updtime):
    #             qrcode_valid_list.append(item)
    #             qrid_valid_list.append(item.id)
    #
    #     if not len(qrid_valid_list):
    #         raise InnerErrorCustom("10010","码池正在加紧制作二维码,请稍等刷新!")
    #
    #     #筛选出最小值对应的obj
    #     obj = None
    #     sysnumber_obj = get_sysnumber()
    #     last_qrcode = sysnumber_obj.last_qrcode
    #
    #     if last_qrcode == max(qrid_valid_list) or last_qrcode == 0:
    #         obj = qrcode_valid_list[0]
    #     elif last_qrcode not in qrid_valid_list:
    #         obj = qrcode_valid_list[0]
    #     else:
    #         isFlag = False
    #         for item in qrcode_valid_list:
    #             if isFlag:
    #                 obj = item
    #                 break
    #             if item.id == last_qrcode:
    #                 isFlag = True
    #
    #     sysnumber_obj.last_qrcode = obj.id
    #     sysnumber_obj.save()
    #
    #     #使用二维码
    #     obj.updtime = self.ut.timestamp
    #     obj.save()
    #
    #     return obj

class QrCodeFlm(QrcodeBase):

    """
    付临门聚合码
    """

    def __init__(self):

        super().__init__(type='QR005')

    def qrcode_valid(self ,updtime=None):

        """
        判断付临门二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """
        return super().qrcode_valid(updtime=updtime)

    # def get_qrcode(self,order=None):
    #     """
    #     #获取付临门有效二维码
    #     :param
    #     :return:
    #     """
    #     qrcodes = Qrcode.objects.filter(status='0',type=self.type).order_by('id')
    #     if not qrcodes.exists():
    #         raise InnerErrorCustom("10010", "码池正在加紧制作二维码,请稍等刷新!")
    #
    #     qrids = [ item.id for item in qrcodes ]
    #     print(qrids)
    #     qrids_exists=[]
    #     for item in Order.objects.filter(qr_id__in=qrids,status=1,createtime__gte=self.get_valid_time()):
    #         if item.amount == order.amount:
    #             qrids_exists.append(item.qr_id)
    #
    #     print(qrids_exists)
    #     qrids_valid=list(set(qrids).difference(set(qrids_exists)))
    #     if not len(qrids_valid):
    #         raise InnerErrorCustom("10010", "码池正在加紧制作二维码,请稍等刷新!")
    #     print(qrids_valid)
    #     qrcode_valid_list = [ item for item in qrcodes if item.id in qrids_valid ]
    #
    #     obj = random.sample(qrcode_valid_list,1)[0]
    #     print(obj)
    #     obj.updtime = self.ut.timestamp
    #     obj.save()
    #
    #     return obj

class QrCodeNxys(QrcodeBase):

    """
    农信易扫聚合码
    """

    def __init__(self):

        super().__init__(type='QR010')

    def qrcode_valid(self ,updtime=None):

        """
        判断付临门二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """
        return super().qrcode_valid(updtime=updtime)

class QrCodeJyys(QrcodeBase):

    """
    金燕易商聚合码
    """

    def __init__(self):

        super().__init__(type='QR015')

    def qrcode_valid(self ,updtime=None):

        """
        判断付临门二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """
        return super().qrcode_valid(updtime=updtime)

class QrCodeZjnx(QrcodeBase):
    """
    金燕易商聚合码
    """

    def __init__(self):
        super().__init__(type='QR020')

    def qrcode_valid(self, updtime=None):
        """
        判断付临门二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """
        return super().qrcode_valid(updtime=updtime)

class QrCodeYzf(QrcodeBase):
    """
    金燕易商聚合码
    """

    def __init__(self):
        super().__init__(type='QR025')

    def qrcode_valid(self, updtime=None):
        """
        判断付临门二维码是否有效
        :param updtime:  创建时间时间戳
        :return:  True : 有效 , False : 失效
        """
        return super().qrcode_valid(updtime=updtime)