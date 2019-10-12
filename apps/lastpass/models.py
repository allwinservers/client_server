from django.db import models



class JdBusiList(models.Model):


    id =models.AutoField(primary_key=True,verbose_name="id")
    busi_id=models.BigIntegerField(verbose_name="门店ID")
    maxnum = models.IntegerField(verbose_name="最多笔数")
    maxamount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="最多限额")
    num = models.IntegerField(verbose_name="实际笔数")
    amount = models.DecimalField(max_digits=18,decimal_places=6,default=0.000,verbose_name="实际金额")
    status = models.CharField(max_length=1,verbose_name='0-正常,1-删除',default='0')



    class Meta:
        verbose_name = '京东小额店铺表'
        verbose_name_plural = verbose_name
        db_table = 'jdbusilist'