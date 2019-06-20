import time
from django.db import models
from django.utils import timezone

# Create your models here.

class Order(models.Model):

    ordercode = models.BigAutoField(primary_key=True,verbose_name="订单ID")
    userid = models.BigIntegerField(verbose_name="商户号",default=0)
    down_ordercode = models.CharField(verbose_name='下游订单号',default='',max_length=60)
    paypass = models.IntegerField(verbose_name="支付渠道",default=0)
    paypassname = models.CharField(verbose_name="支付渠道名称",default="",max_length=60)

    paytype = models.IntegerField(verbose_name="支付方式",default=0)
    paytypename = models.CharField(verbose_name="支付方式名称",default="",max_length=60)

    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="订单金额")
    confirm_amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="收款金额")

    tech_cost = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="技术费")

    myfee = models.DecimalField(max_digits=18, decimal_places=6, default=0.000, verbose_name="抛开码商成本费用")
    codefee = models.DecimalField(max_digits=18, decimal_places=6, default=0.000, verbose_name="码商费用")
    agentfee = models.DecimalField(max_digits=18, decimal_places=6, default=0.000, verbose_name="代理费用")

    status = models.CharField(max_length=1,verbose_name="支付状态 : 0-支付成功,1-等待支付,2-支付失败,3-订单过期")

    down_status = models.CharField(max_length=1,verbose_name="支付状态 : 0-支付成功,1-等待支付,2-回调失败,3-订单过期",default='1')

    ismobile = models.CharField(max_length=1,verbose_name="是否手机,0-手机,1-pc",default='0')

    client_ip = models.CharField(max_length=60,verbose_name="客户端IP",default='')
    notifyurl = models.CharField(max_length=255,verbose_name="异步通知URL",default='')

    createtime = models.BigIntegerField(default=0)

    pay_time = models.BigIntegerField(default=0)

    qr_id = models.BigIntegerField(default=0,verbose_name="二维码ID")

    qr_type = models.CharField(max_length=5,default='QR001' ,
                            verbose_name="""二维码类型 QR001-微信个人二维码,
                                         QR005-付临门聚合支付码""")

    keep_info = models.TextField(verbose_name="请求的信息保存下来，回调时带回去",default='')

    lock = models.CharField(verbose_name="是否加密,0-加密,1-不加密",default="0",max_length=1)


    def save(self, *args, **kwargs):
        t= time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(Order, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '订单表'
        verbose_name_plural = verbose_name
        db_table = 'order'


class CashoutList(models.Model):

    id = models.BigAutoField(primary_key=True)

    userid = models.BigIntegerField(verbose_name="用户ID", default=0)
    name = models.CharField(max_length=120, verbose_name="名称", default='', null=True)

    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="申请金额")

    bank_name = models.CharField(max_length=60,verbose_name="银行名称",default='')
    open_name = models.CharField(max_length=60,verbose_name="开户人",default='')
    open_bank = models.CharField(max_length=250,verbose_name="支行",default='')
    bank_card_number = models.CharField(max_length=60,verbose_name="银行卡号",default='')

    status = models.CharField(max_length=1,verbose_name="提现状态,0-提现申请中,1-提现通过,2-提现拒绝")

    createtime = models.BigIntegerField(default=0)

    updtime  = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t = time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(CashoutList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '交易明细表'
        verbose_name_plural = verbose_name
        db_table = 'cashout_list'


class UpCashoutList(models.Model):

    id = models.BigAutoField(primary_key=True)

    userid = models.BigIntegerField(verbose_name="用户ID", default=0)
    name = models.CharField(max_length=120, verbose_name="名称", default='', null=True)

    userid_to = models.BigIntegerField(verbose_name="码商iD", default=0)
    name_to = models.CharField(max_length=120, verbose_name="码商名称", default='', null=True)

    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="申请金额")

    bank_name = models.CharField(max_length=60,verbose_name="银行名称",default='')
    open_name = models.CharField(max_length=60,verbose_name="开户人",default='')
    open_bank = models.CharField(max_length=250,verbose_name="支行",default='')
    bank_card_number = models.CharField(max_length=60,verbose_name="银行卡号",default='')

    status = models.CharField(max_length=1,verbose_name="提现状态,0-提现申请中,1-提现通过,2-提现拒绝")

    createtime = models.BigIntegerField(default=0)

    updtime  = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        t = time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(UpCashoutList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '交易明细表'
        verbose_name_plural = verbose_name
        db_table = 'upcashout_list'

