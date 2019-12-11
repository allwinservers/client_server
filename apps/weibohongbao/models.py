
import time
from django.db import models
from django.utils import timezone

class WeiboGroup(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name="id")
    group_id = models.CharField(max_length=30,verbose_name="群组ID")
    userid = models.IntegerField(default=0)
    name = models.CharField(max_length=60,verbose_name="群名称")
    uid = models.CharField(max_length=20,verbose_name="群组长微博id")

    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(WeiboGroup, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '群组'
        verbose_name_plural = verbose_name
        db_table = 'wbgroup'

class WeiboGroupMember(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name="id")
    group_id = models.CharField(max_length=30,verbose_name="群组ID")
    name = models.CharField(max_length=60,verbose_name="群名称")
    userid = models.IntegerField(default=0)
    uid = models.CharField(max_length=20,verbose_name="群组长微博id")
    son_uid = models.CharField(max_length=20,verbose_name="群成员微博id")

    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(WeiboGroupMember, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '群成员'
        verbose_name_plural = verbose_name
        db_table = 'wbgroupmember'

class WeiboUser(models.Model):

    """
    微博用户表
    """

    id=models.BigAutoField(primary_key=True,verbose_name="id")
    uid = models.CharField(max_length=20, verbose_name="微博UID")
    username = models.CharField(max_length=60,verbose_name="账号",default='')
    password = models.CharField(max_length=60, verbose_name="密码",default='')

    userid=models.IntegerField(default=0,verbose_name="码商ID")

    session = models.TextField(verbose_name="会话信息",default='')
    type = models.CharField(max_length=1,verbose_name="类型,0-发送的,1-抢红包的",default='1')
    status = models.CharField(max_length=1,verbose_name="是否开启,0-开启,1-暂用",default='1')
    session_status = models.CharField(max_length=1,verbose_name="会话状态,0-存活,1-失效",default="1")

    logintime = models.BigIntegerField(default=0)
    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(WeiboUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '微博用户表'
        verbose_name_plural = verbose_name
        db_table = 'wbuser'

class WeiboSendList(models.Model):
    """
    微博发红包明细
    """

    id = models.BigAutoField(primary_key=True, verbose_name="id")
    userid = models.IntegerField(default=0)
    groupid = models.CharField(max_length=20,verbose_name="群ID",default="")
    setid = models.CharField(max_length=60,verbose_name="群组红包ID",default="")
    uid = models.CharField(max_length=20, verbose_name="微博UID",default="")
    uids = models.CharField(max_length=2048, verbose_name="抢红包人的ID集合",default="")
    status = models.CharField(max_length=1,verbose_name="状态,0-已抢完,1-正在抢",default='1')
    taskid = models.IntegerField(verbose_name="任务ID")

    url = models.CharField(max_length=512,verbose_name="红包链接,用于抢红包用",default="")
    hburl = models.CharField(max_length=512,verbose_name="红包明细链接",default="")
    referer = models.CharField(max_length=1024,verbose_name="",default="")

    getcount = models.IntegerField(default=0,verbose_name="抢红包数量")
    sendcount = models.IntegerField(default=0,verbose_name="发红包数量")

    amount = models.DecimalField(max_digits=18,decimal_places=6,verbose_name="金额",default=0.0)

    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(WeiboSendList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '微博发红包明细'
        verbose_name_plural = verbose_name
        db_table = 'wbsendlist'


class WeiboParams(models.Model):

    """
    微博参数表
    """

    id=models.AutoField(primary_key=True,verbose_name="id")

    nameid = models.IntegerField(default=0)


    class Meta:
        verbose_name = '微博参数表'
        verbose_name_plural = verbose_name
        db_table = 'wbparams'


class WeiboTask(models.Model):
    """
    计划任务表
    """

    taskid = models.AutoField(primary_key=True, verbose_name="任务ID")

    taskname = models.CharField(verbose_name="名称",max_length=60,default="")
    userid = models.IntegerField(verbose_name="码商ID")
    minamount = models.DecimalField(max_digits=18,decimal_places=6,verbose_name="最小金额")
    maxamount = models.DecimalField(max_digits=18,decimal_places=6,verbose_name="最大金额")
    amountwhat = models.DecimalField(max_digits=18,decimal_places=6,verbose_name="一个账号跑多少")

    robnumber = models.IntegerField(verbose_name="抢红包人数,必须是5的倍数",default=0)
    groupid = models.CharField(max_length=30,verbose_name="群组ID")
    uid = models.CharField(max_length=30,verbose_name="发红包UID")

    date = models.CharField(max_length=10,verbose_name="日期")
    sort = models.IntegerField(verbose_name="执行顺序",default=0)

    progree = models.IntegerField(verbose_name="进度",default=0)

    umark = models.CharField(max_length=1,verbose_name="开启:0-开启,1-未开启",default="1")
    status = models.CharField(max_length=1,verbose_name="状态:0-已完成,1-待完成,2-放弃",default="1")

    createtime = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.createtime:
            self.createtime = time.mktime(timezone.now().timetuple())
        return super(WeiboTask, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '微博任务表'
        verbose_name_plural = verbose_name
        db_table = 'wbtask'