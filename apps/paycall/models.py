import time
from django.db import models
from django.utils import timezone


class PayCallList(models.Model):

    id=models.BigAutoField(primary_key=True)
    qr_id = models.BigIntegerField(default=0,verbose_name="二维码ID")
    name = models.CharField(max_length=60,verbose_name="微信昵称",default="")
    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000)
    orderid = models.BigIntegerField()
    status = models.CharField(max_length=1,verbose_name="状态0-成功,1-失败")

    memo = models.CharField(max_length=1024,verbose_name="备注")

    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())

        return super(PayCallList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '扫码明细'
        verbose_name_plural = verbose_name
        db_table = 'paycalllist'


class FlmTranList(models.Model):

    id = models.BigAutoField(primary_key=True)
    userid = models.BigIntegerField(default=0,verbose_name="码商用户ID")
    name = models.CharField(max_length=60,default='',verbose_name="码商名字,取付临门平台登录账号")
    ordercode = models.CharField(max_length=60,default='付临门订单号')
    remark = models.CharField(max_length=60,default='',verbose_name="交易时间")
    status = models.CharField(max_length=60,default='' ,verbose_name="交易状态")
    amount = models.DecimalField(max_digits=18, decimal_places=6, default=0.000,verbose_name="交易金额")
    paytype = models.CharField(max_length=60,default='',verbose_name="交易类型    比如微信扫码")
    createtime = models.BigIntegerField(default=0)

    orderid = models.BigIntegerField(verbose_name="订单号",default=0)
    umark = models.CharField(max_length=1,verbose_name="处理状态 0-成功,1-待处理")

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(FlmTranList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '付临门'
        verbose_name_plural = verbose_name
        db_table = 'flmtranlist'

