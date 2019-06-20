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
    paycode = models.CharField(max_length=20 ,verbose_name="渠道编号")
    name = models.CharField(max_length=60,verbose_name="渠道名称",default='')
    passcode = models.CharField(max_length=30,verbose_name="渠道商户号",default='')
    rate = models.DecimalField(max_digits=18,decimal_places=6,default=0.001)
    alipay  = models.CharField(max_length=1,verbose_name="0-支持,1-不支持  支付宝",default=1)
    wechat = models.CharField(max_length=1,verbose_name="0-支持,1-不支持   微信",default=1)
    ebank = models.CharField(max_length=1,verbose_name="0-支持,1-不支持    网银",default=1)
    mobilet = models.CharField(max_length=1,verbose_name="0-支持,1-不支持  移动端",default=1)
    status = models.CharField(max_length=1,verbose_name="使用状态 0-启用,1-不启用,2-删除",default=1)
    concat = models.CharField(max_length=30,verbose_name="联系人",default="")
    contype = models.CharField(max_length=30,verbose_name="联系方式",default="")
    createtime = models.BigIntegerField(default=0)
    bal = models.DecimalField(max_digits=18,decimal_places=6,default=0.00)

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
    createtime = models.BigIntegerField(default=0)

    passid = models.BigIntegerField(default=0)

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