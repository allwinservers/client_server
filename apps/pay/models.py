import binascii
import os
import time
from django.db import models
from django.utils import timezone
from utils.exceptions import PubErrorCustom

# Create your models here.

class PayType(models.Model):

    paytypeid=models.BigAutoField(primary_key=True,verbose_name="支付方式ID")
    name = models.CharField(max_length=30,verbose_name="支付方式名称",default="")
    type = models.CharField(max_length=1,verbose_name="0-支付宝,1-微信,2-银联",default="0")
    typename = models.CharField(max_length=30,verbose_name="大类名称",default="")
    createtime = models.BigIntegerField(default=0)

    rate=None
    userid=None
    passid=None

    paypassname = None

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())

        from include.data.choices_list import Choices_to_Dict
        self.typename = Choices_to_Dict('paytype')[self.type]

        return super(PayType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '支付方式表'
        verbose_name_plural = verbose_name
        db_table = 'paytype'

class PayPass(models.Model):

    paypassid=models.BigAutoField(primary_key=True,verbose_name="渠道ID")
    name = models.CharField(max_length=60,verbose_name="渠道名称",default='')
    status = models.CharField(max_length=1, verbose_name="使用状态 0-启用,1-不启用,2-删除", default=1)
    concat = models.CharField(max_length=30,verbose_name="联系人",default="")
    contype = models.CharField(max_length=30,verbose_name="联系方式",default="")
    isdayfu = models.CharField(max_length=1,verbose_name="是否代付,0-是,1-不是",default='1')

    bal = models.DecimalField(max_digits=18,decimal_places=6,default=0.00,verbose_name="余额")
    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.00,verbose_name="流水")

    custom = models.CharField(max_length=1,verbose_name="0-走自定义方式,1-走规则(rules)",default="0")
    rules = models.TextField(default="",verbose_name="接入规则",null=True,blank=True)
    callback_ip =  models.CharField(max_length=512,verbose_name="回调IP",default="",null=True,blank=True)
    createtime = models.BigIntegerField(default=0)

    pays=None
    paytypes=None
    status_name=None

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(PayPass, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '支付渠道表'
        verbose_name_plural = verbose_name
        db_table = 'paypass'


class PayPassLinkType(models.Model):
    linkid=models.BigAutoField(primary_key=True,verbose_name="关联ID")
    paytypeid=models.IntegerField(default=0)
    to_id=models.IntegerField(default=0)
    type = models.CharField(max_length=1,verbose_name="类型:0-上游,1-下游,2-码商",default='0')
    rate = models.DecimalField(max_digits=18,decimal_places=6,default=0.000)
    passid = models.BigIntegerField(default=0)
    createtime = models.BigIntegerField(default=0)
    userid = models.BigIntegerField(default=0,null=True)

    paypassname = None
    paytypename = None
    typename = None

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(PayPassLinkType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '支付渠道方式关联表'
        verbose_name_plural = verbose_name
        db_table = 'paypasslinktype'


class BankInfo(models.Model):
    id=models.BigAutoField(primary_key=True)

    userid=models.BigIntegerField()
    bank_name = models.CharField(max_length=60, verbose_name="银行名称", default='')
    open_name = models.CharField(max_length=60, verbose_name="开户人", default='')
    open_bank = models.CharField(max_length=250, verbose_name="支行", default='')
    bank_card_number = models.CharField(max_length=60, verbose_name="银行卡号", default='')
    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(BankInfo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '银行卡信息'
        verbose_name_plural = verbose_name
        db_table = 'bankinfo'


# class WeiboPayUsername(models.Model):
#
#     id=models.BigAutoField(primary_key=True,verbose_name="关联ID")
#     userid=models.IntegerField(default=0,verbose_name="码商ID")
#     username = models.CharField(max_length=60,verbose_name="账号",default='')
#     password = models.CharField(max_length=60, verbose_name="密码",default='')
#     session = models.TextField(verbose_name="会话信息",default='')
#     type = models.CharField(max_length=1,verbose_name="类型,0-发送的,1-抢红包的",default='0')
#
#     status = models.CharField(max_length=1,verbose_name="是否开启,0-开启,1-暂用",default='1')
#
#     createtime = models.BigIntegerField(default=0)
#     logintime = models.BigIntegerField(default=0,verbose_name="微博登录时间")
#
#     def save(self, *args, **kwargs):
#         if not self.createtime:
#             self.createtime = time.mktime(timezone.now().timetuple())
#         return super(WeiboPayUsername, self).save(*args, **kwargs)
#
#     class Meta:
#         verbose_name = '红包账号表'
#         verbose_name_plural = verbose_name
#         db_table = 'webpayusername'