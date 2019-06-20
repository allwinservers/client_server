import binascii
import os
import time
from django.db import models
from django.utils import timezone

from libs.utils.string_extension import md5pass

class Token(models.Model):

    key = models.CharField(max_length=160, primary_key=True)
    userid  = models.BigIntegerField()
    ip = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = verbose_name
        db_table="user_token"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(80)).decode()

    def __str__(self):
        return self.key

class Login(models.Model):

    userid=models.BigIntegerField()
    createtime=models.BigIntegerField(default=0)
    ip = models.CharField(max_length=255,default='')
    user_agent = models.CharField(max_length=255,default='')


    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(Login, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '用户登录表'
        verbose_name_plural = verbose_name
        db_table = 'login'

class Users(models.Model):

    userid=models.BigAutoField(primary_key=True)
    rolecode=models.CharField(max_length=4,default='')
    name=models.CharField(max_length=120,verbose_name="名称",default='',null=True)
    loginname=models.CharField(max_length=60,verbose_name="登录名称",default='',null=True)
    passwd=models.CharField(max_length=60,verbose_name='密码',default='')
    pay_passwd=models.CharField(max_length=60,verbose_name='支付密码',default='')
    pic=models.CharField(max_length=255,verbose_name="头像",default='')
    createtime=models.BigIntegerField(default=0)
    createman = models.BigIntegerField(default=0)
    createman_name = models.CharField(max_length=120,default='')
    status = models.IntegerField(default='0',verbose_name="状态:0-正常,1-删除,2-冻结",null=True)

    email  = models.CharField(max_length=60,verbose_name="邮箱",default="")
    concat = models.CharField(max_length=60,verbose_name='联系人',default="")
    mobile = models.CharField(max_length=20,verbose_name="手机号",default="")
    contype = models.CharField(max_length=60,verbose_name="联系方式",default="")

    paypassid =  models.BigIntegerField(verbose_name="上游支付渠道ID",default=0)

    bal = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="余额")
    cashout_bal = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="提现金额")

    up_bal = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="码商流水")

    google_token = models.CharField(max_length=60,verbose_name="google_token",default="")


    rolename  = None
    level = None
    name_to = None
    userid_to = None
    agents = None

    lastlogintime = None

    paypassname = None

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())

        if not self.createtime:
            self.createtime = t
        if not self.passwd :
            self.passwd = md5pass('123456')
        if not self.pay_passwd:
            self.pay_passwd = md5pass('123456')
        return super(Users, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        db_table = 'user'

class UserLink(models.Model):

    id = models.BigAutoField(primary_key=True)
    userid = models.BigIntegerField(verbose_name="下线用户ID")
    userid_to =  models.BigIntegerField(verbose_name="上线用户ID")
    level = models.IntegerField(verbose_name="代理级别,1-一级代理,2-二级代理")
    rate  = models.DecimalField(max_digits=18,decimal_places=6,default=0.000)
    createtime = models.BigIntegerField()

    name_to = None

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(UserLink, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '代理关系表'
        verbose_name_plural = verbose_name
        db_table = 'userlink'


class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    rolecode =  models.CharField(max_length=4,default='')
    name = models.CharField(max_length=60,default='')
    type = models.CharField(max_length=1,default='0',verbose_name="0-管理员,1-商户,2-代理,3-微信码商")

    """
    1000 - 系统管理员
    1001 - 普通管理员 
    2001 - 商户
    3001 - 代理
    4001 - 微信码商
    """

    class Meta:
        verbose_name = '角色表'
        verbose_name_plural = verbose_name
        db_table = 'role'

class BalList(models.Model):
    id = models.BigAutoField(primary_key=True)
    userid =  models.BigIntegerField(default=0,verbose_name="用户ID")
    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="交易金额")
    bal = models.DecimalField(max_digits=18, decimal_places=6, default=0.000, verbose_name="交易前金额")
    confirm_bal = models.DecimalField(max_digits=18, decimal_places=6, default=0.000, verbose_name="交易后金额")
    memo = models.CharField(max_length=255,verbose_name="交易摘要")
    ordercode = models.BigIntegerField(default=0,verbose_name="订单号")
    memo1 = models.CharField(max_length=255, verbose_name="交易摘要",default="1")

    createtime = models.BigIntegerField()

    name = None

    def save(self, *args, **kwargs):
        t=time.mktime(timezone.now().timetuple())
        if not self.createtime:
            self.createtime = t
        return super(BalList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '角色表'
        verbose_name_plural = verbose_name
        db_table = 'ballist'
