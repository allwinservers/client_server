from django.db import models
import random
import time
import datetime
from django.utils import timezone
import binascii
import os


class Memu(models.Model):


    class Meta:
        verbose_name = '菜单表'
        verbose_name_plural = verbose_name
        db_table = 'menu'


class Sysparam(models.Model):

    id=models.BigAutoField(primary_key=True)
    baserate = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="基本利率，如果下游没有填写利率那么就按照这个利率走!")
    order_failure_time = models.IntegerField(default=0,verbose_name="单位秒")

    bal = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="内部账余额")
    business_agent_tot = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="商户代理总余额")

    class Meta:
        verbose_name = '系统参数表'
        verbose_name_plural = verbose_name
        db_table = 'sysparam'

class WechatHelper(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=60,default="",verbose_name="店员微信昵称")
    login = models.CharField(max_length=1,default="1",verbose_name="是否登录,0-登录,1-未登录")
    qrcode = models.CharField(max_length=255,default="",verbose_name="登录二维码路径")
    md5name = models.CharField(max_length=60,default='',verbose_name="md5文件名")

    type = models.CharField(max_length=5,default='QR001' ,
                            verbose_name="""二维码类型 QR001-微信个人二维码,
                                         QR005-付临门聚合支付码""")

    createtime = models.BigIntegerField(default=0)

    status_name = None

    def save(self, *args, **kwargs):
        t = time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        if not self.md5name:
            self.md5name = self.generate_key()
        return super(WechatHelper, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(32)).decode()

    class Meta:
        verbose_name = '店员助手表'
        verbose_name_plural = verbose_name
        db_table = 'wechathelper'

class QrCodeLinkPayType(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=5,default='QR001' ,
                            verbose_name="""二维码类型 QR001-微信个人二维码,
                                         QR005-付临门聚合支付码""")
    paytypeid = models.BigIntegerField(default=0,verbose_name="支付方式")
    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(QrCodeLinkPayType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '二维码支付方式关联表'
        verbose_name_plural = verbose_name
        db_table = 'qrcodelinkpaytype'

class Qrcode(models.Model):

    id=models.BigAutoField(primary_key=True)
    path = models.CharField(max_length=255,verbose_name='二维码路径',default="")
    name = models.CharField(max_length=60,verbose_name='二维码所对应的微信昵称')
    groupcode = models.IntegerField(verbose_name="分组序号")
    orderno = models.IntegerField(verbose_name="序号")
    status = models.CharField(max_length=1,verbose_name="状态,0-启用，1-不启用,2-失效,3-禁用,4-删除,5-退出")
    usecount = models.IntegerField(verbose_name="使用次数",default=0)
    url = models.CharField(max_length=255,verbose_name="二维码链接",default="")
    createtime = models.BigIntegerField(default=0)

    updtime = models.BigIntegerField(default=0)

    userid = models.BigIntegerField(default=0,verbose_name="码商")

    wechathelper_id = models.BigIntegerField(default=0,verbose_name="店员助手ID")

    type = models.CharField(max_length=5,default='QR001' ,
                            verbose_name="""二维码类型 QR001-微信个人二维码,
                                         QR005-付临门聚合支付码""")

    statusname = None

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(Qrcode, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '二维码表'
        verbose_name_plural = verbose_name
        db_table = 'qrcode'

class QrcodeUseList(models.Model):


    id=models.BigAutoField(primary_key=True)
    qrcode = models.BigIntegerField(verbose_name="二维码ID")
    path = models.CharField(max_length=255,verbose_name='二维码路径',default="")
    name = models.CharField(max_length=60,verbose_name='二维码所对应的微信昵称')
    groupcode = models.IntegerField(verbose_name="分组序号")
    orderno = models.IntegerField(verbose_name="序号")
    status = models.CharField(max_length=1,verbose_name="状态,0-成功使用，1-使用中,2-失败")
    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(QrcodeUseList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '二维码使用明细表'
        verbose_name_plural = verbose_name
        db_table = 'qrcodeuselist'



class SysNumber(models.Model):

    id=models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=5,default='QR001' ,
                            verbose_name="""二维码类型 QR001-微信个人二维码,
                                         QR005-付临门聚合支付码""")
    last_qrcode = models.IntegerField()

    class Meta:
        verbose_name = '二维码轮询表'
        verbose_name_plural = verbose_name
        db_table = 'sysnumber'

